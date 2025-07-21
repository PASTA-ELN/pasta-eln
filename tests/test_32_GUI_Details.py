from PySide6.QtWidgets import QMainWindow
from pasta_eln.backend import Backend
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.UI.palette import Palette
from pasta_eln.UI.details import Details

def test_simple(qtbot):
  class MainWindow(QMainWindow):
    def __init__(self):
      super().__init__()
      self.backend = Backend('research')
      palette = Palette(self,'none')
      self.comm = Communicate(self.backend, palette)
      widget = Details(self.comm)
      self.setCentralWidget(widget)
      self.docIDs = [i.split('|')[-1].strip() for i in self.backend.output('measurement').split('\n')[-3:]]

  window = MainWindow()
  window.setMinimumSize(600,800)
  window.show()
  qtbot.addWidget(window)

  for i in range(3):
    window.comm.changeDetails.emit(window.docIDs[i])
    path = qtbot.screenshot(window)
    print(path)
