#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, logging
import warnings
import unittest
import re
from pathlib import Path
from pasta_eln.backendWorker.backend import Backend
from pasta_eln.textTools.stringChanges import outputString
from pasta_eln.miscTools import getConfiguration


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
    outputFormat = 'print'  #change to 'print' for human usage, '' for less output
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)

    log_records = []
    class ErrorHandler(logging.Handler):
      def emit(self, record):
        if record.levelno >= logging.ERROR:
          log_records.append(record)
    handler = ErrorHandler()
    logging.getLogger().addHandler(handler)

    projectGroup = 'research'
    configuration, _ = getConfiguration(projectGroup)
    path = 'Data_SynteticNiAl_Indentation'
    self.be = Backend(configuration, projectGroup)

    self.dirName = self.be.basePath
    addOnePath = self.be.addOnPath
    self.be.exit()
    shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    shutil.copy(Path(__file__).parent/path/'extractor_hdf5.py', addOnePath/'extractor_hdf5.py')
    self.be = Backend(configuration, projectGroup)
    print()

    # adopt measurements view
    measurementView = 'name,tags,metaUser.alloy,metaUser.H_GPa,metaUser.E_GPa,metaUser.hc_um,metaUser.pMax_mN'
    self.be.db.cursor.execute(f'UPDATE docTypes SET view = "{measurementView}" WHERE docType = "measurement"')

    # Create structure
    self.be.addData('x0', {'name': 'Nanoindentation NiAl', '.objective': 'Understand mechanical properties of different NiAl ',
                         '.status': 'active', 'comment': 'For tutorial'})
    dfProj  = self.be.db.getView('viewDocType/x0')
    projID1 = list(dfProj['id'])[0]
    self.be.changeHierarchy(projID1)
    dir1ID = self.be.addData('x1', {'comment': '', 'name': 'Alloy 1'})['id']
    dir2ID = self.be.addData('x1', {'comment': 'This has to be continued', 'tags':['TODO'], 'name': 'Alloy 2'})['id']

    self.be.changeHierarchy(dir1ID)
    dir1Path = self.be.basePath/self.be.cwd
    pattern = re.compile(r'NiAl_1_')
    for file in (Path(__file__).parent / path).iterdir():
      if file.is_file() and pattern.match(file.name):
        shutil.copy(file, dir1Path)

    self.be.changeHierarchy(dir2ID)
    dir2Path = self.be.basePath/self.be.cwd
    pattern = re.compile(r'NiAl_2_')
    for file in (Path(__file__).parent / path).iterdir():
      if file.is_file() and pattern.match(file.name):
        shutil.copy(file, dir2Path)

    #scan all
    self.be.scanProject(None, projID1)

    # Final output
    (addOnePath/'extractor_hdf5.py').unlink()
    self.be.changeHierarchy(projID1)
    outputString(outputFormat,'info', self.be.outputHierarchy(onlyHierarchy=False, addID=True))

    df = self.be.db.getView('viewDocType/measurement')
    print('Measurements')
    print(df)
    print('One document')
    docID = list(df['id'])[0]
    doc = self.be.db.getDoc(docID)
    del doc['image']
    print(doc)

    logging.getLogger().removeHandler(handler)
    self.assertEqual(len(log_records), 0, f"Logging errors found: {[r.getMessage() for r in log_records]}")

