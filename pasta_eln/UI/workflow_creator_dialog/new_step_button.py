from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolButton, QSizePolicy, QMenu

from .step_list import StepList
from .workplan_functions import get_db_procedures
from ..guiCommunicate import Communicate


class NewStepButton(QToolButton):
    """
    The Button to add a new StepWidget to the current StepList.
    """

    # Depending on Amount of Procedures, the Dropdown Menu could be Exchanged for a dialog
    def __init__(self, comm: Communicate):
        super().__init__()
        self.comm = comm
        self.storage = self.comm.storage
        self.procedures = []
        self.menu = QMenu(self)
        self.comm.proceduresChanged.connect(self.update_dropdownmenu)

        # Configure Appearence of Button
        self.setText("Add new Step")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setMinimumSize(QSize(30, 30))

    def update_dropdownmenu(self):
        self.procedures = get_db_procedures(self.comm)
        self.menu.clear()
        for procedure in self.procedures:
            action = QAction(procedure, self)
            action.triggered.connect(lambda checked, name=procedure: self.parentWidget().step_list.add_new_step(name))
            self.menu.addAction(action)
        self.setMenu(self.menu)
