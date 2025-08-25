from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.details import Details
from .test_34_GUI_Form import getTable

def test_simple(qtbot):

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
