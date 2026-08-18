"""Regression tests for import preflight validation."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pasta_eln.backend_worker.input_output import importELN


class TestImportValidation(unittest.TestCase):
  def test_invalid_ro_crate_is_rejected_before_import(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
      archivePath = Path(directory) / 'invalid.eln'
      with ZipFile(archivePath, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('crate/ro-crate-metadata.json', json.dumps({
            '@graph': [{'@id': './', '@type': 'Dataset'}]}))

      report, statistics = importELN(object(), str(archivePath), 'project')

      self.assertEqual(report, 'ERROR: ro-crate is invalid. Cannot process')
      self.assertEqual(statistics, {})


if __name__ == '__main__':
  unittest.main()
