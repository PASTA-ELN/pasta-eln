""" Central widget: everything that is not sidebar: switches between project-view and table-details """
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget
from .docTypes import DocTypes
from .guiCommunicate import Communicate
from .project import Project


class Body(QWidget):
  """ Central widget: everything that is not sidebar: switches between project-view and table-details """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.changeTable)
    comm.changeProject.connect(self.changeProject)

    self.docTypes = DocTypes(comm)
    self.project  = Project(comm)
    self.project.hide()
    mainL = QVBoxLayout()
    mainL.setSpacing(0)
    mainL.setContentsMargins(0, 0, 0, 0)
    mainL.addWidget(self.docTypes)
    mainL.addWidget(self.project)
    self.setLayout(mainL)


  @Slot(str)
  def changeTable(self) -> None:
    """
    What happens when user clicks to change doc-type
    -> show table
    """
    self.project.hide()
    self.docTypes.show()
    return


  @Slot(str)
  def changeProject(self) -> None:
    """
    What happens when user clicks to change project
    """
    self.docTypes.hide()
    self.project.show()
    return
