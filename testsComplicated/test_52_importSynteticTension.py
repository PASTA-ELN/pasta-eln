#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, json, uuid
import warnings
import unittest
import pandas as pd
import numpy as np
import re
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.miscTools import DummyProgressBar
from pasta_eln.textTools.stringChanges import outputString

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
    outputFormat = 'print'  #change to 'print' for human usage, '' for less output
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)

    projectGroup = 'research'
    path = 'Data_SynteticALMTensile'
    self.be = Backend(projectGroup)

    self.dirName = self.be.basePath
    self.be.exit()
    shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    self.be = Backend(projectGroup)
    print()

    # adopt measurements view
    measurementView = 'name,tags,metaUser.direction,metaUser.maxstrain,metaUser.strength,metaUser.yieldstress,metaUser.youngsmodulus'
    self.be.db.cursor.execute(f'UPDATE docTypes SET view = "{measurementView}" WHERE docType = "measurement"')

    # Create structure
    self.be.addData('x0', {'name': 'Tensile testing of ALM metal', '.objective': 'Test if printing direction influences the mechanical properties.',
                         '.status': 'active', 'comment': 'For tutorial'})
    dfProj  = self.be.db.getView('viewDocType/x0')
    projID1 = list(dfProj['id'])[0]
    self.be.changeHierarchy(projID1)
    dir1ID = self.be.addData('x1', {'comment': '', 'name': 'Printing direction 0'})['id']
    dir2ID = self.be.addData('x1', {'comment': 'This has to be continued', 'tags':['TODO'], 'name': 'Printing direction 90'})['id']

    self.be.changeHierarchy(dir1ID)
    dir1Path = self.be.basePath/self.be.cwd
    pattern = re.compile(r'Measurement_0_')
    for file in (Path(__file__).parent / path).iterdir():
      if file.is_file() and pattern.match(file.name):
        shutil.copy(file, dir1Path)

    self.be.changeHierarchy(dir2ID)
    dir2Path = self.be.basePath/self.be.cwd
    pattern = re.compile(r'Measurement_90_')
    for file in (Path(__file__).parent / path).iterdir():
      if file.is_file() and pattern.match(file.name):
        shutil.copy(file, dir2Path)

    #scan all
    self.be.scanProject(None, projID1)

    # Final output
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
