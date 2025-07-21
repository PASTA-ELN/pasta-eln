from PySide6.QtWidgets import QMainWindow
from pasta_eln.backend import Backend
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.UI.palette import Palette
from pasta_eln.UI.config import Configuration

def test_simple(qtbot):
  app = QMainWindow()
  backend = Backend('research')
  palette = Palette(app,'none')
  comm = Communicate(backend,palette)
  dialog = Configuration(comm)
  dialog.setMinimumSize(1024,800)
  dialog.show()
  qtbot.addWidget(dialog)
  path = qtbot.screenshot(dialog)
  print(path)
