#!/usr/bin/python3
"""Tests for elabFTW raw upload size limits."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pasta_eln.backendWorker.elabFTWsync import Pasta2Elab
from pasta_eln.installationTools import createDefaultConfiguration


class TestElabFTWUploadLimit(unittest.TestCase):
  """Test raw file upload size limit handling."""

  def makeSync(self, maxUploadSizeMB=100):
    sync = Pasta2Elab.__new__(Pasta2Elab)
    sync.projectGroup = 'research'
    maxUploadSize = f'{maxUploadSizeMB // 1024} GB' if maxUploadSizeMB >= 1024 else f'{maxUploadSizeMB} MB'
    sync.backend = SimpleNamespace(configuration={
        'GUI': {'maxUploadSize': maxUploadSize},
        'projectGroups': {
            'research': {
                'remote': {}
            }
        }
    })
    return sync


  def test_default_configuration_sets_upload_limit(self):
    with tempfile.TemporaryDirectory() as tempDir:
      configuration = createDefaultConfiguration(Path(tempDir))
    self.assertEqual(configuration['GUI']['maxUploadSize'], '100 MB')


  def test_allows_file_at_limit(self):
    with tempfile.TemporaryDirectory() as tempDir:
      path = Path(tempDir)/'raw.bin'
      with open(path, 'wb') as fOut:
        fOut.truncate(10 * 1024 * 1024)
      sync = self.makeSync(maxUploadSizeMB=10)

      self.assertTrue(sync.rawDataUploadAllowed(path, 'doc-1'))


  def test_skips_file_above_limit(self):
    with tempfile.TemporaryDirectory() as tempDir:
      path = Path(tempDir)/'raw.bin'
      with open(path, 'wb') as fOut:
        fOut.truncate(20 * 1024 * 1024)
      sync = self.makeSync(maxUploadSizeMB=10)

      self.assertFalse(sync.rawDataUploadAllowed(path, 'doc-1'))


if __name__ == '__main__':
  unittest.main()
