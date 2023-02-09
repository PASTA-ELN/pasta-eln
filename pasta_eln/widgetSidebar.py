""" Sidebar widget that includes the navigation items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout    # pylint: disable=no-name-in-module
from anytree import PreOrderIter
from PySide6.QtCore import QSize

from .dialogConfig import Configuration
from .style import RadioIconButton, TextButton, LetterButton, IconButton

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    if hasattr(self.comm.backend, 'configuration'):
      width = self.comm.backend.configuration['GUI']['sidebarWidth']
      self.setFixedWidth(width)#64

    # GUI elements
    mainL = QVBoxLayout()
    mainL.setContentsMargins(7,77,7,7)
    mainL.setSpacing(7)
    self.setLayout(mainL)
    # storage of all projects
    self.widgets = {}
    self.layouts = {}
    self.widgetsHidden = {}

    if hasattr(comm.backend, 'db'):
      # All projects
      textButton = RadioIconButton('ei.book', self.btnDocType, mainL, 'x0/', 'All Projects', backend=self.comm.backend) #TODO weird formatting on Right side
      textButton.setFixedSize(width,50)
      textButton.setIconSize(QSize(30,30))
      #Storage of Icons for Buttons
      iconTable = {"Measurements":"fa.thermometer-3","Samples":"fa5s.vial","Procedures":"fa.list-ol","Instruments":"ri.scales-2-line"}
      # Add other data types
      dTypeW = QWidget()
      dTypeL = QVBoxLayout(dTypeW)
      dTypeL.setContentsMargins(0,10,0,0)
      for idx, doctype in enumerate(comm.backend.db.dataLabels):
        if doctype[0]!='x':
          button = RadioIconButton(iconTable[comm.backend.db.dataLabels[doctype]], self.btnDocType, mainL, doctype+'/', comm.backend.db.dataLabels[doctype], backend=self.comm.backend)
          button.setFixedSize(width,50)
          button.setIconSize(QSize(30, 30))
          dTypeL.addWidget(button)
      mainL.addWidget(dTypeW)

      # projectIDs = [i['id'] for i in comm.backend.db.getView('viewDocType/x0')]
      # currentID  = None
      # for projID in projectIDs:
      #   hierarchy = comm.backend.db.getHierarchy(projID)
      #   for node in PreOrderIter(hierarchy, maxlevel=2):
      #     if node.docType[0][0]!='x':
      #       continue
      #     if node.docType[0]=='x0':
      #       button = TextButton(node.name, self.btnProject, mainL, node.id+'/', style='margin-top: 30')
      #       projectW = QWidget()
      #       projectW.hide()
      #       projectL = QVBoxLayout(projectW)
      #       projectL.setContentsMargins(0,0,0,0)
      #       currentID = node.id
      #       # Add other data types
      #       dTypeW = QWidget()
      #       dTypeL = QVBoxLayout(dTypeW)
      #       dTypeL.setContentsMargins(0,0,0,0)
      #       for idx, doctype in enumerate(comm.backend.db.dataLabels):
      #         if doctype[0]!='x':
      #           button = LetterButton(comm.backend.db.dataLabels[doctype], self.btnDocType, None, doctype+'/'+currentID)
      #           dTypeL.addWidget(button)
      #       # create widgets
      #       projectL.addWidget(dTypeW)
      #       self.widgets[currentID] = projectW
      #       self.layouts[currentID] = projectL
      #       self.widgetsHidden[currentID] = True
      #       mainL.addWidget(projectW)
      #     if node.docType[0]=='x1':
      #       button = TextButton(node.name, self.btnProject, self.layouts[currentID], currentID+'/'+node.id, \
      #                           style='margin-left: 20')

    # Other buttons
    mainL.addStretch(1)
    settingButton = IconButton('fa.gear', self.btnConfig, mainL, backend=self.comm.backend)
    settingButton.setFixedSize(width,50)
    settingButton.setIconSize(QSize(30, 30))
    settingButton.setStyleSheet("border-width:2")
    if not hasattr(comm.backend, 'db'):  #if no backend
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
