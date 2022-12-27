from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout

from widgetConfig import Configuration
from style import TextButton, LetterButton, IconButton

class Sidebar(QWidget):

  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    self.setMinimumWidth(200)
    self.setMaximumWidth(200)
    print(self.styleSheet.values)
    self.setStyleSheet("background-color: blue")

    # GUI stuff
    mainLayout = QVBoxLayout()
    mainLayout.setContentsMargins(0,0,0,0)
    mainLayout.setSpacing(20)
    self.setLayout(mainLayout)

    if hasattr(comm.backend, 'dataLabels'):
      # All projects
      mainLayout.addWidget( TextButton('All projects', self.buttonDocTypeClicked, 'x0') )
      # Add other data types
      dTypeWidget = QWidget()
      dTypeLayout = QGridLayout()
      dTypeWidget.setLayout(dTypeLayout)
      for idx, doctype in enumerate(comm.backend.dataLabels):
        button = LetterButton(comm.backend.dataLabels[doctype], self.buttonDocTypeClicked, doctype)
        dTypeLayout.addWidget(button, int(idx/3), idx%3)
      mainLayout.addWidget(dTypeWidget)

      view = comm.backend.db.getView('viewHierarchy/viewHierarchy')
      nativeView = {}
      for item in view:
        if not item['id'].startswith('x-'):
          continue
        nativeView[item['id']] = [item['key']]+item['value']
      for item in nativeView:
        docType = nativeView[item][2][0]
        if docType=='x0':
          button = TextButton(nativeView[item][3], None)  #icon with no text
          mainLayout.addWidget(button)
          # Add other data types
          dTypeWidget = QWidget()
          dTypeLayout = QGridLayout()
          dTypeWidget.setLayout(dTypeLayout)
          for idx, doctype in enumerate(comm.backend.dataLabels):
            button = LetterButton(comm.backend.dataLabels[doctype], self.buttonDocTypeClicked, doctype)
            dTypeLayout.addWidget(button, int(idx/3), idx%3)
          mainLayout.addWidget(dTypeWidget)
        if docType=='x1':
          button = TextButton(nativeView[item][3], None)  #icon with no text
          mainLayout.addWidget(button)

    # Other buttons
    mainLayout.addWidget(IconButton('fa.gear', self.buttonDocTypeClicked, '_configuration_'))

    if not hasattr(comm.backend, 'dataLabels'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()


  def buttonDocTypeClicked(self):
    if self.sender().accessibleName() == '_configuration_':
      print("SHOW CONFIGURATION WINDOW")
      configWindow = Configuration(self.comm.backend, None)
      configWindow.exec()
    else:
      self.comm.chooseDocType.emit(self.sender().accessibleName())
    return

