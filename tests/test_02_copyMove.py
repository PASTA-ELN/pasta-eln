#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: randomly move,copy,delete files to check resistance of scanning """
import os, shutil, logging, random
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
    projID = self.be.output('x0').split('|')[-1].strip()
    self.be.changeHierarchy(projID)

    progressBar = DummyProgressBar()
    choices = random.choices(range(100), k=150)
    choices =  [67,87,0,18,31,2,32,88,67,92,67,71,90,38,61,66,81,42,46,62,8,21,43,30,23,3,19,35,16,48,91,39,96,84,48,88,9,81,65,68,5,85,97,6,87,24,9,38,31,40,14,33,96,93,9,82,43,30,48,19,90,49,73,43,27,5,95,25,77,99,82,99,90,52,42,7,0,58,55,89,52,88,63,64,3,79,66,26,7,42,36,75,50,89,46,40,98,67,4,89,48,65,65,55,60,96,20,88,75,18,88,18,66,68,69,77,68,88,73,97,3,35,70,57,66,21,0,17,60,19,96,46,87,99,95,97,47,95,50,36,64,34,22,15,17,6,97,36,61,99]
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
    self.assertNotIn('**ERROR', output, 'Error in checkDB')
    self.assertEqual(len(output.split('\n')), 8, 'Check db should have 8 more-less empty lines')
    return

  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
