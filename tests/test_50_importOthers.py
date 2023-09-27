#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, logging, socket
import warnings
import unittest
import tempfile
import urllib.request
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

  def test_main(self):
    """
    main function
    """
    dummyProgressBar = DummyProgressBar()
    outputFormat = 'print'
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    projectGroup = 'research'
    url = 'https://github.com/TheELNConsortium/TheELNFileFormat/raw/master/examples/elabftw/multiple-database-items.eln'
    dirpath = Path(tempfile.mkdtemp())
    elnFile = dirpath/'multiple-database-items.eln'
    urllib.request.urlretrieve(url, elnFile)

    # remove everything else
    self.be = Backend(projectGroup, initConfig=False)
    self.dirName = self.be.basePath
    self.be.exit(deleteDB=True)
    shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    self.be = Backend(projectGroup, initViews=True, initConfig=False)

    # import
    print('\n\n---------------\nImport')
    status = importELN(self.be, str(elnFile))
    print(status)
    self.assertEqual(status[:7],'Success','Import unsuccessful')

    # test / verify after import
    print('Number of documents', len(self.be.db.getView('viewHierarchy/viewHierarchy')))
    outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
    outputString(outputFormat,'info', self.be.checkDB(outputStyle='text'))
    outputString(outputFormat,'h2','DONE WITH VERIFY')
    fileCount = 0
    for _, _, files in os.walk(self.be.basePath):
      fileCount+=len(files)
    print('Number of files 8 =', fileCount)
    self.assertEqual(fileCount, 8, 'Not 8 files exist')
    return

  def tearDown(self):
    logging.info('End Import others test')
    return

if __name__ == '__main__':
  unittest.main()
