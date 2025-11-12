from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
                               QHBoxLayout)

from pasta_eln.UI.workflow_creator_dialog.workplan_functions import get_db_samples


class ExportWorkplanDialog(QDialog):
    """
    Dialog after pressing Export in WorkplanCreatorDialog to choose Sample and Filename
    """

    def __init__(self, comm):
        super().__init__()
        self.setWindowTitle("Export Workplan")
        self.setFixedSize(450, 300)

        layout = QVBoxLayout()

        # Dropdown menu
        layout.addWidget(QLabel("Choose a sample:"))
        self.sample = QComboBox()
        self.sample.addItems(get_db_samples(comm))
        layout.addWidget(self.sample)

        # Text input
        layout.addWidget(QLabel("Enter Workplan name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_values(self):
        return self.name_input.text(), self.sample.currentText()
