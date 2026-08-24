import logging
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.details.details import Details
from pasta_eln.ui.details.context import DetailContext, DetailOrigin
from .test_34_GUI_Form import getTable

def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None or comm.backendThread.worker.backend.dbRaw is None:
    qtbot.wait(100)
  window = Details(comm)
  window.setMinimumSize(300, 800)
  window.show()
  qtbot.addWidget(window)

  table = getTable(qtbot, comm, 'measurement')
  docIDs = table['id'].values[:3].tolist()
  print(docIDs)

  for i in range(3):
    window.comm.changeDetails.emit(DetailContext(docIDs[i], origin=DetailOrigin.TABLE))
    qtbot.wait(1000)
    path = qtbot.screenshot(window)
    print(path)

  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
