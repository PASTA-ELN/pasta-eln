#!/usr/bin/python3
"""Tests for extractor timeout handling and parallel scan extraction."""
import hashlib
import json
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

from pasta_eln.backend_worker.backend import Backend
from pasta_eln.backend_worker.extractor import isPastaExport, saveFigure
from pasta_eln.backend_worker.sqlite import SqlLiteDB
from pasta_eln.configuration_file import CONFIGURATION_FILE_NAME


class TestExtractorTimeoutParallel(unittest.TestCase):
  """Timeout and parallel extractor behavior."""

  def setUp(self):
    self.tempDir = tempfile.TemporaryDirectory()
    self.homePatch = patch('pathlib.Path.home', return_value=Path(self.tempDir.name))
    self.homePatch.start()
    self.basePath = Path(self.tempDir.name)/'data'
    self.addOnPath = Path(self.tempDir.name)/'addons'
    self.basePath.mkdir()
    self.addOnPath.mkdir()
    self.configuration = {
        'defaultProjectGroup': 'research',
        'projectGroups': {
            'research': {
                'local': {'database': 'research', 'path': str(self.basePath)},
                'remote': {},
                'addOnDir': str(self.addOnPath),
                'addOns': {'project': {}, 'extractors': {}, 'table': {}}
            }
        },
        'version': 4,
        'userID': 'test_user',
        'GUI': {'maxExtractionDuration': '1 sec'}
    }
    self._writeConfiguration()
    self.backend = Backend('research')


  def tearDown(self):
    self.backend.exit()
    self.homePatch.stop()
    self.tempDir.cleanup()


  def _writeConfiguration(self) -> None:
    with open(Path(self.tempDir.name)/CONFIGURATION_FILE_NAME, 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.configuration))


  def _writeExtractor(self, sleepSeconds:float) -> None:
    (self.addOnPath/'extractor_slow.py').write_text(
        'import time\n'
        'def use(filePath, style={\'main\':\'\'}, saveFileName=None):\n'
        f'  time.sleep({sleepSeconds})\n'
        '  return {\'style\': {\'main\': \'measurement/slow\'}, '
        '\'metaVendor\': {}, \'metaUser\': {\'done\': True}}\n',
        encoding='utf-8')


  def _writeInvalidMetadataExtractor(self) -> None:
    (self.addOnPath/'extractor_slow.py').write_text(
        'def use(filePath, style={\'main\':\'\'}, saveFileName=None):\n'
        '  return {\'style\': {\'main\': \'measurement/slow\'}, '
        '\'metaVendor\': \'not metadata\', \'metaUser\': {}}\n',
        encoding='utf-8')


  def _writeV2Extractor(self, value:str='first') -> None:
    (self.addOnPath/'extractor_v2.py').write_text(
        'from PIL import Image\n'
        'PASTA_ELN_EXTRACTOR_API = 2\n'
        'def use(filePath, style, saveFigure):\n'
        '  saveFigure(Image.new("RGB", (2, 2), "white"))\n'
        f'  return {{"style": {{"main": "measurement/v2"}}, "metaVendor": {{}}, "metaUser": {{"value": "{value}"}}}}\n',
        encoding='utf-8')


  def test_export_metadata_is_detected_for_all_formats(self):
    for suffix in ('png', 'jpg'):
      exportPath = self.basePath/f'figure.{suffix}'
      saveFigure(exportPath, 'data-hash', 'extractor-hash', Image.new('RGB', (2, 2), 'white'))
      self.assertTrue(isPastaExport(exportPath))

    exportPath = self.basePath/'figure.svg'
    import matplotlib.pyplot as plt
    plt.plot([1, 2])
    saveFigure(exportPath, 'data-hash', 'extractor-hash')
    self.assertTrue(isPastaExport(exportPath))

    project = self.backend.addData('x0', {'name':'Export scan'})
    scannedExport = self.basePath/project['branch'][0]['path']/'marked.png'
    saveFigure(scannedExport, 'data-hash', 'extractor-hash', Image.new('RGB', (2, 2), 'white'))
    self.backend.scanProject(None, project['id'])
    paths = [item['key'] for item in self.backend.db.getView('viewHierarchy/viewPathsAll')]
    self.assertNotIn(scannedExport.relative_to(self.basePath).as_posix(), paths)


  def test_v2_extractor_stores_hashes_and_replaces_extractor_hash(self):
    self._writeV2Extractor()
    self.configuration['GUI']['maxExtractionDuration'] = '5 sec'
    self._writeConfiguration()
    self.backend.exit()
    self.backend = Backend('research')
    dataPath = self.basePath/'data.v2'
    dataPath.write_text('source data', encoding='utf-8')
    doc = self.backend.addData('', {'name':'data.v2'})
    firstHash = doc['extractorHash']
    self.assertEqual(doc['dataHash'], hashlib.sha256(dataPath.read_bytes()).hexdigest())

    self._writeV2Extractor('second')
    self.backend.extractors.use(dataPath, doc['dataHash'], doc)
    self.assertNotEqual(doc['extractorHash'], firstHash)


  def test_legacy_database_migrates_to_sha256_data_hash(self):
    migrationBase = Path(self.tempDir.name)/'migration'
    migrationBase.mkdir()
    source = migrationBase/'legacy.dat'
    source.write_text('legacy source', encoding='utf-8')
    connection = sqlite3.connect(migrationBase/'pastaELN.db')
    connection.execute('CREATE TABLE main (id TEXT PRIMARY KEY, name TEXT, user TEXT, type TEXT, dateCreated TEXT, '
                       'dateModified TEXT, gui TEXT, client TEXT, shasum TEXT, image TEXT, content TEXT, comment TEXT, '
                       'externalId TEXT, dateSync TEXT)')
    connection.execute("INSERT INTO main VALUES ('m1', 'legacy.dat', '', 'measurement', '', '', 'T', '', 'old', '', '', '', '', '')")
    connection.execute('CREATE TABLE branches (id TEXT, idx INTEGER, stack TEXT, child TEXT, path TEXT, show TEXT, PRIMARY KEY (id, idx))')
    connection.execute("INSERT INTO branches VALUES ('m1', 0, '', '0', 'legacy.dat', 'T')")
    connection.commit()
    connection.close()

    with patch.dict('os.environ', {'PASTA_ELN_ALLOW_DATAHASH_MIGRATION':'0'}):
      with self.assertRaisesRegex(RuntimeError, 'not safe for productive use'):
        SqlLiteDB(basePath=migrationBase)
    self.assertFalse(list(migrationBase.glob('*.pre-dataHash-migration-*.bak')))

    database = SqlLiteDB(basePath=migrationBase)
    self.assertEqual(database.cursor.execute('PRAGMA user_version').fetchone()[0], 1)
    self.assertEqual(database.getDoc('m1')['dataHash'], hashlib.sha256(source.read_bytes()).hexdigest())
    columns = [row[1] for row in database.cursor.execute('PRAGMA table_info(main)')]
    self.assertNotIn('shasum', columns)
    self.assertIn('extractorHash', columns)
    self.assertTrue(list(migrationBase.glob('*.pre-dataHash-migration-*.bak')))
    database.exit()


  def test_newer_database_version_is_not_opened(self):
    futureBase = Path(self.tempDir.name)/'future'
    futureBase.mkdir()
    connection = sqlite3.connect(futureBase/'pastaELN.db')
    connection.execute('PRAGMA user_version=2')
    connection.commit()
    connection.close()

    with self.assertRaisesRegex(ValueError, 'cannot be migrated'):
      SqlLiteDB(basePath=futureBase)
    with sqlite3.connect(futureBase/'pastaELN.db') as connection:
      self.assertEqual(connection.execute(
          "SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0], 0)


  def test_extractor_test_reports_invalid_metadata_type(self):
    self._writeInvalidMetadataExtractor()
    dataPath = self.basePath/'data.slow'
    dataPath.write_text('slow data', encoding='utf-8')

    report, _ = self.backend.extractors.test(dataPath)

    self.assertIn('metaVendor must be a dictionary not str.', report)


  def test_extractor_timeout_marks_document_stopped(self):
    self._writeExtractor(5)
    dataPath = self.basePath/'data.slow'
    dataPath.write_text('slow data', encoding='utf-8')

    start = time.monotonic()
    doc = self.backend.addData('', {'name':'data.slow'})
    duration = time.monotonic()-start

    self.assertLess(duration, 3)
    self.assertEqual(doc['metaUser']['extractorStatus'], 'stopped')
    self.assertEqual(doc['metaUser']['extractorError'], 'Extractor stopped after 1 seconds.')
    self.assertIn('dataHash', doc)


  def test_scan_extractors_run_in_parallel(self):
    self._writeExtractor(0.8)
    self.configuration['GUI']['maxExtractionDuration'] = '5 sec'
    self._writeConfiguration()
    self.backend.exit()
    self.backend = Backend('research')
    project = self.backend.addData('x0', {'name':'Parallel Scan'})
    projectPath = self.basePath/project['branch'][0]['path']
    for idx in range(4):
      (projectPath/f'data_{idx}.slow').write_text(f'slow data {idx}', encoding='utf-8')

    start = time.monotonic()
    self.backend.scanProject(None, project['id'])
    duration = time.monotonic()-start

    self.assertLess(duration, 3.4)
    docs = self.backend.db.getView('viewDocType/measurement')
    self.assertGreaterEqual(len(docs), 4)


if __name__ == '__main__':
  unittest.main()
