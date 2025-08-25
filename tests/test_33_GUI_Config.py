from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.config.main import Configuration

def test_simple(qtbot):

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
