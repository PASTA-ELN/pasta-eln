from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot

from widgetDocTypes import DocTypes
from widgetProject import Project

class Body(QWidget):
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.chooseDocType.connect(self.changeDoctype)
    self.docTypes = DocTypes(comm)
    self.project  = Project(comm)
    self.project.hide()
    mainL = QVBoxLayout()
    mainL.addWidget(self.docTypes)
    mainL.addWidget(self.project)
    self.setLayout(mainL)

  @Slot(str)
  def changeDoctype(self, docType):
    if docType=='x0':
      self.docTypes.hide()
      self.project.show()
    else:
      self.project.hide()
      self.docTypes.show()
