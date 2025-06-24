#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create the default example that all installations create and verify it thoroughly """
import logging, warnings, unittest, tempfile, os
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.AddOns.project_importCSV import main


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
    logging.info('Start test')

    # create .eln
    self.be = Backend('research')
    projID = self.be.output('x0').split('|')[-1].strip()
    self.be.changeHierarchy(projID)

    folderID = [i for i in self.be.outputHierarchy(True, True).split('\n') if 'This is an example task' in i][0]
    folderID = folderID.split('|')[-1].strip()
    self.be.changeHierarchy(folderID)
    main(self.be, '/'.join(self.be.hierStack), None, {'fileNames':['tests/inputSamples.csv']})

    self.verify()
    self.be.changeHierarchy(None)
    output = self.be.outputHierarchy(False)
    print(output)
    self.assertIn('sample A | sample', output, 'Sample A incorrect')
    self.assertIn('sample B | sample', output, 'Sample B incorrect')
    self.assertIn('sample C | sample', output, 'Sample C incorrect')
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
    logging.info('End test')
    return


if __name__ == '__main__':
  unittest.main()
