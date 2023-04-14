#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, sys, shutil, traceback, logging, subprocess, socket
import warnings, json
import unittest
from pathlib import Path

from ..backend import Backend             # pylint: disable=relative-beyond-top-level

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
    warnings.filterwarnings('ignore', module='js2py')
    logPath = Path.home()/'pastaELN.log'
    logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                        datefmt='%m-%d %H:%M:%S')   #This logging is always info, since for installation only
    for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
      logging.getLogger(package).setLevel(logging.WARNING)
    logging.info('Start 3Projects test')

    if socket.gethostname()=='dena':  #SB's computer
      projectGroup = 'pasta_tutorial'
    else:
      projectGroup = 'research'
    self.be = Backend(projectGroup, initConfig=False)
    self.dirName = self.be.basePath
    self.be.exit(deleteDB=True)
    shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    self.be = Backend(projectGroup, initViews=True, initConfig=False)

    try:
      ### CREATE PROJECTS AND SHOW
      print('*** CREATE PROJECTS AND SHOW ***')
      self.be.addData('x0', {'-name': 'Intermetals at interfaces', \
        'objective': 'Does spray coating lead to intermetalic phase?', 'status': 'active', \
        'comment': '#intermetal #Fe #Al This is a test project'})
      self.be.addData('x0', {'-name': 'Surface evolution in tribology', \
        'objective': 'Why does the surface get rough during tribology?', 'status': 'passive', \
        'comment': '#tribology The answer is obvious'})
      self.be.addData('x0', {'-name': 'Steel', 'objective': 'Test strength of steel', 'status': 'paused', \
        'comment': '#Fe Obvious example without answer'})
      print(self.be.output('x0'))

      ### TEST PROJECT PLANING
      print('*** TEST PROJECT PLANING ***')
      viewProj = self.be.db.getView('viewDocType/x0')
      projID1  = [i['id'] for i in viewProj if i['value'][0]=='Intermetals at interfaces'][0]
      projID2  = [i['id'] for i in viewProj if i['value'][0]=='Steel'][0]

      self.be.changeHierarchy(projID2)
      self.be.addData('x1',    {'comment': 'Random text', '-name': 'Task 1'})
      self.be.addData('x1',    {'-name': 'Task2'})
      self.be.changeHierarchy(None)

      self.be.changeHierarchy(projID1)
      self.be.addData('x1',    {'comment': 'This is hard! #TODO ', '-name': 'Get steel and Al-powder'})
      self.be.addData('x1',    {'comment': 'This will take a long time. #WAIT #_curated', '-name': 'Get spray machine'})
      self.be.changeHierarchy(self.be.currentID)
      self.be.addData('x2',    {'-name': 'Get quotes', 'comment': 'Dont forget company-A #_1 ', 'procedure': 'Guidelines of procurement'})
      self.be.addData('x2',    {'-name': 'Buy machine','comment': 'Delivery time will be 6month #_3 '})
      self.be.changeHierarchy(None)
      self.be.addData('x1',    {'-name': 'SEM images'})
      semStepID = self.be.currentID
      self.be.changeHierarchy(semStepID)
      semDirName = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      self.be.addData('x1',    {'-name': 'Nanoindentation'})
      self.be.changeHierarchy(self.be.currentID)
      indentDirName = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      print(self.be.outputHierarchy())

      ### TEST PROCEDURES
      print('\n*** TEST PROCEDURES ***')
      sopDir = self.dirName/'StandardOperatingProcedures'
      os.makedirs(sopDir)
      with open(sopDir/'Nanoindentation.org','w', encoding='utf-8') as fOut:
        fOut.write('* Put sample in nanoindenter\n* Do indentation\nDo not forget to\n- calibrate tip\n- *calibrate stiffness*\n')
      with open(sopDir/'SEM.md','w', encoding='utf-8') as fOut:
        fOut.write('# Put sample in SEM\n# Do scanning\nDo not forget to\n- contact the pole-piece\n- **USE GLOVES**\n')
      self.be.addData('procedure', {'-name': 'StandardOperatingProcedures/SEM.md', 'comment': '#v1'})
      self.be.addData('procedure', {'-name': 'StandardOperatingProcedures/Nanoindentation.org', 'comment': '#v1'})
      print(self.be.output('procedure'))

      ### TEST SAMPLES
      print('*** TEST SAMPLES ***')
      self.be.addData('sample',    {'-name': 'AlFe cross-section', 'chemistry': 'Al99.9; FeMnCr ', 'qrCode': '13214124 99698708', 'comment': 'after OPS polishing'})
      print(self.be.output('sample'))
      print(self.be.outputQR())

      ###  TEST MEASUREMENTS AND SCANNING/CURATION
      print('*** TEST MEASUREMENTS AND SCANNING/CURATION ***')
      examplePath = Path(__file__).parent/'ExampleMeasurements'
      shutil.copy(examplePath/'Zeiss.tif', semDirName)
      shutil.copy(examplePath/'RobinSteel0000LC.txt', indentDirName)
      shutil.copy(examplePath/'1500nmXX 5 7074 -4594.txt', indentDirName)
      shutil.copy(examplePath/'test.odt', semDirName)
      shutil.copy(examplePath/'story.odt', semDirName)
      self.be.scanProject(projID1)

      ### USE GLOBAL FILES
      print('*** USE GLOBAL FILES ***')
      self.be.changeHierarchy(semStepID)
      self.be.addData('measurement', {'-name': 'https://upload.wikimedia.org/wikipedia/commons/a/a4/Misc_pollen.jpg'})
      print(self.be.output('measurement'))

      ### VERIFY DATABASE INTEGRITY
      print("\n*** VERIFY DATABASE INTEGRITY ***")
      print(self.be.checkDB(verbose=True))

      print('\n*** DONE WITH VERIFY ***')
    except:
      print('ERROR OCCURRED IN VERIFY TESTING\n'+ traceback.format_exc() )
      raise
    return

  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
