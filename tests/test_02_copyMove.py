#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: randomly move,copy,delete files to check resistance of scanning """
import os, shutil, traceback, logging, random
from datetime import datetime
import warnings
import unittest
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.miscTools import outputString
from pasta_eln.miscTools import DummyProgressBar
from pasta_eln.installationTools import exampleData

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
    outputFormat = ''  #change to 'print' for human usage, '' for less output
    dummyProgressBar = DummyProgressBar()
    # initialization: create database, destroy on filesystem and database and then create new one
    warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
    warnings.filterwarnings('ignore', message='invalid escape sequence')
    warnings.filterwarnings('ignore', category=ResourceWarning, module='PIL')
    warnings.filterwarnings('ignore', category=ImportWarning)
    logPath = Path.home()/'pastaELN.log'
    logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                        datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
    for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
      logging.getLogger(package).setLevel(logging.WARNING)
    logging.info('Start 02 test')
    self.be = Backend('research')
    output = self.be.output('x0')
    projID = output.split('|')[-1].strip()
    self.be.changeHierarchy(projID)

    progressBar = DummyProgressBar()
    choices = random.choices(range(100), k=100)
    print(f'Current choice: {choices}')
    for epoch in range(5):
      print(f'\nStart epoch: {epoch}')
      allDirs = []
      allFiles = []
      for root, _, files in os.walk(self.be.basePath):
        if root.endswith('StandardOperatingProcedures'):
          continue
        allDirs.append(root)
        allFiles += [f'{root}{os.sep}{i}' for i in files if i not in ('.id_pastaELN.json','pastaELN.db')]
      for iFile in allFiles:
        op = ['keep','copy','move','delete'][choices.pop(0)%4]
        parent = Path(iFile).parent
        possTargets = [i for i in allDirs if Path(i)!=parent]
        target = possTargets[choices.pop(0)%len(possTargets)]
        if choices.pop(0)%4==0:
          target += '/NewDirectory'
        print(iFile, op,target)
        try:
          if op=='keep':
            continue
          elif op=='copy':
            shutil.copy(iFile, target)
          elif op=='move':
            shutil.move(iFile, target)
          elif op=='delete':
            os.unlink(iFile)
        except shutil.Error:
          pass  #skip step if invalid step because file already exists in that folder
      if choices.pop(0)%2==1:
        print('Start scanning')
        self.be.scanProject(progressBar, projID)
      if choices.pop(0)%2==1:
        print('Start scanning')
        self.be.scanProject(progressBar, projID)

    self.verify()
    return

  def verify(self):
    #Verify DB
    output = self.be.checkDB(outputStyle='text')
    output = '\n'.join(output.split('\n')[8:])
    self.assertNotIn('**ERROR', output, 'Error in checkDB')
    self.assertEqual(len(output.split('\n')), 8, 'Check db should have 8 more-less empty lines')
    return

  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
