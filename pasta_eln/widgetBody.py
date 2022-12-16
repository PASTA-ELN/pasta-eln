from PySide6.QtWidgets import QWidget, QSplitter, QTextBrowser, QVBoxLayout

class Body(QWidget):

  def __init__(self, parentLayout):
    super().__init__()
    parentLayout.addWidget(self)
    self.table = QTextBrowser(self)
    self.detail = QTextBrowser(self)
    splitter = QSplitter()
    splitter.addWidget(self.table)
    splitter.addWidget(self.detail)

    layoutBody = QVBoxLayout()
    layoutBody.addWidget(splitter)
    self.setLayout(layoutBody)