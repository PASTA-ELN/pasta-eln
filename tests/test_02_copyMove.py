#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: randomly move,copy,delete files to check resistance of scanning """
import os, shutil, logging, random
import warnings
import unittest
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.stringChanges import outputString
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
    projID = self.be.output('x0').split('|')[-1].strip()
    self.be.changeHierarchy(projID)

    progressBar = DummyProgressBar()
    choices = random.choices(range(100), k=150)
    choices =  [60,59,95,79,9,38,32,93,88,3,71,85,81,96,63,18,88,81,94,32,74,52,74,38,93,1,17,33,61,45,36,47,33,21,34,77,1,99,96,57,73,89,26,78,56,13,63,2,20,26,1,56,53,66,82,79,9,7,90,40,55,54,20,42,88,0,55,28,80,36,34,52,8,20,43,91,9,28,80,49,80,31,82,48,94,25,63,28,92,91,47,40,88,46,79,31,56,90,91,29,81,45,6,3,95,50,23,88,97,39,6,18,39,22,9,76,4,85,23,72,65,76,95,92,55,85,42,70,51,72,10,49,93,80,5,53,53,28,11,86,16,60,24,61,61,97,32,42,98,95]
    print(f'Current choice: [{",".join([str(i) for i in choices])}]')
    for epoch in range(5):
      print(f'\nStart epoch: {epoch}')
      allDirs = []
      allFiles = []
      for root, _, files in os.walk(self.be.basePath):
        if root.endswith('StandardOperatingProcedures') or root==str(self.be.basePath):
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
        print(iFile[len(str(self.be.basePath))+1:], op, target[len(str(self.be.basePath))+1:])
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
    print('Final scanning and verification')
    self.be.scanProject(progressBar, projID)
    self.verify()
    return

  def verify(self):
    #Verify DB
    output = self.be.checkDB(outputStyle='text')
    output = '\n'.join(output.split('\n')[8:])
    print(output)
    self.assertNotIn('**ERROR', output, 'Error in checkDB')
    self.assertLessEqual(len(output.split('\n')), 6, 'Check db should have less than 6 almost empty lines')
    return

  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
