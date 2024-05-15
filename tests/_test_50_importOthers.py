#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, logging
import warnings
import unittest
import tempfile
import urllib.request
import pytest
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.inputOutput import exportELN, importELN
from pasta_eln.miscTools import outputString
from pasta_eln.miscTools import DummyProgressBar
try:
  from eln_validator import checkFile
except:
  pass

class TestStringMethods(unittest.TestCase):
  """
  derived class for this test
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.be = None
    self.dirName = ''

  @pytest.mark.skip(
    reason="Disabled for github since cannot create couchdb instance during actions")
  def test_main(self):
    """
    main function
    """
    outputFormat = 'print'
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)

    # setup
    localPath = Path('/home/steffen/FZJ/DataScience/Repositories/TheELNConsortium/TheELNFileFormat/examples')
    dirpath = localPath if localPath.exists() else Path(tempfile.mkdtemp())
    baseURL = 'https://github.com/TheELNConsortium/TheELNFileFormat/raw/master/examples/'
    files = [('kadi4mat/records-example.eln', 6), ('kadi4mat/collections-example.eln', 18),
             ('SampleDB/sampledb_export.eln', 13)]
    for fileI, numFiles in files:
      # remove everything else
      self.be = Backend('research', initConfig=False)
      self.dirName = self.be.basePath
      self.be.exit(deleteDB=True)
      shutil.rmtree(self.dirName)
      os.makedirs(self.dirName)
      self.be = Backend('research', initViews=True, initConfig=False)

      elnFile = dirpath/fileI
      if not elnFile.exists():
        print(f'Download file {elnFile}')
        elnFile.parent.mkdir(exist_ok=True)
        try:
          urllib.request.urlretrieve(baseURL+fileI, elnFile)
        except:
          print(f'Could not download eln file {baseURL+fileI} to {elnFile}')
          return

      # import
      print(f'\n\n==============================\nImport {fileI}\n==============================')
      status = importELN(self.be, str(elnFile))
      print(status)
      self.assertEqual(status[:7],'Success','Import unsuccessful')

      # test / verify after import
      print('Number of documents', len(self.be.db.getView('viewHierarchy/viewHierarchy')))
      outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
      outputString(outputFormat,'info', self.be.checkDB(outputStyle='text'))
      outputString(outputFormat,'h2','Tree of results on hard disk')
      os.system(f'tree {self.be.basePath}')
      outputString(outputFormat,'h2','DONE WITH VERIFY')

      fileCount = 0
      for _, _, files in os.walk(self.be.basePath):
        fileCount+=len(files)
      print(f'Number of files should:{numFiles} = reality:{fileCount}')
      self.assertEqual(fileCount, numFiles, f'Not {numFiles} files exist')
    return

  def tearDown(self):
    logging.info('End Import others test')
    return

if __name__ == '__main__':
  unittest.main()
