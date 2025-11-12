from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout


class ParamWidget(QWidget):
    """
    The Widget that contains the Parameters and QLineEdits in a StepWidget.
    """

    def __init__(self, param: str, default_value: str = "", value: str = ""):
        super().__init__()
        self.param = param
        # label
        label = QLabel(f"{self.param}:")

        # text-box
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(default_value)
        if value and default_value != value:
            self.line_edit.setText(value)
        elif value:
            self.line_edit.setPlaceholderText(value)

        # layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(label)
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)
