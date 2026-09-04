#!/usr/bin/python3
"""TEST using the FULL set of python-requirements: create the default example that all installations create and verify it thoroughly """
import logging, unittest, tempfile, os
from zipfile import ZipFile
from pasta_eln.backend_worker.backend import Backend
from pasta_eln.backend_worker.input_output import exportELN


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
    logging.info('Start test')

    log_records = []
    class ErrorHandler(logging.Handler):
      def emit(self, record):
        if record.levelno >= logging.ERROR:
          log_records.append(record)
    handler = ErrorHandler()
    logging.getLogger().addHandler(handler)

    # create .
    self.be = Backend('research')
    projID = self.be.output('x0').split('\n')
    projID = [x for x in projID if 'PASTAs Example Project' in x]
    projID = projID[0].split('|')[-2].strip()
    tempDir = tempfile.gettempdir()
    fileName = f'{tempDir}/PASTA_ELN.eln'
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
└── CommonFiles
    └── Example_SOP.md
""")

    logging.getLogger().removeHandler(handler)
    self.assertEqual(len(log_records), 0, f"Logging errors found: {[r.getMessage() for r in log_records]}")
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
