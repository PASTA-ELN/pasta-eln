#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, logging, socket
import warnings
import unittest
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.inputOutput import exportELN, importELN
from pasta_eln.miscTools import outputString
from pasta_eln.miscTools import DummyProgressBar
try:
  from eln_validator import checkFile
  elnValidation = True
except:
  elnValidation = False


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
    if socket.gethostname()=='dena':  #SB's computer
      projectGroup = 'pasta_tutorial'
    else:
      projectGroup = 'research'
    self.be = Backend(projectGroup, initConfig=False)

    # export
    idProj = self.be.db.getView('viewDocType/x0')[0]['id']
    self.fileName = str(Path.home()/'temporary_pastaTest.eln')
    status = exportELN(self.be, idProj, self.fileName)
    print(f'Export to: {self.fileName}\n{status}')
    self.assertEqual(status[:21],'Success: exported 31 ','Export unsuccessful')

    # verify eln
    print('\n\n---------------\nVerification')
    if elnValidation:
      checkFile(Path(self.fileName), verbose=True, plot=False)

    # remove old
    docProj = self.be.db.getDoc(idProj)
    oldPath = self.be.basePath/docProj['-branch'][0]['path']
    shutil.rmtree(oldPath)
    allDocs = self.be.db.getView('viewHierarchy/viewHierarchy',    startKey=idProj)
    for doc in allDocs:
      self.be.db.remove(doc['id'])

    # import
    status = importELN(self.be, self.fileName)
    print(status)
    self.assertEqual(status[:7],'Success','Import unsuccessful')

    #test / verify
    print('Number of documents', len(self.be.db.getView('viewHierarchy/viewHierarchy',    startKey=idProj)))
    outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
    outputString(outputFormat,'info', self.be.checkDB(outputStyle='text'))
    outputString(outputFormat,'h2','DONE WITH VERIFY')
    fileCount = 0
    for _, _, files in os.walk(self.be.basePath):
      fileCount+=len(files)
    print('Number of files 25=', fileCount)
    self.assertEqual(fileCount, 25, 'Not 25 files exist')
    return

  def tearDown(self):
    logging.info('End Export-import test')
    # Path(self.fileName).unlink()  #remove file
    return

if __name__ == '__main__':
  unittest.main()
