from PySide6.QtWidgets import QWidget, QSplitter, QTextBrowser, QVBoxLayout

class Body(QWidget):

  def __init__(self, backend):
    super().__init__()
    self.backend = backend
    self.table = QTextBrowser(self)
    self.detail = QTextBrowser(self)
    splitter = QSplitter()
    splitter.setHandleWidth(10)
    splitter.addWidget(self.table)
    splitter.addWidget(self.detail)

    layoutBody = QVBoxLayout()
    layoutBody.addWidget(splitter)
    self.setLayout(layoutBody)

  def cbChangeDoctype(self, docType):
    table = self.backend.output(docType,True)
    self.table.append(table)
    docID = table.split('\n')[2].split('|')[-1].strip()
    doc   = self.backend.db.getDoc(docID)
    self.detail.append(str(doc))
    return