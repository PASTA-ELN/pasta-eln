from PySide6.QtWidgets import QWidget, QSplitter, QTextBrowser, QVBoxLayout
from PySide6.QtCore import Slot

class Body(QWidget):

  def __init__(self, comm):
    super().__init__()
    self.backend = comm.backend
    comm.chooseDocType.connect(self.changeDoctype)

    # GUI stuff
    self.table = QTextBrowser(self)
    self.detail = QTextBrowser(self)
    splitter = QSplitter()
    splitter.setHandleWidth(10)
    splitter.addWidget(self.table)
    splitter.addWidget(self.detail)
    mainLayout = QVBoxLayout()
    mainLayout.addWidget(splitter)
    self.setLayout(mainLayout)

  @Slot(str)
  def changeDoctype(self, docType):
    table = self.backend.output(docType,True)
    self.table.append(table)
    docID = table.split('\n')[2].split('|')[-1].strip()
    doc   = self.backend.db.getDoc(docID)
    self.detail.append(str(doc))
    return