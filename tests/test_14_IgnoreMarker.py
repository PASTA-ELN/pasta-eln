#!/usr/bin/python3
"""Test recursive folder ignore marker during scan and database checks."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pasta_eln.backendWorker.backend import Backend
from pasta_eln.fixedStringsJson import CONF_FILE_NAME


class TestIgnoreMarker(unittest.TestCase):
  """
  Tests for folders containing .pastaELN_ignore.
  """

  def setUp(self):
    self.tempDir = tempfile.TemporaryDirectory()
    self.homePatch = patch('pathlib.Path.home', return_value=Path(self.tempDir.name))
    self.homePatch.start()
    self.configuration = {
        'defaultProjectGroup': 'research',
        'projectGroups': {
            'research': {
                'local': {'database': 'research', 'path': self.tempDir.name},
                'remote': {},
                'addOnDir': str(Path(__file__).parents[1]/'pasta_eln'/'AddOns'),
                'addOns': {'project': {}, 'extractors': {}, 'table': {}}
            }
        },
        'version': 3,
        'userID': 'test_user'
    }
    with open(Path(self.tempDir.name)/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.configuration))
    self.backend = Backend('research')
    self.project = self.backend.addData('x0', {'name': 'Ignore Marker Project'})
    self.projectID = self.project['id']
    self.projectPath = self.backend.basePath/self.project['branch'][0]['path']


  def tearDown(self):
    self.backend.exit()
    self.homePatch.stop()
    self.tempDir.cleanup()


  def test_ignored_untracked_folder_is_not_added_or_reported(self):
    ignoredPath = self.projectPath/'raw'
    ignoredPath.mkdir()
    (ignoredPath/'.pastaELN_ignore').touch()
    (ignoredPath/'data.txt').write_text('ignored data', encoding='utf-8')

    self.backend.scanProject(None, self.projectID)

    paths = [i['key'] for i in self.backend.db.getView('viewHierarchy/viewPathsAll')]
    self.assertNotIn((ignoredPath.relative_to(self.backend.basePath)).as_posix(), paths)
    self.assertNotIn((ignoredPath/'data.txt').relative_to(self.backend.basePath).as_posix(), paths)
    self.assertNotIn('**ERROR', self.backend.checkDB(outputStyle='text'))


  def test_ignored_existing_folder_entries_are_preserved(self):
    self.backend.changeHierarchy(self.projectID)
    ignoredDoc = self.backend.addData('x1', {'name': 'Ignored Existing'})
    ignoredPath = self.backend.basePath/ignoredDoc['branch'][0]['path']
    ignoredID = ignoredDoc['id']
    self.backend.changeHierarchy(ignoredID)
    dataPath = ignoredPath/'data.txt'
    dataPath.write_text('registered data', encoding='utf-8')
    dataDoc = self.backend.addData('', {'name': 'data.txt'})
    dataID = dataDoc['id']

    (ignoredPath/'.pastaELN_ignore').touch()
    dataPath.unlink()

    self.backend.scanProject(None, self.projectID)

    pathsByID = {i['id']: i['key'] for i in self.backend.db.getView('viewHierarchy/viewPathsAll')}
    self.assertEqual(pathsByID[ignoredID], ignoredDoc['branch'][0]['path'])
    self.assertEqual(pathsByID[dataID], dataDoc['branch'][0]['path'])
    self.assertNotIn('**ERROR', self.backend.checkDB(outputStyle='text'))


if __name__ == '__main__':
  unittest.main()
