#!/usr/bin/python3
"""TEST the form """
import logging, warnings, random
from pathlib import Path
from PySide6.QtCore import QModelIndex                                  # pylint: disable=no-name-in-module
from pasta_eln.backend import Backend
from pasta_eln.installationTools import exampleData
from pasta_eln.GUI.form import Form
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.GUI.palette import Palette

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
  palette = Palette(None, 'light_blue')
  comm = Communicate(backend, palette)
  window = Form(comm, {'_projectID': '', 'type': ['x0']})
  qtbot.addWidget(window)


  # projID = backend.output('x0').split('|')[-1].strip()
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
