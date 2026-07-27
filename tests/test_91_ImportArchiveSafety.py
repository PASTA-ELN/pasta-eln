"""Tests for resource limits on imported ELN archives."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

from pasta_eln.backend_worker.input_output import _checkImportArchive


class TestImportArchiveSafety(unittest.TestCase):
  """Archive preflight checks reject inputs that exceed resource limits."""

  def _createArchive(self, names:list[str], content:bytes=b'x') -> Path:
    tempFile = tempfile.NamedTemporaryFile(suffix='.eln', delete=False)
    tempFile.close()
    archivePath = Path(tempFile.name)
    with ZipFile(archivePath, 'w', compression=ZIP_DEFLATED) as archive:
      for name in names:
        archive.writestr(name, content)
    return archivePath

  def test_rejects_too_many_members(self):
    archivePath = self._createArchive(['one', 'two', 'three'])
    self.addCleanup(archivePath.unlink)
    with ZipFile(archivePath) as archive, \
         patch('pasta_eln.backend_worker.input_output.MAX_IMPORT_ARCHIVE_MEMBERS', 2):
      error = _checkImportArchive(archive)
    self.assertEqual(error, 'ERROR: eln file contains more than 2 archive members. Cannot process')

  def test_rejects_excessive_uncompressed_data(self):
    archivePath = self._createArchive(['content'], b'abc')
    self.addCleanup(archivePath.unlink)
    with ZipFile(archivePath) as archive, \
         patch('pasta_eln.backend_worker.input_output.MAX_IMPORT_ARCHIVE_BYTES', 2):
      error = _checkImportArchive(archive)
    self.assertEqual(error, 'ERROR: eln file expands beyond 2 bytes. Cannot process')


if __name__ == '__main__':
  unittest.main()
