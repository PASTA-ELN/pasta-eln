#!/usr/bin/python3
"""TEST the form """
import logging, warnings
from pathlib import Path
from pasta_eln.backend_worker.backend import Backend
from pasta_eln.backend_worker.elab_ftw_sync import Pasta2Elab
from .misc import verify, handleReport


def test_simple(qtbot, caplog):
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
  report = sync.sync('gA')
  print()
  handleReport(report, [0,18,0,0,0])

  # verify
  verify(backend)
  projID = backend.db.getView('viewDocType/x0')['id'].values[0]
  backend.changeHierarchy(projID)
  print(backend.outputHierarchy(False, True))

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
