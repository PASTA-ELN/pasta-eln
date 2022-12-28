""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module

class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.chooseDocType.connect(self.changeDoctype)


  @Slot(str)
  def changeDoctype(self, docType):
    """
    What happens when user clicks to change doc-type

    Args:
      docType (str): document type
    """
    table = self.comm.backend.db.getView('viewDocType/x0')
    # print(table[0]['id']) #TODO for now
    hierarchy = self.comm.backend.db.getView('viewHierarchy/viewHierarchy', startKey=table[0]['id'])
    mainL = QVBoxLayout()
    for item in hierarchy:
      label = QLabel(str(item['value']))
      mainL.addWidget(label)
    self.setLayout(mainL)
