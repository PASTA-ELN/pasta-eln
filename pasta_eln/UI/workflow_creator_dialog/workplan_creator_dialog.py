import logging

import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout

from .central_widget import CentralWidget
from ..guiCommunicate import Communicate


class WorkplanCreatorDialog(QDialog):
    """
    The Top level Widget of the Workplan Creator Dialog containing only the CentralWidget.
    """

    def __init__(self, comm: Communicate):
        super().__init__()

        self.setWindowTitle("Workplan Creator")

        # Configure Backend / Storage
        self.comm = comm
        self.comm.backendThread.worker.beSendTable.connect(self.onGetData)
        self.docType = 'workflow/procedure'

        self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, True)

        # Central widget
        central_widget = CentralWidget(self.comm)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(central_widget)

        self.setLayout(layout)

    @Slot(pd.DataFrame, str)
    def onGetData(self, data:pd.DataFrame, docType:str) -> None:
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