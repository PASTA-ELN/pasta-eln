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
    # choices =  [60,70,90,45,20,39,12,90,11,59,73,47,73,45,58,38,93,55,96,60,19,68,42,12,16,60,38,55,36,59,91,99,46,84,34,71,97,87,18,61,42,67,53,75,35,48,38,65,65,71,74,88,48,65,47,70,49,16,67,51,14,68,12,26,44,80,83,38,90,16,77,12,18,75,38,45,92,68,34,20,30,85,21,38,53,33,20,84,59,82,66,68,59,71,48,93,61,90,63,69]
    print(f'Current choice: [{','.join([str(i) for i in choices])}]')
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
        op = ['keep','copy','copy','move','move','delete'][choices.pop(0)%6]
        parent = Path(iFile).parent
        possTargets = [i for i in allDirs if Path(i)!=parent]
        target = possTargets[choices.pop(0)%len(possTargets)]
        if choices.pop(0)%4==0:
          target += f'/NewDirectory/{Path(iFile).name}'
        print(iFile, op,target)
        try:
          if op=='keep':
            continue
          elif op=='copy':
            if not Path(target).parent.is_dir():
              Path(target).parent.mkdir()
            shutil.copy(iFile, target)
          elif op=='move':
            if not Path(target).parent.is_dir():
              Path(target).parent.mkdir()
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
    print('Final verification')
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
