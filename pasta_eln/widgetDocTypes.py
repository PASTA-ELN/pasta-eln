""" widget that shows the table and the details of the items """
import logging
from random import randint
from PySide6.QtCore import Slot                                                     # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QLabel, QScrollArea  # pylint: disable=no-name-in-module
from .widgetTable import Table
from .widgetDetails import Details
from .communicate import Communicate

class DocTypes(QWidget):
  """ widget that shows the table and the details of the items """
  def __init__(self, comm:Communicate):
    super().__init__()
    comm.changeTable.connect(self.changeTable)
    comm.changeDetails.connect(self.changeDetails)

    # GUI elements
    table = Table(comm)
    self.details = Details(comm)
    splitter = QSplitter()
    splitter.setHandleWidth(10)
    splitter.addWidget(table)
    splitter.addWidget(self.details)
    splitter.setSizes([1,1])
    mainLayout = QVBoxLayout()
    mainLayout.addWidget(splitter)
    self.setLayout(mainLayout)


  @Slot(str, str)
  def changeTable(self, docType:str, projID:str) -> None:
    """
    What happens when user clicks to change doc-type
    -> show table

    Args:
      docType (str): document type
      projID (str): project ID for filtering
    """
    self.details.hide()
    return


  @Slot(str)
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
