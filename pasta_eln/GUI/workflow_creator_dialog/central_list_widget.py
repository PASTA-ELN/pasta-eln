from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QSizePolicy, QScrollArea, QPushButton, QVBoxLayout, QMessageBox, QInputDialog, \
    QDialog

from .central_text_widget import CentralTextWidget
from .export_workplan_dialog import ExportWorkplanDialog
from .new_step_button import NewStepButton
from .step_list import StepList
from .workflow_functions import generate_workflow
from ...guiCommunicate import Communicate


class CentralListWidget(QWidget):
    """
    The Widget on the left that displays the StepList and buttons to show/create the Workflow.
    """

    def __init__(self, comm: Communicate, textfield: CentralTextWidget):
        super().__init__()
        self.comm = comm
        self.storage = self.comm.storage
        self.textfield = textfield

        self.setFixedWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # step list
        self.step_list = StepList(self.comm, self.textfield)

        # scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.step_list)

        # New Step Button
        new_step_button = NewStepButton(self.step_list, self.comm)

        # Font for the buttons
        font = QFont()
        font.setPointSize(16)
        new_step_button.setFont(font)

        # export button
        export_button = QPushButton("Save / Export Workflow")
        export_button.clicked.connect(self.export_button_pressed)
        export_button.setFont(font)

        # layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(new_step_button)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(export_button)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(self.layout)

    def export_button_pressed(self):
        library_url = "https://raw.githubusercontent.com/SteffenBrinckmann/common-workflow-description_Procedures/main"
        procedures = self.step_list.get_procedures()
        parameters = self.step_list.get_parameters()
        docType = "workflow/workplan"
        export_dialog = ExportWorkplanDialog(self.comm)
        if export_dialog.exec() == QDialog.DialogCode.Accepted:
            user_input_name, sample_name = export_dialog.get_values()
        else:
            return
        if user_input_name.endswith(".py"):
            workflow_name = user_input_name
        else:
            workflow_name = user_input_name+".py"

        if not procedures:
            QMessageBox.warning(self.step_list,
                                "Export Failed",
                                "Cannot Export Workflow without Procedures")
        else:
            generate_workflow(self.comm, workflow_name, library_url, sample_name, procedures, parameters, docType)
            QMessageBox.information(self.step_list, "Export Successful", "Export Successful")
