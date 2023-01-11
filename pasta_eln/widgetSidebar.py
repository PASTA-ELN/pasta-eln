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

    # GUI stuff
    mainL = QVBoxLayout()
    mainL.setContentsMargins(0,0,0,0)
    mainL.setSpacing(7)
    self.setLayout(mainL)
    # storage of all projects
    self.widgets = {}
    self.layouts = {}
    self.widgetsHidden = {}


    if hasattr(comm.backend, 'dataLabels'):
      # All projects
      btn = TextButton('All projects', self.buttonDocTypeClicked, 'x0')
      mainL.addWidget(btn)
      # Add other data types
      dTypeW = QWidget()
      dTypeL = QGridLayout(dTypeW)
      dTypeL.setContentsMargins(0,0,0,0)
      for idx, doctype in enumerate(comm.backend.dataLabels):
        button = LetterButton(comm.backend.dataLabels[doctype], self.buttonDocTypeClicked, doctype)
        dTypeL.addWidget(button, int(idx/3), idx%3)
      mainL.addWidget(dTypeW)

      projectIDs = [i['id'] for i in comm.backend.db.getView('viewDocType/x0')]
      currentID  = None
      for projID in projectIDs:
        hierarchy = comm.backend.db.getHierarchy(projID)
        for node in PreOrderIter(hierarchy, maxlevel=2):
          if node.docType[0][0]!='x':
            continue
          if node.docType[0]=='x0':
            button = TextButton(node.name, self.buttonDocTypeClicked, node.id)
            button.setStyleSheet('margin-top: 30')
            mainL.addWidget(button)
            projectW = QWidget()
            projectW.hide()
            projectL = QVBoxLayout(projectW)
            projectL.setContentsMargins(0,0,0,0)
            # Add other data types
            dTypeW = QWidget()
            dTypeL = QGridLayout(dTypeW)
            dTypeL.setContentsMargins(0,0,0,0)
            for idx, doctype in enumerate(comm.backend.dataLabels):
              button = LetterButton(comm.backend.dataLabels[doctype], self.buttonDocTypeClicked, doctype)
              dTypeL.addWidget(button, int(idx/3), idx%3)
            # create widgets
            projectL.addWidget(dTypeW)
            currentID = node.id
            self.widgets[currentID] = projectW
            self.layouts[currentID] = projectL
            self.widgetsHidden[currentID] = True
            mainL.addWidget(projectW)
          if node.docType[0]=='x1':
            button = TextButton(node.name, None)  #icon with no text
            button.setStyleSheet('margin-left: 20')
            self.layouts[currentID].addWidget(button)

    # Other buttons
    mainL.addStretch(1)
    mainL.addWidget(IconButton('fa.gear', self.buttonDocTypeClicked, '_configuration_'))

    if not hasattr(comm.backend, 'dataLabels'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()


  def buttonDocTypeClicked(self):
    """
    What happens when user clicks to change doc-type
    """
    btnName = self.sender().accessibleName()
    print('\nButton', btnName )
    if btnName == '_configuration_':
      print("SHOW CONFIGURATION WINDOW")
      configWindow = Configuration(self.comm.backend, None)
      configWindow.exec()
    elif btnName[1]=='-':
      print("Show project", btnName)
      self.comm.changeProject.emit(btnName)
      if self.widgetsHidden[btnName]: #get button in question
        self.widgets[btnName].show()
        self.widgetsHidden[btnName]=False
      else:
        self.widgets[btnName].hide()
        self.widgetsHidden[btnName]=True
    else:
      print("doctype",btnName)
      self.comm.changeTable.emit(btnName)
    return
