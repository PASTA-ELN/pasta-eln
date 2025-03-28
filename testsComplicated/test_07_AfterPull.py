#!/usr/bin/python3
"""TEST the form """
import logging, warnings
from pathlib import Path
from pasta_eln.backend import Backend
from pasta_eln.elabFTWsync import Pasta2Elab
from .misc import verify, handleReport

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

  # start app and load project
  backend = Backend('research')
  sync = Pasta2Elab(backend, 'research', purge=False)
  if not sync.api.url:
    return
  # All cases
  print('\nRe-pull: same as before')
  report = sync.sync('gA')
  handleReport(report, [0,14,0,0,0])

  print('Re-push: same as tests 02')
  report = sync.sync('sA')
  handleReport(report, [14,0,0,0,0])

  print('Re-push')
  report = sync.sync('sA')
  handleReport(report, [14,0,0,0,0])

  print('\nRe-pull')
  report = sync.sync('gA')
  handleReport(report, [0,14,0,0,0])

  print('\nRe-pull')
  report = sync.sync('gA')
  handleReport(report, [0,14,0,0,0])

  # verify
  verify(backend)
  return
