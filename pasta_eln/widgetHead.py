from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class Head(QWidget):

  def __init__(self, backend, cbChangeDoctype):
    super().__init__()
    self.cbChangeDoctype = cbChangeDoctype
    self.setFixedHeight(60)
    layout = QHBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(20)
    self.setLayout(layout)

    # Projects
    button = QPushButton('Projects')
    button.setAccessibleName('x0')
    button.clicked.connect(self.buttonClicked)
    layout.addWidget(button)

    # Add other data types
    for doctype in backend.dataLabels:
      button = QPushButton(backend.dataLabels[doctype])
      button.setAccessibleName(doctype)
      button.clicked.connect(self.buttonClicked)
      layout.addWidget(button)

    # Other buttons
    button = QPushButton('Configuration')
    button.setAccessibleName('_configuration_')
    button.clicked.connect(self.buttonClicked)
    layout.addWidget(button)

  def buttonClicked(self):
    if self.sender().accessibleName() == '_configuration_':
      print("SHOW CONFIGURATION WINDOW")
    else:
      self.cbChangeDoctype(self.sender().accessibleName())
    return

