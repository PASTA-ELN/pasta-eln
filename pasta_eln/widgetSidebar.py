from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QToolTip
import qtawesome as qta

from widgetConfig import Configuration

class Sidebar(QWidget):

  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    self.setMinimumWidth(200)

    # GUI stuff
    layout = QVBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(20)
    self.setLayout(layout)

    if hasattr(comm.backend, 'dataLabels'):
      # All projects
      button = QPushButton("All projects")  #icon with no text
      button.setAccessibleName('x0')
      button.clicked.connect(self.buttonClicked)
      layout.addWidget(button)
      # Add other data types
      dTypeWidget = QWidget()
      dTypeLayout = QGridLayout()
      dTypeWidget.setLayout(dTypeLayout)
      for idx, doctype in enumerate(comm.backend.dataLabels):
        button = QPushButton(comm.backend.dataLabels[doctype][0])
        button.setAccessibleName(doctype)
        button.setToolTip(comm.backend.dataLabels[doctype])
        button.clicked.connect(self.buttonClicked)
        dTypeLayout.addWidget(button, int(idx/3), idx%3)
      layout.addWidget(dTypeWidget)

      view = comm.backend.db.getView('viewHierarchy/viewHierarchy')
      nativeView = {}
      for item in view:
        if not item['id'].startswith('x-'):
          continue
        nativeView[item['id']] = [item['key']]+item['value']
      for item in nativeView:
        docType = nativeView[item][2][0]
        if docType=='x0':
          button = QPushButton(nativeView[item][3])  #icon with no text
          layout.addWidget(button)
          # Add other data types
          dTypeWidget = QWidget()
          dTypeLayout = QGridLayout()
          dTypeWidget.setLayout(dTypeLayout)
          for idx, doctype in enumerate(comm.backend.dataLabels):
            button = QPushButton(comm.backend.dataLabels[doctype][0])
            button.setToolTip(comm.backend.dataLabels[doctype])
            dTypeLayout.addWidget(button, int(idx/3), idx%3)
          layout.addWidget(dTypeWidget)
        if docType=='x1':
          button = QPushButton(nativeView[item][3])  #icon with no text
          layout.addWidget(button)

    # Other buttons
    icon = qta.icon('fa.gear', color='blue', scale_factor=1.2)
    button = QPushButton(icon, "")  #icon with no text
    button.setAccessibleName('_configuration_')
    button.clicked.connect(self.buttonClicked)
    layout.addWidget(button)

    if not hasattr(comm.backend, 'dataLabels'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()


  def buttonClicked(self):
    if self.sender().accessibleName() == '_configuration_':
      print("SHOW CONFIGURATION WINDOW")
      configWindow = Configuration(self.backend, None)
      configWindow.exec()
    else:
      self.cbChangeDoctype(self.sender().accessibleName())
    return


  def cbConfigWidget(self):
    print('Callback pressed')

