""" widget that shows the table and the details of the items """
import logging
from random import randint
from PySide6.QtCore import Slot                                                     # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QLabel, QScrollArea  # pylint: disable=no-name-in-module
from .widgetTable import Table
from .widgetDetails import Details

class DocTypes(QWidget):
  """ widget that shows the table and the details of the items """
  def __init__(self, comm):
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
  def changeTable(self, docType, projID):
    """
    What happens when user clicks to change doc-type
    -> show table

    Args:
      docType (str): document type
      projID (str): project ID for filtering
    """
    logging.debug('docType:changeTable |'+docType+'|'+projID+'|')
    self.details.hide()
    # if docType=='x0':
    # else:
    #   self.details.show()
    return


  @Slot(str)
  def changeDetails(self, docID):
    """
    What happens when user clicks to change details
    -> show show details

    Args:
      docID (str): document ID
    """
    logging.debug('docType:changeDetails |'+docID+'|')
    if docID!='':
      self.details.show()
    return
