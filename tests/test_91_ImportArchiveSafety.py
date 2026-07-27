"""Tests for resource limits on imported ELN archives."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
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
    archivePath = self._createArchive(['one'])
    self.addCleanup(archivePath.unlink)
    with ZipFile(archivePath) as archive, \
         patch.object(archive, 'infolist', return_value=[Mock(file_size=0)]*10_001):
      error = _checkImportArchive(archive)
    self.assertEqual(error, 'ERROR: eln file contains more than 10000 archive members. Cannot process')

  def test_rejects_excessive_uncompressed_data(self):
    archivePath = self._createArchive(['content'])
    self.addCleanup(archivePath.unlink)
    with ZipFile(archivePath) as archive, \
         patch.object(archive, 'infolist', return_value=[Mock(file_size=4*1024**3+1)]):
      error = _checkImportArchive(archive)
    self.assertEqual(error, 'ERROR: eln file expands beyond 4294967296 bytes. Cannot process')


if __name__ == '__main__':
  unittest.main()
