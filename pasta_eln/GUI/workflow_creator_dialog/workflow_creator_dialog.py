from PySide6.QtWidgets import QDialog, QVBoxLayout

from .central_widget import CentralWidget
from .common_workflow_description import Storage
from ...backend import Backend


class WorkflowCreatorDialog(QDialog):
    """
    The Top level Widget of the Workflow Creator Dialog containing only the CentralWidget.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Workflow Creator")  # + Sample name ?

        # Configure Backend / Storage
        self.backend = Backend()
        self.storage = Storage({})  # Empty Storage gets filled by add_pasta_database below
        self.storage.add_pasta_database(self.backend)

        # Central widget
        central_widget = CentralWidget(self.storage)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(central_widget)

        self.setLayout(layout)
