#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create the default example that all installations create and verify it thoroughly """
import logging
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
    logging.info('Start 01 test')

    exampleData(True, None, 'research', '')
    self.be = Backend('research')
    output = self.be.output('x0')
    self.assertEqual(output.split('\n')[0][:129],
                      'name                   | tag       | status | objective                                | comment                             | id')
    self.assertEqual(output.split('\n')[2][:126],
                      'PASTAs Example Project | Important | active | Test if everything is working as inte... | Can be used as reference or deleted |')
    projID = output.split('|')[-1].strip()
    self.be.changeHierarchy(projID)

    output = self.be.outputHierarchy(False, False)
    refOutput = """PASTAs Example Project | x0
  This is an example task | x1
  This is another example task | x1
    This is an example subtask | x1
    This is another example subtask | x1
    simple.png | measurement/image
  Data files | x1
    simple.png | measurement/image
    simple.csv | measurement/csv/linesAndDots
    https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Misc_pollen.jpg/315px-Misc_pollen.jpg | measurement/image
  Big instrument | instrument
  Sensor | instrument/extension
  Example_SOP.md | procedure/markdown
  Example sample | sample
"""
    for line in refOutput.split('\n'):
      self.assertIn(line, output.split('\n'))

    output = self.be.output('procedure')
    self.assertEqual(output.split('\n')[0][:78], 'name           | tag | comment | content                                  | id')
    self.assertEqual(output.split('\n')[2][:59], 'Example_SOP.md | v1  |         | # Put sample in instrument')

    output = self.be.output('sample')
    self.assertEqual(output.split('\n')[0][:101], 'name           | tag | chemistry | comment                                  | qrCode             | id')
    self.assertEqual(output.split('\n')[2][:101], 'Example sample | nan | A2B2C3    | this sample has multiple groups of me... | 13214124, 99698708 | s-')

    output = self.be.output('instrument')
    self.assertEqual(output.split('\n')[0][:81], 'name           | tag | comment                                  | vendor    | id ')
    self.assertIn('Big instrument | nan | Instrument onto which attachments can... | Company A | i-', output)
    self.assertIn('        Sensor | nan | Attachment that increases functionali... | Company B | i-', output)

    output = self.be.output('measurement')
    self.assertEqual(output.split('\n')[0][:179], 'name                                     | tag | comment                                  | type                         | image | sample | procedure                          | id')
    self.assertIn('https://upload.wikimedia.org/wikipedi... |  _3 | - Remote image from wikipedia. Used f... |            measurement/image | True  | nan    | p-', output)
    self.assertIn('simple.csv | nan | # These .csv files use the simple con... | measurement/csv/linesAndDots | True  | nan    |                                nan | m-', output)
    self.assertIn('simple.png | nan | # File with two locations', output)
    self.assertIn(' - The sam... |            measurement/image | True  | nan    |                                nan | m-', output)

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
