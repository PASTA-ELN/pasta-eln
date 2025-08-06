#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: randomly move,copy,delete files to check resistance of scanning """
import os, shutil, logging, random
import warnings
import unittest
from pathlib import Path
from pasta_eln.backendWorker.backend import Backend
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
    configuration, _ = getConfiguration('research')
    self.be = Backend(configuration, 'research')
    projID = self.be.output('x0').split('|')[-2].strip()
    self.be.changeHierarchy(projID)

    choices = random.choices(range(100), k=250)
    # choices =
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
