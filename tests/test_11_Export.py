#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create the default example that all installations create and verify it thoroughly """
import logging, warnings, unittest, tempfile, os
from pathlib import Path
from zipfile import ZipFile
from pasta_eln.backendWorker.backend import Backend
from pasta_eln.backendWorker.inputOutput import exportELN
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
    logging.info('Start test')

    # create .
    configuration, _ = getConfiguration('research')
    self.be = Backend(configuration, 'research')
    projID = self.be.output('x0').split('|')[-2].strip()
    tempDir = tempfile.gettempdir()
    fileName = f'{tempDir}/PASTA.eln'
    allDocTypes = self.be.db.dataHierarchy('','')+['-']
    print(f'Filename {fileName}: docTypes: {", ".join(allDocTypes)}')
    exportELN(self.be, [projID], fileName, allDocTypes)

    # test file
    with ZipFile(fileName, 'r') as zObject:
      zObject.extractall(path=tempDir)
    os.system(f'tree {tempDir}/PASTA')
    print("""
Data on disk:
├── pastaELN.db
├── PastasExampleProject
│   ├── 000_ThisIsAnExampleTask
│   ├── 001_ThisIsAnotherExampleTask
│   │   ├── 000_ThisIsAnExampleSubtask
│   │   ├── 001_ThisIsAnotherExampleSubtask
│   │   └── simple.png
│   └── 002_DataFiles
│       ├── simple.csv
│       ├── simple.png
│       └── story.odt
└── StandardOperatingProcedures
    └── Example_SOP.md
""")

    # try:
    #   os.system(f'code {tempDir}/PASTA/ro-crate-metadata.json')
    # except Exception:
    #   pass
    return


  def tearDown(self):
    logging.info('End test')
    return


if __name__ == '__main__':
  unittest.main()
