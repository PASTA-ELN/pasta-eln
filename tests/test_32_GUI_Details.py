import logging
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.details import Details
from .test_34_GUI_Form import getTable

def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)
  window = Details(comm)
  window.setMinimumSize(1024,800)
  window.show()
  qtbot.addWidget(window)

  table = getTable(qtbot, comm, 'measurement')
  docIDs = table['id'].values[:3].tolist()
  print(docIDs)

  for i in range(3):
    window.comm.changeDetails.emit(docIDs[i])
    qtbot.wait(1000)
    path = qtbot.screenshot(window)
    print(path)

  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
