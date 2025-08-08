from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.project import Project

def test_simple(qtbot):

  comm = Communicate('research')
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)
  window = Project(comm)
  window.setMinimumSize(1024,800)
  window.show()

  output = comm.backendThread.worker.backend.output('x0')
  line   = [i for i in output.split('\n') if 'PASTAs Example Project ' in i][0]
  projID = line.split('|')[-2].strip()
  comm.changeProject.emit(projID, '')

  qtbot.addWidget(window)
  while comm.backendThread.worker.backend is None:
    qtbot.wait(100)

  path = qtbot.screenshot(window)
  print(path)
  # saved in
  #   /tmp/pytest-of-steffen/pytest-0/test_simple0/
  #   /tmp/pytest-of-runner/pytest-0/test_simple0/screenshot_MainWindow.png
  comm.shutdownBackendThread()
