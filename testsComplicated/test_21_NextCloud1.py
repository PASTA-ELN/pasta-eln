#!/usr/bin/python3
"""Test the complete headless Nextcloud link workflow."""
import json
import unittest
from pathlib import Path

from pasta_eln.backend_worker.backend import Backend
from pasta_eln.configuration_file import saveConfiguration


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
    from .nextcloud_common import readNclink, writeNclink
    targetFile = {'name':'Al1.TXT', 'fileId':'1580', 'nextcloudETag': '"fb39837ff04d4fe55fa338a14357ae33"',
                  'nextcloudContentType': 'text/plain', 'nextcloudSize': 43580}
    linkPath = writeNclink(backend.cwd, config['instance'], targetFile)  #assemble nclink-path

    # 1b. Verify only: Read it back and verify its durable identity.
    link = readNclink(linkPath)
    self.assertEqual(link['fileId'], targetFile['fileId'])
    self.assertEqual(link['name'], targetFile['name'])

    # 2. Exercise the extractor.
    from .extractor_nclink import use
    result = use(linkPath, {'main':''})
    self.assertIn('metaVendor', result)
    self.assertIn('metaUser', result)


if __name__ == '__main__':
  unittest.main()
