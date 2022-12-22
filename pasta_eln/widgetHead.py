from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
import qtawesome as qta

from widgetConfig import Configuration

class Head(QWidget):

  def __init__(self, backend, cbChangeDoctype):
    super().__init__()
    self.backend = backend
    self.cbChangeDoctype = cbChangeDoctype

    # GUI stuff
    self.setFixedHeight(60)
    layout = QHBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(20)
    self.setLayout(layout)

    # Projects
    icon = qta.icon('fa5s.home', color='blue', scale_factor=1.2)
    button = QPushButton(icon, "")  #icon with no text
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
    icon = qta.icon('fa.gear', color='blue', scale_factor=1.2)
    button = QPushButton(icon, "")  #icon with no text
    button.setAccessibleName('_configuration_')
    button.clicked.connect(self.buttonClicked)
    layout.addWidget(button)


  def buttonClicked(self):
    if self.sender().accessibleName() == '_configuration_':
      print("SHOW CONFIGURATION WINDOW")
      configWindow = Configuration(self.backend, self.cbConfigWidget)
      configWindow.exec()
    else:
      self.cbChangeDoctype(self.sender().accessibleName())
    return

  def cbConfigWidget(self):
    print('Callback pressed')

