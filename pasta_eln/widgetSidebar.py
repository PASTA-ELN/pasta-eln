""" Sidebar widget that includes the navigation items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout    # pylint: disable=no-name-in-module
from anytree import PreOrderIter

from .widgetConfig import Configuration
from .style import TextButton, LetterButton, IconButton

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    self.setMinimumWidth(200)
    self.setMaximumWidth(200)
    # print(self.styleSheet.values)
    self.setStyleSheet("background-color: red")

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

      projectIDs = [i['id'] for i in comm.backend.db.getView('viewDocType/x0')]
      for projID in projectIDs:
        hierarchy = comm.backend.db.getHierarchy(projID)
        for node in PreOrderIter(hierarchy, maxlevel=2):
          if node.docType[0][0]!='x':
            continue
          if node.docType[0]=='x0':
            button = TextButton(node.name, None)  #icon with no text
            mainLayout.addWidget(button)
            # Add other data types
            dTypeWidget = QWidget()
            dTypeLayout = QGridLayout()
            dTypeWidget.setLayout(dTypeLayout)
            for idx, doctype in enumerate(comm.backend.dataLabels):
              button = LetterButton(comm.backend.dataLabels[doctype], self.buttonDocTypeClicked, doctype)
              dTypeLayout.addWidget(button, int(idx/3), idx%3)
            mainLayout.addWidget(dTypeWidget)
          if node.docType[0]=='x1':
            button = TextButton(node.name, None)  #icon with no text
            mainLayout.addWidget(button)

    # Other buttons
    mainLayout.addWidget(IconButton('fa.gear', self.buttonDocTypeClicked, '_configuration_'))

    if not hasattr(comm.backend, 'dataLabels'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()


  def buttonDocTypeClicked(self):
    """
    What happens when user clicks to change doc-type
    """
    if self.sender().accessibleName() == '_configuration_':
      print("SHOW CONFIGURATION WINDOW")
      configWindow = Configuration(self.comm.backend, None)
      configWindow.exec()
    else:
      self.comm.chooseDocType.emit(self.sender().accessibleName())
    return
