import logging
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.project.project import Project
from .test_34_GUI_Form import getTable
from .helpers import waitForBackend

def test_simple(qtbot, caplog):

  comm = Communicate('research')
  waitForBackend(qtbot, comm)
  window = Project(comm)
  window.setMinimumSize(1024,800)
  window.show()

  df = getTable(qtbot, comm, 'x0')
  projID = df[df['name']=='PASTAs Example Project']['id'].values[0]
  comm.changeProject.emit(projID, '')
  qtbot.addWidget(window)
  qtbot.wait(1000)

  path = qtbot.screenshot(window)
  print(path)
  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
