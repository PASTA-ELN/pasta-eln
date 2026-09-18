#!/usr/bin/python3
"""Test the complete headless Nextcloud link workflow."""
import json
import unittest
from pathlib import Path

from pasta_eln.backend_worker.backend import Backend
from pasta_eln.configuration_file import saveConfiguration

from testsComplicated.nextcloud_common import readNclink, writeNclink
from testsComplicated.extractor_nclink import use

class TestNextcloud(unittest.TestCase):
  """Test Nextcloud access, link creation, and extraction."""


  def test_main(self) -> None:
    """Create and extract an `.nclink` without using GUI components."""

    # get nextcloud credentials for testing
    testingConfigPath = Path.home()/'.pastaELN_testing.json'
    if not testingConfigPath.exists():
      print('**ERROR**: No testing configuration file found.')
      return
    config = json.loads(testingConfigPath.read_text(encoding='utf-8'))['nextcloud']

    # use backend and create credential file
    backend = Backend('research')
    credentialsPath = backend.basePath/'.nextcloud_credentials.json'
    saveConfiguration({'type':'pasta nextcloud credential file', 'version':4, 'addOnParameter':{'nextcloud':{
          config['instance']:json.dumps({key:config[key] for key in ('url','loginName','appPassword')})}}}, credentialsPath)

    # go into a project
    dfProj  = backend.db.getView('viewDocType/x0')
    projID1 = list(dfProj['id'])[0]
    backend.changeHierarchy(projID1)

    # 1. Create the pointer from the selected-file information
    targetFile = {'name':'scratch.png', 'fileId':'1568', 'nextcloudETag': '"b4766562a8467914ce3ce8354946bfa2"',
                  'nextcloudContentType': 'image/png', 'nextcloudSize': 314033}
    linkPath = writeNclink(backend.cwd, config['instance'], targetFile)  #assemble nclink-path

    # 2. Verify only - not in production: Read it back and verify its durable identity.
    link = readNclink(linkPath)
    self.assertEqual(link['fileId'], targetFile['fileId'])
    self.assertEqual(link['name'], targetFile['name'])

    # 3. Verify only - not in production: Exercise the extractor.
    result = use(linkPath, {'main':''})
    self.assertIn('metaVendor', result)
    self.assertIn('metaUser', result)

    # 4. Scan
    backend.extractors.addOnPath = Path(__file__).parent
    backend.scanProject(None, projID1)

    # 5. Check scan is correct
    view = backend.db.getView('viewHierarchy/viewPathsAll', startKey=linkPath.relative_to(backend.basePath).as_posix())
    scanned = backend.db.getDoc(view[0]['id'])
    self.assertEqual(scanned['metaVendor']['nextcloudFileId'][0], targetFile['fileId'])
    self.assertEqual(scanned['metaVendor']['nextcloudETag'][0], targetFile['nextcloudETag'])

if __name__ == '__main__':
  unittest.main()
