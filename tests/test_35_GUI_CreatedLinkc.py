import logging
from pathlib import Path
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.details import Details
from pasta_eln.backendWorker.worker import Task
from .test_34_GUI_Form import getTable
from .test_35_GUI_CreatedLinka import LINE

def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  # change file back
  pathExtractor = Path(__file__).parent.parent/'pasta_eln'/'AddOns'/'extractor_tif.py'
  with open(pathExtractor, 'r') as fIn:
    contentOld = fIn.read()
  contentNew = ''
  for line in contentOld.splitlines():
    if line.startswith(LINE):
      line = LINE + '}'
    contentNew += line + '\n'
  with open(pathExtractor, 'w') as fOut:
    fOut.write(contentNew)

  comm.shutdownBackendThread()
  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
