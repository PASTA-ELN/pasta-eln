from PySide6.QtWidgets import QWidget, QGridLayout

from .central_list_widget import CentralListWidget
from .central_text_widget import CentralTextWidget


class CentralWidget(QWidget):
    """
    The central widget of the application. Containing a CentralListWidget (left) and a CentralTextWidget (right).
    """

    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.sample_name = "TODO"  # TODO

        # Widget that displays text of procedures
        self.central_text_widget = CentralTextWidget()

        # Widget that contains the Steplist
        self.central_list_widget = CentralListWidget(self.storage, self.central_text_widget)

        # layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.central_list_widget, 0, 0)
        self.layout.addWidget(self.central_text_widget, 0, 1)

        self.setLayout(self.layout)
