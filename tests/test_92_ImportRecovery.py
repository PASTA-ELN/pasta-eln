"""Regression tests for import validation and reporting."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pasta_eln.backend_worker.input_output import importELN


class _ImportDatabase:
  def getDoc(self, docID: str) -> dict[str, str]:
    return {'id': docID}


class _ImportBackend:
  def __init__(self, basePath: Path, failAdd: bool=False):
    self.basePath = basePath
    self.cwd: Path | None = basePath
    self.hierStack: list[str] = []
    self.db = _ImportDatabase()
    self._count = 0
    self._failAdd = failAdd

  def changeHierarchy(self, docID: str | None) -> None:
    if docID is None:
      self.cwd = self.cwd.parent if self.cwd is not None else self.basePath
      self.hierStack.pop()
    elif docID == 'project':
      self.cwd = self.basePath
      self.hierStack = [docID]
    else:
      self.cwd = self.cwd / docID
      self.cwd.mkdir()
      self.hierStack.append(docID)

  def addData(self, docType: str, doc: dict) -> dict[str, str]:
    if self._failAdd:
      raise RuntimeError('database write failed')
    self._count += 1
    return {'id': f"x-{self._count}" if docType.startswith('x') else f"d-{self._count}"}


class TestImportRecovery(unittest.TestCase):
  def _writeArchive(self, path: Path, graph: list[dict], files: dict[str, str] | None=None) -> None:
    with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
      archive.writestr('crate/ro-crate-metadata.json', json.dumps({'@graph': graph}))
      for fileName, content in (files or {}).items():
        archive.writestr(f'crate/{fileName}', content)

  def test_invalid_metadata_does_not_change_destination(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
      archivePath = Path(directory) / 'invalid.eln'
      self._writeArchive(archivePath, [{'@id': './', '@type': 'Dataset'}])
      backend = _ImportBackend(Path(directory))

      report, statistics = importELN(backend, str(archivePath), 'project')

      self.assertIn('RO-Crate metadata node is missing', report)
      self.assertEqual(statistics, {})
      self.assertEqual(backend._count, 0)

  def test_missing_embedded_file_is_reported(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
      archivePath = Path(directory) / 'partial.eln'
      graph = [
          {'@id': 'ro-crate-metadata.json', '@type': 'CreativeWork'},
          {'@id': './', '@type': 'Dataset', 'hasPart': [{'@id': './folder'}]},
          {'@id': './folder', '@type': 'Dataset', 'name': 'folder',
           'hasPart': [{'@id': './folder/missing.txt'}]},
          {'@id': './folder/missing.txt', '@type': 'File', 'name': 'missing.txt'},
      ]
      self._writeArchive(archivePath, graph)
      backend = _ImportBackend(Path(directory))

      report, statistics = importELN(backend, str(archivePath), 'project')

      self.assertTrue(report.startswith('Partial success'))
      self.assertEqual(len(statistics['errors']), 1)
      self.assertIn('missing from the archive', statistics['errors'][0])

  def test_database_failure_is_reported_and_removes_copied_file(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
      archivePath = Path(directory) / 'database-failure.eln'
      graph = [
          {'@id': 'ro-crate-metadata.json', '@type': 'CreativeWork'},
          {'@id': './', '@type': 'Dataset', 'hasPart': [{'@id': './document.txt'}]},
          {'@id': './document.txt', '@type': 'File', 'name': 'document.txt'},
      ]
      self._writeArchive(archivePath, graph, {'document.txt': 'test content'})
      backend = _ImportBackend(Path(directory), failAdd=True)

      report, statistics = importELN(backend, str(archivePath), 'project')

      self.assertTrue(report.startswith('Partial success'))
      self.assertIn('database write failed', statistics['errors'][0])
      self.assertFalse((Path(directory) / 'document.txt').exists())
