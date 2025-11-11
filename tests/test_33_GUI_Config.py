import logging
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.config.main import Configuration

def test_simple(qtbot, caplog):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  dialog = Configuration(comm)
  dialog.setMinimumSize(1024,800)
  dialog.show()
  qtbot.addWidget(dialog)
  qtbot.wait(1000)
  path = qtbot.screenshot(dialog)
  print(path)

  comm.shutdownBackendThread()

  errors = [record for record in caplog.records if record.levelno >= logging.ERROR]
  assert not errors, f"Logging errors found: {[record.getMessage() for record in errors]}"
