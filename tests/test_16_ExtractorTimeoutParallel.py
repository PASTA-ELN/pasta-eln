#!/usr/bin/python3
"""Tests for extractor timeout handling and parallel scan extraction."""
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from pasta_eln.backend_worker.backend import Backend
from pasta_eln.fixed_strings_json import confFileName


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
        'version': 3,
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
    with open(Path(self.tempDir.name)/confFileName, 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.configuration))


  def _writeExtractor(self, sleepSeconds:float) -> None:
    (self.addOnPath/'extractor_slow.py').write_text(
        'import time\n'
        'def use(filePath, style={\'main\':\'\'}, saveFileName=None):\n'
        f'  time.sleep({sleepSeconds})\n'
        '  return {\'style\': {\'main\': \'measurement/slow\'}, '
        '\'metaVendor\': {}, \'metaUser\': {\'done\': True}}\n',
        encoding='utf-8')


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
    self.assertIn('shasum', doc)


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
