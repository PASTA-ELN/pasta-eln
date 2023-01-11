""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module
from anytree import PreOrderIter

class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeProject.connect(self.changeProject)
    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)


  @Slot(str)
  def changeProject(self, projectID):
    """
    What happens when user clicks to change doc-type

    Args:
      projectID (str): document id of project
    """
    for i in reversed(range(self.mainL.count())):
      self.mainL.itemAt(i).widget().setParent(None)
    hierarchy = self.comm.backend.db.getHierarchy(projectID)
    for node in PreOrderIter(hierarchy):
      label = QLabel('   - '*node.depth+node.name+' | '+'/'.join(node.docType)+' | '+node.id)
      self.mainL.addWidget(label)
