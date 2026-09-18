#!/usr/bin/python3
"""Test browsing and selecting a Nextcloud file."""
import json
import unittest
from pathlib import Path

from pasta_eln.backend_worker.backend import Backend
from pasta_eln.configuration_file import loadConfiguration

from testsComplicated.nextcloud_common import NextcloudBrowser, readNclink, writeNclinks


class TestNextcloud(unittest.TestCase):
  """Test selecting a Nextcloud file after tests 20 to 22."""


  def test_main(self) -> None:
    """Select file 3531434, write its pointer, and scan it."""
    # setup Pasta
    print()
    backend = Backend('research')
    projectID = list(backend.db.getView('viewDocType/x0')['id'])[0]
    backend.changeHierarchy(projectID)

    # get account details
    instance = readNclink(next(backend.basePath.rglob('*.nclink')))['instance']
    credentials = loadConfiguration(backend.basePath/'.nextcloud_credentials.json')
    account = json.loads(credentials['addOnParameter']['nextcloud'][instance])

    # select a file with python functions
    browser = NextcloudBrowser(account)
    browser.openFolder('LabData')
    browser.openFolder('instruments')
    browser.openFolder('141_RoboMet')
    browser.openFolder('Training')
    browser.openFolder('Mosaic')
    browser.listFolder()  # folder content
    # print('\n'.join(str(i) for i in res))
    # targetFile = next(i for i in browser.listFolder() if i['name']=='Image Data.csv')
    selectedFiles = browser.selectFiles(['Image Data.csv'])
    self.assertEqual(selectedFiles[0]['fileId'], '3531434')

    # do the previously tested steps: write Nclinks, scan
    linkPath = writeNclinks(backend.cwd, instance, selectedFiles)[0]
    self.assertEqual(readNclink(linkPath)['fileId'], '3531434')

    backend.extractors.addOnPath = Path(__file__).parent
    backend.scanProject(None, projectID)
    view = backend.db.getView('viewHierarchy/viewPathsAll')
    item = next(i for i in view if 'Image Data.csv.nclink' in i['key'])
    scanned = backend.db.getDoc(item['id'])
    self.assertEqual(scanned['metaVendor']['nextcloudFileId'][0], '3531434')


if __name__ == '__main__':
  unittest.main()
