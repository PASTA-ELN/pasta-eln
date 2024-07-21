#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create 3 projects; simplified form of testTutorialComplex """
import os, shutil, traceback, logging
from datetime import datetime
import warnings
import unittest
from pathlib import Path
import pytest
from pasta_eln.backend import Backend
from pasta_eln.miscTools import outputString
from pasta_eln.miscTools import DummyProgressBar

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
    #TODO check if test successful
    dummyProgressBar = DummyProgressBar()
    outputFormat = 'print'
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
    logging.info('Start 3Projects test')

    projectGroup = 'research'
    self.be = Backend('research', initConfig=False)
    self.dirName = self.be.basePath
    self.be.exit(deleteDB=True)
    shutil.rmtree(self.dirName)
    os.makedirs(self.dirName)
    self.be = Backend(projectGroup, initViews=True, initConfig=False)

    try:
      ### CREATE PROJECTS AND SHOW
      outputString(outputFormat,'h2','CREATE PROJECTS AND SHOW')
      self.be.addData('x0', {'name': 'Intermetals at interfaces', \
        '.objective': 'Does spray coating lead to intermetalic phase?', '.status': 'active', \
        'comment': '#intermetal #Fe #Al This is a test project'})
      self.be.addData('x0', {'name': 'Surface evolution in tribology', \
        '.objective': 'Why does the surface get rough during tribology?', '.status': 'passive', \
        'comment': '#tribology The answer is obvious'})
      self.be.addData('x0', {'name': 'Steel', '.objective': 'Test strength of steel', '.status': 'paused', \
        'comment': '#Fe Obvious example without answer'})
      outputString(outputFormat, 'info', self.be.output('x0'))

      ### TEST PROJECT PLANING
      outputString(outputFormat,'h2','TEST PROJECT PLANING')
      dfProj  = self.be.db.getView('viewDocType/x0')
      projID1 = list(dfProj[dfProj['name']=='Intermetals at interfaces']['id'])[0]
      projID2 = list(dfProj[dfProj['name']=='Steel']['id'])[0]

      self.be.changeHierarchy(projID2)
      self.be.addData('x1',    {'comment': 'Random text', 'name': 'Task 1'})
      self.be.addData('x1',    {'name': 'Task2'})
      self.be.changeHierarchy(None)

      self.be.changeHierarchy(projID1)
      self.be.addData('x1',    {'comment': 'This is hard! #TODO ', 'name': 'Get steel and Al-powder'})
      currentID = self.be.addData('x1',    {'comment': 'This will take a long time. #WAIT #_curated', 'name': 'Get spray machine'})
      self.be.changeHierarchy(currentID)
      self.be.addData('x2',    {'name': 'Get quotes', 'comment': 'Dont forget company-A #_1 '})
      self.be.addData('x2',    {'name': 'Buy machine','comment': 'Delivery time will be 6month #_3 '})
      self.be.changeHierarchy(None)
      semStepID = self.be.addData('x1',    {'name': 'SEM images'})
      self.be.changeHierarchy(semStepID)
      semDirName = self.be.basePath/self.be.cwd
      self.be.changeHierarchy(None)
      currentID = self.be.addData('x1',    {'name': 'Nanoindentation'})
      outputString(outputFormat,'info',self.be.outputHierarchy())

      ### TEST PROCEDURES
      outputString(outputFormat,'h2','TEST PROCEDURES')
      sopDir = self.dirName/'StandardOperatingProcedures'
      os.makedirs(sopDir)
      with open(sopDir/'Nanoindentation.md','w', encoding='utf-8') as fOut:
        fOut.write('# Put sample in nanoindenter\n# Do indentation\nDo not forget to\n- calibrate tip\n- *calibrate stiffness*\n')
      with open(sopDir/'SEM.md','w', encoding='utf-8') as fOut:
        fOut.write('# Put sample in SEM\n# Do scanning\nDo not forget to\n- contact the pole-piece\n- **USE GLOVES**\n')
      self.be.addData('procedure', {'name': 'StandardOperatingProcedures/SEM.md', 'comment': '#v1'})
      self.be.addData('procedure', {'name': 'StandardOperatingProcedures/Nanoindentation.md', 'comment': '#v1'})
      outputString(outputFormat,'info',self.be.output('procedure'))
      output = self.be.output('procedure',True)
      idSEM = None
      for line in output.split('\n'):
        if 'SEM' in line:
          idSEM = line.split('|')[-1].strip()

      ### TEST SAMPLES
      outputString(outputFormat,'h2','TEST SAMPLES')
      self.be.addData('sample',    {'name': 'AlFe cross-section', '.chemistry': 'Al99.9; FeMnCr ', 'qrCode': '13214124 99698708', 'comment': 'after OPS polishing',
                                    'geometry.height':4, 'geometry.width':2, 'weight.initial':6})
      outputString(outputFormat,'info',self.be.output('sample'))
      outputString(outputFormat,'info',self.be.outputQR())

      ###  TEST MEASUREMENTS AND SCANNING
      outputString(outputFormat,'h2','TEST MEASUREMENTS AND SCANNING')
      examplePath = Path(__file__).parent.parent/'pasta_eln'/'Resources'/'ExampleMeasurements'
      shutil.copy(examplePath/'simple.png', semDirName)
      shutil.copy(examplePath/'simple.csv', semDirName)
      shutil.copy(examplePath/'story.odt',  semDirName)
      progressBar = DummyProgressBar()
      self.be.scanProject(progressBar, projID1)

      ### USE GLOBAL FILES
      outputString(outputFormat,'h2','USE GLOBAL FILES')
      self.be.changeHierarchy(semStepID)
      self.be.addData('measurement', {'name': 'https://upload.wikimedia.org/wikipedia/commons/a/a4/Misc_pollen.jpg', '.procedure':idSEM})
      outputString(outputFormat,'info',self.be.output('measurement'))

      ### ADD INSTRUMENTS AND THEIR ATTACHMENTS
      outputString(outputFormat,'h2','ADD INSTRUMENTS AND ATTACHMENTS')
      self.be.addData('instrument', {'name': 'G200X', '.vendor':'KLA', '.model':'KLA G200X'})
      self.be.addData('instrument/extension', {'name': 'B1', '.vendor':'Synthon', '.model':'Berkovich tip'})
      output = self.be.output('instrument',True)
      idKLA, idSynthon = None, None
      for line in output.split('\n'):
        if 'KLA' in line:
          idKLA = line.split('|')[-1].strip()
        if 'Synthon'  in line:
          idSynthon = line.split('|')[-1].strip()
      self.be.db.initAttachment(idKLA, "Right side of instrument", 'instrument/extension')
      self.be.db.addAttachment(idKLA, "Right side of instrument",
        {'date':datetime.now().isoformat(),'remark':'Worked well','docID':idSynthon,'user':'nobody'})
      self.be.db.addAttachment(idKLA, "Right side of instrument",
        {'date':datetime.now().isoformat(),'remark':'Service','docID':'','user':'nobody'})
      outputString(outputFormat,'info',self.be.output('instrument'))


      ### VERIFY DATABASE INTEGRITY
      outputString(outputFormat,'h2','VERIFY DATABASE INTEGRITY')
      outputString(outputFormat,'info', self.be.checkDB(outputStyle='text'))
      outputString(outputFormat,'h2','DONE WITH VERIFY')
    except:
      outputString(outputFormat,'h2','ERROR OCCURRED IN VERIFY TESTING\n'+ traceback.format_exc() )
      raise
    return

  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
