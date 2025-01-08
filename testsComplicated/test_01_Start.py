#!/usr/bin/python3
"""TEST the form """
import logging, warnings
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.installationTools import exampleData
from pasta_eln.GUI.form import Form
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.GUI.palette import Palette
from pasta_eln.elabFTWsync import Pasta2Elab
from .misc import verify

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
  _ = Pasta2Elab(backend, 'research', purge=True)
  verify(backend)
  return
