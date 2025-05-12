#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: randomly move,copy,delete files to check resistance of scanning """
import os, shutil, logging, random
import warnings
import unittest
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.textTools.stringChanges import outputString
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

    choices = random.choices(range(100), k=250)
    choices =  [87,90,89,65,91,27,82,79,16,97,85,40,26,69,49,25,47,21,84,82,35,4,67,59,13,12,89,51,4,6,75,53,3,82,5,54,2,36,26,19,45,85,33,16,53,63,40,61,82,33,56,10,0,50,5,35,52,82,46,82,78,14,80,75,78,67,19,72,26,33,74,54,7,66,90,78,99,89,88,76,17,15,98,20,89,35,80,34,82,80,64,68,69,95,41,92,62,32,94,67,20,72,25,32,45,4,77,48,50,6,3,59,29,25,74,30,75,78,76,7,23,72,88,0,33,30,61,79,8,19,54,66,58,95,99,3,94,59,32,49,54,75,4,16,14,68,40,83,29,94,61,43,90,42,48,6,4,44,86,13,46,15,75,36,60,76,90,74,85,71,98,77,27,60,92,72,66,88,66,89,21,45,98,9,71,61,42,74,31,53,27,88,94,47,96,64,92,93,5,46,18,61,48,73,56,25,83,11,81,43,77,1,12,20,92,10,53,79,38,55,57,45,21,68,69,92,80,23,69,70,38,22,66,6,48,38,64,53,10,12,39,62,77,97,42,68,57,71,23,75]
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
        self.be.scanProject(None, projID)
      if choices.pop(0)%2==1:
        print('Start scanning')
        self.be.scanProject(None, projID)
    print('Final scanning and verification')
    self.be.scanProject(None, projID)
    self.verify()
    self.be.changeHierarchy(projID)
    print(self.be.outputHierarchy(False))
    print(f'{"*"*40}\nEND TEST 02 \n{"*"*40}')
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
