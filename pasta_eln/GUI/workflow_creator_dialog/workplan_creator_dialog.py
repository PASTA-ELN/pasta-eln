from PySide6.QtWidgets import QDialog, QVBoxLayout

from .central_widget import CentralWidget
from .common_workflow_description import Storage
from ...guiCommunicate import Communicate


class WorkplanCreatorDialog(QDialog):
    """
    The Top level Widget of the Workplan Creator Dialog containing only the CentralWidget.
    """

    def __init__(self, comm: Communicate):
        super().__init__()

        self.setWindowTitle("Workplan Creator")

        # Configure Backend / Storage
        self.comm = comm
        self.comm.storage = Storage({})  # Empty Storage gets filled by add_pasta_database below
        self.comm.storage.add_pasta_database(self.comm.backend)

        # Central widget
        central_widget = CentralWidget(self.comm)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(central_widget)

        self.setLayout(layout)
