""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module
from anytree import PreOrderIter

class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.changeTable)


  @Slot(str)
  def changeTable(self, docType):
    """
    What happens when user clicks to change doc-type

    Args:
      docType (str): document type
    """
    table = self.comm.backend.db.getView('viewDocType/x0')
    # print(table[0]['id']) #TODO for now
    hierarchy = self.comm.backend.db.getHierarchy(table[0]['id'])
    mainL = QVBoxLayout()
    for node in PreOrderIter(hierarchy):
      label = QLabel('   - '*node.depth+node.name+' | '+'/'.join(node.docType)+' | '+node.id)
      mainL.addWidget(label)
    self.setLayout(mainL)
