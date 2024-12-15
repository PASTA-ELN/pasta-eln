from PySide6.QtWidgets import QMainWindow
from pasta_eln.backend import Backend
from pasta_eln.guiCommunicate import Communicate
from pasta_eln.GUI.palette import Palette
from pasta_eln.GUI.form import Form

def test_simple(qtbot):
  app = QMainWindow()
  backend = Backend('research')
  palette = Palette(app,'none')
  comm = Communicate(backend,palette)
  df = backend.db.getView('viewDocType/measurement')
  docID = df[df['name']=='simple.png']['id'].values[0]
  doc = backend.db.getDoc(docID)
  dialog = Form(comm, doc)
  dialog.setMinimumSize(1024,800)
  dialog.show()
  qtbot.addWidget(dialog)
  path = qtbot.screenshot(dialog)
  print(path)
