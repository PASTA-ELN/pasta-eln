from PySide6.QtWidgets import QWidget, QSizePolicy, QTextEdit, QVBoxLayout


class CentralTextWidget(QWidget):
    """
    The Widget on the right that displays the text describing the selected procedure.
    """

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # text edit field
        self.textedit = QTextEdit()
        self.textedit.setReadOnly(True)  # Could be Changed later for comments

        # layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textedit)

        self.setLayout(self.layout)
