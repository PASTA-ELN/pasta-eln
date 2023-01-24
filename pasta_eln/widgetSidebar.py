""" Sidebar widget that includes the navigation items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout    # pylint: disable=no-name-in-module
from anytree import PreOrderIter

from .dialogConfig import Configuration
from .style import TextButton, LetterButton, IconButton

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    width = self.comm.backend.configuration['GUI']['sidebarWidth']
    self.setMinimumWidth(width)
    self.setMaximumWidth(width)

    # GUI elements
    mainL = QVBoxLayout()
    mainL.setContentsMargins(0,0,0,0)
    mainL.setSpacing(7)
    self.setLayout(mainL)
    # storage of all projects
    self.widgets = {}
    self.layouts = {}
    self.widgetsHidden = {}

    if hasattr(comm.backend.db, 'dataLabels'):
      # All projects
      TextButton('All projects', self.btnDocType, mainL, 'x0/')
      # Add other data types
      dTypeW = QWidget()
      dTypeL = QGridLayout(dTypeW)
      dTypeL.setContentsMargins(0,0,0,0)
      for idx, doctype in enumerate(comm.backend.db.dataLabels):
        if doctype[0]!='x':
          button = LetterButton(comm.backend.db.dataLabels[doctype], self.btnDocType, None, doctype+'/')
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
            button = TextButton(node.name, self.btnProject, mainL, node.id+'/', style='margin-top: 30')
            projectW = QWidget()
            projectW.hide()
            projectL = QVBoxLayout(projectW)
            projectL.setContentsMargins(0,0,0,0)
            currentID = node.id
            # Add other data types
            dTypeW = QWidget()
            dTypeL = QGridLayout(dTypeW)
            dTypeL.setContentsMargins(0,0,0,0)
            for idx, doctype in enumerate(comm.backend.db.dataLabels):
              if doctype[0]!='x':
                button = LetterButton(comm.backend.db.dataLabels[doctype], self.btnDocType, None, doctype+'/'+currentID)
                dTypeL.addWidget(button, int(idx/3), idx%3)
            # create widgets
            projectL.addWidget(dTypeW)
            self.widgets[currentID] = projectW
            self.layouts[currentID] = projectL
            self.widgetsHidden[currentID] = True
            mainL.addWidget(projectW)
          if node.docType[0]=='x1':
            button = TextButton(node.name, self.btnProject, self.layouts[currentID], currentID+'/'+node.id, \
                                style='margin-left: 20')

    # Other buttons
    mainL.addStretch(1)
    IconButton('fa.gear', self.btnConfig, mainL, backend=self.comm.backend)
    if not hasattr(comm.backend.db, 'dataLabels'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()


  def btnConfig(self):
    """
    What happens when user clicks to use configuration
    """
    configWindow = Configuration(self.comm.backend, None)
    configWindow.exec()
    return


  def btnDocType(self):
    """
    What happens when user clicks to change doc-type
    """
    btnName = self.sender().accessibleName()
    item, projID = btnName.split('/')
    self.comm.changeTable.emit(item, projID)
    return


  def btnProject(self):
    """
    What happens when user clicks to view project
    """
    btnName = self.sender().accessibleName()
    projID, item = btnName.split('/')
    if item=='':
      if self.widgetsHidden[projID]: #get button in question
        self.widgets[projID].show()
        self.widgetsHidden[projID]=False
        self.comm.changeProject.emit(projID, item)
      else:
        self.widgets[projID].hide()
        self.widgetsHidden[projID]=True
    else:
      self.comm.changeProject.emit(projID, item)
    return
