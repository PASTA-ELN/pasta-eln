from PySide6.QtWidgets import QMainWindow
from pasta_eln.backend import Backend
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.UI.palette import Palette
from pasta_eln.UI.project import Project

def test_simple(qtbot):
  class MainWindow(QMainWindow):
    def __init__(self):
      super().__init__()
      self.backend = Backend('research')
      palette = Palette(self,'none')
      comm = Communicate(self.backend, palette)
      widget = Project(comm)
      self.setCentralWidget(widget)
      projID1 = self.backend.output('x0').split('|')[-1].strip()
      comm.changeProject.emit(projID1, '')

  window = MainWindow()
  window.setMinimumSize(1024,800)
  window.show()
  qtbot.addWidget(window)

  path = qtbot.screenshot(window)
  print(path)
  # saved in
  #   /tmp/pytest-of-steffen/pytest-0/test_simple0/
  #   /tmp/pytest-of-runner/pytest-0/test_simple0/screenshot_MainWindow.png
