#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create the default example that all installations create and verify it thoroughly """
import logging, warnings, unittest, tempfile, os
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.AddOns.project_html_report import main

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
    tempDir = tempfile.gettempdir()
    fileName = f'{tempDir}/temp.html'
    print(f'Filename {fileName}')
    main(self.be, projID, None, {'fileNames':[fileName]})

    # test file
    try:
      os.system(f'google-chrome {fileName}')
    except Exception:
      pass
    return


  def tearDown(self):
    logging.info('End test')
    return

if __name__ == '__main__':
  unittest.main()
