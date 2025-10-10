import logging
import pytest
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.details import Details
from pasta_eln.backendWorker.worker import Task
from .test_34_GUI_Form import getTable
from .test_35_GUI_CreatedLinka import LINE

@pytest.mark.timeout(600)
def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  # identify items that change
  tabMeasurements = getTable(qtbot, comm, 'measurement')
  idMeasurement = tabMeasurements[tabMeasurements['name']=='example.tif']['id'].values[0]

  comm.uiRequestTask.emit(Task.EXTRACTOR_RERUN, {'docIDs':[idMeasurement],'recipe':''})

  # should be called general: since not only links
  window = Details(comm)
  window.setMinimumSize(300,800)
  window.show()
  qtbot.addWidget(window)

  window.comm.changeDetails.emit(idMeasurement)
  qtbot.wait(1000)
  while window.metaDetailsL.itemAt(0) is None:
    qtbot.wait(500)
  path = qtbot.screenshot(window)
  print(path)

  window.metaDetailsL.itemAt(0).widget().text() == '<b>Sample</b>: ☍ Example sample'
  comm.shutdownBackendThread()
  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
