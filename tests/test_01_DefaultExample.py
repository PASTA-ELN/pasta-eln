#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create the default example that all installations create and verify it thoroughly """
import logging
import warnings
import unittest
from pathlib import Path
from pasta_eln.backendWorker.backend import Backend
from pasta_eln.miscTools import DummyProgressBar, getConfiguration
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
    logging.info('Start 01 test')

    configuration, _ = getConfiguration('research')
    exampleData(True, None, 'research', '')
    self.be = Backend(configuration, 'research')
    output = self.be.output('x0')
    self.assertEqual(output.split('\n')[0][:129],
                      'name                   | tags      | status | objective                                | comment                             | id')
    self.assertEqual(output.split('\n')[2][:126],
                      'PASTAs Example Project | Important | active | Test if everything is working as inte... | Can be used as reference or deleted |')
    projID = output.split('|')[-2].strip()
    self.be.changeHierarchy(projID)

    output = self.be.outputHierarchy(False, False)
    refOutput = """PASTAs Example Project | x0
  This is an example task | x1
  This is another example task | x1
    This is an example subtask | x1
    This is another example subtask | x1
    simple.png | measurement/image
  Data files | x1
    story.odt | -
    simple.png | measurement/image
    example.tif | measurement/image
    https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Misc_pollen.jpg/315px-Misc_pollen.jpg | measurement/image
    simple.csv | measurement/csv/linesAndDots
  procedure.md | workflow/procedure/markdown
  workplan.py | workflow/workplan
  Example_SOP.md | workflow/procedure/markdown
  worklog.log | workflow/worklog
"""
    for line in refOutput.split('\n'):
      self.assertIn(line, output.split('\n'))

    output = self.be.output('workflow')
    self.assertIn('name           | tags | comment | id', output)
    self.assertIn('Example_SOP.md |  v1  |         |'   , output)
    self.assertIn('procedure.md | nan  |', output)
    self.assertIn('workplan.py | nan  |', output)
    self.assertIn('worklog.log | nan  |', output)

    output = self.be.output('sample')
    self.assertEqual(output.split('\n')[0][:102], 'name           | tags | chemistry | comment                                  | qrCodes            | id')
    self.assertEqual(output.split('\n')[2][:102], 'Example sample | nan  | A2B2C3    | this sample has multiple groups of me... | 13214124, 99698708 | s-')

    output = self.be.output('instrument')
    self.assertEqual(output.split('\n')[0][:82], 'name           | tags | comment                                  | vendor    | id ')
    self.assertIn('Big instrument | nan  | Instrument onto which attachments can... | Company A | i-', output)
    self.assertIn('        Sensor | nan  | Attachment that increases functionali... | Company B | i-', output)

    output = self.be.output('measurement')
    self.assertIn('https://upload.wikimedia.org/wikipedi... |  _3  | - Remote image from wikipedia. Used f... |            measurement/image | Y     | nan    ', output)
    self.assertIn('simple.csv | nan  | # These .csv files use the simple con... | measurement/csv/linesAndDots | Y     | nan    |                                nan | m-', output)
    self.assertIn('simple.png | nan  | # File with two locations', output)
    self.assertIn('- The sam... |            measurement/image | Y     | nan    |                                nan | m-', output)

    #Verify DB
    output = self.be.checkDB(outputStyle='text')
    output = '\n'.join(output.split('\n')[8:])
    self.assertNotIn('**ERROR', output, 'Error in checkDB')
    self.assertEqual(len(output.split('\n')), 6, 'Check db should have 6 more-less empty lines')
    return


  def tearDown(self):
    logging.info('End 3Projects test')
    return

if __name__ == '__main__':
  unittest.main()
