from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class Head(QWidget):

  def __init__(self, parentLayout, backend):
    super().__init__()
    self.setFixedHeight(60)
    parentLayout.addWidget(self)
    layout = QHBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(20)
    self.setLayout(layout)
    self.backend = backend

    button1 = QPushButton("1a")
    button1.setCheckable(True)
    button1.clicked.connect(self.the_button_was_clicked)
    layout.addWidget(button1)

    button2 = QPushButton("2")
    button2.setCheckable(True)
    button2.clicked.connect(self.the_button_was_clicked)
    layout.addWidget(button2)

  def the_button_was_clicked(self):
    print(self.backend.basePath)

