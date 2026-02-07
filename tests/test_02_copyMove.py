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

    log_records = []
    class ErrorHandler(logging.Handler):
      def emit(self, record):
        if record.levelno >= logging.ERROR:
          log_records.append(record)
    handler = ErrorHandler()
    logging.getLogger().addHandler(handler)

    configuration, _ = getConfiguration('research')
    self.be = Backend(configuration, 'research')
    projID = self.be.output('x0').split('|')[-2].strip()
    self.be.changeHierarchy(projID)

    choices = random.choices(range(100), k=260)
    choices = [22,0,30,56,30,10,29,14,82,73,97,3,17,61,85,7,14,71,4,40,4,7,34,55,2,32,46,33,69,58,13,99,49,28,37,72,74,20,31,12,44,24,73,55,40,35,22,21,58,59,51,43,59,96,88,80,71,0,4,21,4,3,89,24,46,63,97,91,48,8,56,65,73,38,1,10,34,70,66,45,29,45,12,0,77,44,22,97,34,93,79,15,18,8,65,42,87,50,80,64,75,77,60,2,52,60,77,41,42,35,24,66,11,34,17,22,0,51,43,77,41,76,76,1,11,41,94,84,59,4,84,31,42,48,9,96,88,22,1,44,66,82,38,53,88,80,70,1,68,42,50,71,84,95,28,82,85,2,48,75,32,29,74,73,34,53,66,39,98,68,31,55,16,58,64,67,80,69,99,95,44,35,11,2,61,84,27,6,88,1,26,61,58,49,22,27,45,37,57,37,32,25,51,57,76,55,75,51,58,52,31,94,88,7,3,73,75,80,74,47,98,58,53,39,49,52,77,31,15,80,87,43,81,35,83,40,16,44,2,76,74,82,17,68,21,51,60,38,49,47,59,64,77,11,75,29,62,5,77,10]
    print(f'Current choice: [{",".join([str(i) for i in choices])}]')
    for epoch in range(5):
      print(f'\nStart epoch: {epoch}')
      allDirs = []
      allFiles = []
      for root, _, files in os.walk(self.be.basePath):
        if root.endswith('CommonFiles') or root==str(self.be.basePath):
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

    logging.getLogger().removeHandler(handler)
    self.assertEqual(len(log_records), 0, f"Logging errors found: {[r.getMessage() for r in log_records]}")
    return

  def verify(self):
    #Verify DB
    output = self.be.checkDB(outputStyle='text')
    output = '\n'.join(output.split('\n')[8:])
    print(output)
    self.assertNotIn('**ERROR', output, 'Error in checkDB')
    self.assertLessEqual(len(output.split('\n')), 8, 'Check db should have less than 8 almost empty lines')
    return

  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
