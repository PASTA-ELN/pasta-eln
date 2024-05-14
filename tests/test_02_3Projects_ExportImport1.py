#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, logging
import warnings
import unittest
from pathlib import Path
import pytest
from pasta_eln.backend import Backend
from pasta_eln.inputOutput import exportELN, importELN
from pasta_eln.miscTools import outputString

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
    # main test function: create stuff, test, ...
    outputFormat = 'print'
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    projectGroup = 'research'
    self.be = Backend(projectGroup, initConfig=False)

    # change documents
    docIDs = [i.split('|')[-1].strip() for i in self.be.output('procedure',True).split('\n')[2:-1]]
    docIDs +=[i.split('|')[-1].strip() for i in self.be.output('sample',True).split('\n')[2:-1]]
    for idx,docID in enumerate(docIDs):
      doc = self.be.db.getDoc(docID)
      doc['comment'] = f'Test string {idx}'
      self.be.editData(doc)

    # export
    viewProj = self.be.db.getView('viewDocType/x0')
    idProj  = [i['id'] for i in viewProj if i['value'][0]=='Intermetals at interfaces'][0]
    self.fileName = str(Path.home()/'temporary_pastaTest.eln')
    status = exportELN(self.be, [idProj], self.fileName, ['procedure','measurement','sample'])
    print(f'Export to: {self.fileName}\n{status}')
    self.assertEqual(status[:21],'Success: exported 12 ','Export unsuccessful')

    # verify eln
    print('\n\nEnd export\n----------------------\nStart verification')
    #testELNFile(self.fileName)

    # IMPORT NOT IMPLEMENTED YET
    # # remove old
    # docProj = self.be.db.getDoc(idProj)
    # oldPath = self.be.basePath/docProj['-branch'][0]['path']
    # shutil.rmtree(oldPath)
    # allDocs = self.be.db.getView('viewHierarchy/viewHierarchy',    startKey=idProj)
    # for doc in allDocs:
    #   self.be.db.remove(doc['id'])

    # # import
    # print('\n\n---------------\nImport')
    # status = importELN(self.be, self.fileName)
    # print(status)
    # self.assertEqual(status[:7],'Success','Import unsuccessful')

    # #test / verify
    # print('Number of documents', len(self.be.db.getView('viewHierarchy/viewHierarchy',    startKey=idProj)))
    # outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
    # outputString(outputFormat,'info', self.be.checkDB(outputStyle='text'))
    # outputString(outputFormat,'h2','DONE WITH VERIFY')
    # fileCount = 0
    # for _, _, files in os.walk(self.be.basePath):
    #   fileCount+=len(files)
    # print(f'Number of files 15 (should be) = {fileCount} (are)')
    # self.assertEqual(fileCount, 15, 'Imported entries are not 15, as they should.')
    return

  def tearDown(self):
    logging.info('End Export-import test')
    # Path(self.fileName).unlink()  #remove file
    return


if __name__ == '__main__':
  unittest.main()
