#!/usr/bin/python3
import logging, warnings, os, shutil
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.GUI.project import Project
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.GUI.palette import Palette
from pasta_eln.inputOutput import importELN

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
  logging.info('Start 03 test')

  # start app and load project
  backend = Backend('research')
  palette = Palette(None, 'light_blue')
  comm = Communicate(backend, palette)
  window = Project(comm)
  qtbot.addWidget(window)

  # remove old and recreate empty
  dirName = backend.basePath
  backend.exit()
  try:
    shutil.rmtree(dirName)
    os.makedirs(dirName)
  except Exception:
    pass
  backend = Backend('research')

  for eln in os.listdir('tests/importELNs'):
    print(f'\nStart with {eln}')
    projName = f'{eln[:-4]} Import'
    backend.addData('x0', {'name': projName})
    df = backend.db.getView('viewDocType/x0')
    projID = df[df['name']==projName]['id'].values[0]
    reply = importELN(backend, f'tests/importELNs/{eln}', projID)
    print(reply)
    #statistics type File can be larger than num.Files because there are remote files which are not Files but in the @type

  return
