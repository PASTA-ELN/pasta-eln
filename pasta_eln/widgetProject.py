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
  def changeProject(self, projID, docID):
    """
    What happens when user clicks to change doc-type

    Args:
      projID (str): document id of project
      docID (str): document id of focus item, if not given focus at project
    """
    for i in reversed(range(self.mainL.count())):
      self.mainL.itemAt(i).widget().setParent(None)
    hierarchy = self.comm.backend.db.getHierarchy(projID)
    for idx, node in enumerate(PreOrderIter(hierarchy)):
      if docID=='' and idx==0:
        label = QLabel('>>> '+node.name+' | '+'/'.join(node.docType)+' | '+node.id)
      elif docID==node.id:
        label = QLabel('>>>   - '*node.depth+node.name+' | '+'/'.join(node.docType)+' | '+node.id)
      else:
        label = QLabel('   - '*node.depth+node.name+' | '+'/'.join(node.docType)+' | '+node.id)
      self.mainL.addWidget(label)
    return
