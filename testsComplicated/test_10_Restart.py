#!/usr/bin/python3
"""TEST the form """
import shutil, os, platform
import logging, warnings
from pathlib import Path
from pasta_eln.backend import Backend
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
  logging.info('Start 10 test: deterministic process')

  # start app and load project
  backend = Backend('georgTesting')
  dirName = backend.basePath
  backend.exit()
  try:
    shutil.rmtree(dirName)
    os.makedirs(dirName)
    if platform.system()=='Windows':
      print('Try-Except unnecessary')
  except Exception:
    pass
  backend = Backend('georgTesting')
  sync = Pasta2Elab(backend, 'georgTesting', purge=False)
  if not sync.api.url:
    return
  reports = sync.sync('gA')
  print('Reports',reports)

  # verify
  verify(backend)
  return
