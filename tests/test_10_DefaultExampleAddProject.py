#!/usr/bin/python3
"""TEST the form """
import logging, warnings, shutil
from pathlib import Path
from PySide6.QtGui import QStandardItem
from pasta_eln.backend import Backend
from pasta_eln.miscTools import DummyProgressBar
from pasta_eln.installationTools import exampleData
from pasta_eln.GUI.form import Form
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.GUI.palette import Palette
from pasta_eln.GUI.project import Project

def test_simple(qtbot):
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
  logging.info('Start 12 test: deterministic process')

  # start app and load project
  exampleData(True, None, 'research', '')
  backend = Backend('research')
  palette = Palette(None, 'dark_blue')
  comm = Communicate(backend, palette)
  window = Form(comm, {'_projectID': '', 'type': ['x0']})
  qtbot.addWidget(window)

  # change project to make it displayable
  projID = backend.output('x0').split('|')[-1].strip()
  doc   = backend.db.getDoc(projID)
  doc['comment'] = '# PASTA-ELN | The favorite ELN for experimental scientists\n - This is an example .eln output for sharing between different ELNs.'
  backend.editData(doc)
  backend.changeHierarchy(projID)
  dirName = backend.basePath/backend.cwd
  shutil.copy(Path(__file__).parent.parent/'pasta_eln'/'Resources'/'Icons'/'pasta512.png', dirName)
  backend.scanProject(DummyProgressBar(), projID)

  # move to top: directly in the database
  cmd = "UPDATE branches SET child='-1' WHERE path=='PastasExampleProject/pasta512.png'"
  backend.db.cursor.execute(cmd)
  backend.db.connection.commit()

  # window.change(projID,'')
    #change to pyside
    #form: create project
    #add folders (2) -> new item (copy from
    #
      # self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['branch'][0]['path'])
      # docID = self.comm.backend.addData(docType, {'name':'new item'}, hierStack)['id']
      # self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['branch'][0]['path'])
      # docID = self.comm.backend.addData(docType, {'name':'new item'}, hierStack)['id']

  verify(backend)
  return

def verify(backend): # Verify DB
  output = backend.checkDB(outputStyle='text')
  print(output)
  output = '\n'.join(output.split('\n')[8:])
  assert '**ERROR' not in output, 'Error in checkDB'
  assert len(output.split('\n')) == 5, 'Check db should have 5 more-less empty lines'
  return
