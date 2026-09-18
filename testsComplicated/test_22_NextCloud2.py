#!/usr/bin/python3
"""Test subsequent scans and failures of the Nextcloud link workflow.
  - Stable document ID and pointer hash after rescanning.
  - Original filename preservation.
  - Encrypted credential storage.
  - Stale ETag detection.
  - Missing credentials.
  - Invalid credentials.
  - Restoration of every temporarily modified local file.
"""
import json
import unittest
from pathlib import Path

import requests

from pasta_eln.backend_worker.backend import Backend
from pasta_eln.configuration_file import loadConfiguration, saveConfiguration

from testsComplicated.extractor_nclink import use
from testsComplicated.nextcloud_common import readNclink


class TestNextcloud(unittest.TestCase):
  """Test an existing Nextcloud link created by test 21."""


  def test_main(self) -> None:
    """Rescan the link and exercise authentication and change failures."""
    backend = Backend('research')
    linkPath = next(backend.basePath.rglob('*.nclink'))
    link = readNclink(linkPath)
    relativePath = linkPath.relative_to(backend.basePath).as_posix()
    view = backend.db.getView('viewHierarchy/viewPathsAll', preciseKey=relativePath)
    before = backend.db.getDoc(view[0]['id'])

    # A standard rerun keeps the existing document and pointer hash.
    projectID = before['branch'][0]['stack'][0]
    backend.extractors.addOnPath = Path(__file__).parent
    backend.scanProject(None, projectID)
    view = backend.db.getView('viewHierarchy/viewPathsAll', preciseKey=relativePath)
    after = backend.db.getDoc(view[0]['id'])
    self.assertEqual(after['id'], before['id'])
    self.assertEqual(after['shasum'], before['shasum'])
    self.assertEqual(after['name'], link['name'])

    # Credentials retain their plaintext type but not their secrets.
    credentialsPath = backend.basePath/'.nextcloud_credentials.json'
    credentialsText = credentialsPath.read_text(encoding='utf-8')
    stored = json.loads(credentialsText)
    credentials = loadConfiguration(credentialsPath)
    account = json.loads(credentials['addOnParameter']['nextcloud'][link['instance']])
    self.assertEqual(stored['type'], 'pasta nextcloud credential file')
    self.assertNotIn(account['appPassword'], credentialsText)

    # A stale pointer detects changed remote data.
    pointerBytes = linkPath.read_bytes()
    staleLink = link | {'nextcloudETag':'invalid-test-etag'}
    linkPath.write_text(json.dumps(staleLink, ensure_ascii=False, sort_keys=True)+'\n', encoding='utf-8')
    try:
      with self.assertRaisesRegex(ValueError, 'nextcloudETag'):
        use(linkPath, {'main':''})
    finally:
      linkPath.write_bytes(pointerBytes)

    # Missing and invalid credentials fail without modifying the pointer.
    backupPath = credentialsPath.with_name('.nextcloud_credentials.test-backup.json')
    credentialsPath.rename(backupPath)
    try:
      with self.assertRaises(FileNotFoundError):
        use(linkPath, {'main':''})
    finally:
      backupPath.rename(credentialsPath)

    credentialsBytes = credentialsPath.read_bytes()
    account['appPassword'] = 'invalid-pasta-nextcloud-test-password'
    credentials['addOnParameter']['nextcloud'][link['instance']] = json.dumps(account)
    saveConfiguration(credentials, credentialsPath)
    try:
      with self.assertRaises(requests.RequestException):
        use(linkPath, {'main':''})
    finally:
      credentialsPath.write_bytes(credentialsBytes)


if __name__ == '__main__':
  unittest.main()
