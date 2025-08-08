from PySide6.QtWidgets import QMainWindow
from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.details import Details

def test_simple(qtbot):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)
  window = Details(comm)
  window.setMinimumSize(1024,800)
  window.show()

  docIDs = [i.split('|')[-1].strip() for i in comm.backendThread.worker.backend.output('measurement').split('\n')[-3:]]

  qtbot.addWidget(window)
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  for i in range(3):
    window.comm.changeDetails.emit(docIDs[i])
    path = qtbot.screenshot(window)
    print(path)

  comm.shutdownBackendThread()
