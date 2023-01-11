""" Central widget: everything that is not sidebar: switches between project-view and table-details """
from PySide6.QtWidgets import QWidget, QVBoxLayout   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module

from .widgetDocTypes import DocTypes
from .widgetProject import Project

class Body(QWidget):
  """ Central widget: everything that is not sidebar: switches between project-view and table-details """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.changeTable)
    comm.changeProject.connect(self.changeProject)
    self.docTypes = DocTypes(comm)
    self.project  = Project(comm)
    self.project.hide()
    mainL = QVBoxLayout()
    mainL.addWidget(self.docTypes)
    mainL.addWidget(self.project)
    self.setLayout(mainL)


  @Slot(str)
  def changeTable(self, docType):
    """
    What happens when user clicks to change doc-type
    -> show table

    Args:
      docType (str): document type
    """
    self.project.hide()
    self.docTypes.show()


  @Slot(str)
  def changeProject(self, docID):
    """
    What happens when user clicks to change project

    Args:
      docID (str): document id
    """
    self.docTypes.hide()
    self.project.show()
