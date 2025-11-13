import logging

import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QFrame, QGridLayout, QSplitter

from .centerWidgets.centerMainWidget import CenterMainWidget
from .leftWidgets.leftMainWidget import LeftMainWidget
from .rightWidgets.rightMainWidget import RightMainWidget
from ..guiCommunicate import Communicate


class WorkplanCreatorDialog(QDialog):
  """
  The Top level Widget of the Workplan Creator Dialog. Containing the 3 Main Widgets:
  - LeftMainWidget: Displays list and search for choosing procedures
  - CenterMainWidget: Displays information and fill in Sample+Paramaters for chosen procedure
  - RightMainWidget: Displays Workplan and export-button
  """

  def __init__(self, comm: Communicate):
    super().__init__()

    self.setWindowTitle("Workplan Creator")

    # Configure Backend / Storage
    self.comm = comm
    self.docType = 'workflow/procedure'

    self.comm.backendThread.worker.beSendTable.connect(self.onGetData)
    self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, True)

    # Widget that Displays list and search for choosing procedures
    self.leftMainWidget = LeftMainWidget(self.comm)

    # Widget that Displays information and fill in Sample+Paramaters for chosen procedure
    self.centerMainWidget = CenterMainWidget(self.comm)

    # Widget that Displays Workplan and export-button
    self.rightMainWidget = RightMainWidget(self.comm)

    # splitter to resize each column
    self.splitter = QSplitter()
    self.splitter.addWidget(self.leftMainWidget)
    self.splitter.setStretchFactor(0, 1)
    self.splitter.addWidget(self.centerMainWidget)
    self.splitter.setStretchFactor(1, 2)
    self.splitter.addWidget(self.rightMainWidget)
    self.splitter.setStretchFactor(2, 1)

    # layout
    self.layout = QGridLayout()
    self.layout.addWidget(self.splitter, 0, 0)
    self.layout.setContentsMargins(0, 0, 0, 0)
    #self.layout.addWidget(self.leftMainWidget, 0, 0)
    #self.layout.addWidget(self.centerMainWidget, 0, 1)
    #self.layout.addWidget(self.rightMainWidget, 0, 2)
    self.setLayout(self.layout)

  @Slot(pd.DataFrame, str)
  def onGetData(self, data: pd.DataFrame, docType: str) -> None:
    """
    Callback function to handle the received data
    Fills self.comm.storage with Procedures from current Project

    Args:
      data (pd.DataFrame): DataFrame containing table
      docType (str): document type
    """
    logging.debug('got table data %s', docType)
    if docType == self.docType:
      self.comm.storage.add_pasta_database(data, self.comm)
    else:
      print("DEBUG: Workplan Creator got wrong docType")
