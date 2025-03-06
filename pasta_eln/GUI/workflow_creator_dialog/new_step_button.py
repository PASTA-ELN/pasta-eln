from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolButton, QSizePolicy, QMenu

from .common_workflow_description import Storage
from .step_list import StepList
from .workflow_functions import get_db_procedures


class NewStepButton(QToolButton):
    """
    The Button to add a new StepWidget to the current StepList.
    """

    # Depending on Amount of Procedures, the Dropdown Menu could be Exchanged for a dialog
    def __init__(self, parent: StepList, storage: Storage):
        super().__init__(parent)
        self.storage = storage
        self.procedures = get_db_procedures(self.storage)

        # Configure Appearence of Button
        self.setText("Add new Step")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setMinimumSize(QSize(30, 30))

        # Configure Dropdown Menu
        self.menu = QMenu(self)
        for procedure in self.procedures:
            action = QAction(procedure, self)
            action.triggered.connect(lambda checked, name=procedure: parent.add_new_step(name))
            self.menu.addAction(action)
        self.setMenu(self.menu)
