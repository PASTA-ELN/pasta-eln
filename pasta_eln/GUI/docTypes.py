""" widget that shows the table and the details of the items """
from typing import Any
from PySide6.QtCore import Slot                                # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout  # pylint: disable=no-name-in-module
from .table import Table
from .details import Details
from ..guiCommunicate import Communicate

class DocTypes(QWidget):
  """ widget that shows the table and the details of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    comm.changeTable.connect(self.changeTable)
    comm.changeDetails.connect(self.changeDetails)
    # GUI elements
    table = Table(comm)
    self.details = Details(comm)
    self.details.resizeEvent = self.resizeWidget # type: ignore
    splitter = QSplitter()
    splitter.setHandleWidth(10)
    splitter.addWidget(table)
    splitter.addWidget(self.details)
    splitter.setContentsMargins(0,0,0,0)
    splitter.setSizes([1,1])
    mainL = QVBoxLayout()
    mainL.setSpacing(0)
    mainL.setContentsMargins(0, 0, 0, 0)
    mainL.addWidget(splitter)
    self.setLayout(mainL)


  @Slot(str, str)                                           # type: ignore[arg-type]
  def changeTable(self,  docType:str, projID:str) -> None:  # pylint: disable=no-unused-argument
    """
    What happens when user clicks to change doc-type
    -> show table

    Args:
      docType (str): document type
      projID (str): project ID for filtering
    """
    self.details.hide()
    return


  @Slot(str)                                                # type: ignore[arg-type]
  def changeDetails(self, docID:str) -> None:
    """
    What happens when user clicks to change details
    -> show show details

    Args:
      docID (str): document ID
    """
    if docID!='':
      self.details.show()
    return


  def resizeWidget(self, _:Any) -> None:
    """ called if splitter resizes details-view  """
    self.details.resizeWidth(self.details.width())
    return
