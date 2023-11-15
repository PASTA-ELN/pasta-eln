""" Sidebar widget that includes the navigation items """
from enum import Enum
from typing import Any
from PySide6.QtGui import QResizeEvent                                                                 # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QFrame, QProgressBar # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot                                                                        # pylint: disable=no-name-in-module
from anytree import PreOrderIter, Node
from .config import Configuration
from ..guiStyle import TextButton, IconButton, getColor, showMessage, widgetAndLayout, space, iconsDocTypes
from ..guiCommunicate import Communicate

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeSidebar.connect(self.change)
    if hasattr(self.comm.backend, 'configuration'):
      self.sideBarWidth = self.comm.backend.configuration['GUI']['sidebarWidth']
      self.setFixedWidth(self.sideBarWidth)
    if not hasattr(comm.backend, 'db'):  #if no backend
      configWindow = Configuration(comm, 'setup')
      configWindow.exec()
    self.openProjectId = ''

    # GUI elements
    mainL = QVBoxLayout()
    mainL.setContentsMargins(space['s'],space['s'],space['0'],space['s'])
    mainL.setSpacing(0)
    _, self.projectsListL = widgetAndLayout('V', mainL, spacing='s')
    # projectListW, self.projectsListL = widgetAndLayout('V', None, spacing='s')
    # scrollSection = QScrollArea()
    # scrollSection.setWidget(projectListW)
    # mainL.addWidget(scrollSection)
    self.progress = QProgressBar(self)
    self.progress.hide()
    self.comm.progressBar = self.progress
    mainL.addWidget(self.progress)
    self.setLayout(mainL)

    self.widgetsAction:dict[str,QWidget] = {}
    self.widgetsList:dict[str,QWidget]   = {}
    self.widgetsProject:dict[str,Any]    = {} #title bar and widget that contains all of project
    self.change()
    #++ TODO projectView: allow size changegable, drag-and-drop to move
    #   more below and other files


  @Slot(str)
  def change(self, projectChoice:str='') -> None:
    """
    Redraw sidebar: e.g. after change of project visibility in table

    Args:
      projectChoice (str): projectID on which to focus: '' string=draw default=none; 'redraw' implies redraw; id implies id
    """
    # Delete old widgets from layout and create storage
    for i in reversed(range(self.projectsListL.count())):
      self.projectsListL.itemAt(i).widget().setParent(None) # type: ignore
    if projectChoice != 'redraw':
      self.openProjectId = projectChoice
    self.widgetsAction = {}
    self.widgetsList = {}
    self.widgetsProject = {} #title bar and widget that contains all of project
    backend = self.comm.backend

    if hasattr(backend, 'db'):
      db = self.comm.backend.db
      hierarchy = db.getView('viewDocType/x0')
      lastChangeDate = [db.getDoc(project['id'])['-date'] for project in hierarchy]
      maxProjects = int((self.height()-120)/50)-1
      for index, project in enumerate(x for _, x in sorted(zip(lastChangeDate, hierarchy), reverse=True)):
        if index>maxProjects:
          break
        projID = project['id']
        projName = project['value'][0]
        #head: show project name as button
        projectW = QFrame()
        # projectW.setMinimumHeight(300) #convenience: allow scroll in sidebar
        projectL = QVBoxLayout(projectW)
        projectL.setContentsMargins(3,3,3,3)
        maxLabelCharacters = int((self.sideBarWidth-50)/7.1)
        label = (projName if len(projName) < maxLabelCharacters else f'{projName[:maxLabelCharacters - 3]}...')
        btnProj = TextButton(label, self, [Command.SHOW_PROJECT, projID, ''], projectL)
        btnProj.setStyleSheet("border-width:0")
        self.widgetsProject[projID] = [btnProj, projectW]

        # actions: scan, curate, ...
        actionW, actionL = widgetAndLayout('Grid', projectL)
        if self.openProjectId != projID: #depending which project is open
          actionW.hide()
          projectW.setStyleSheet("background-color:"+ getColor(backend, 'secondaryDark'))
        else:
          projectW.setStyleSheet("background-color:"+ getColor(backend, 'secondaryLight'))
        btnScan = TextButton('Scan', self, [Command.SCAN_PROJECT, projID], None, 'Scan', \
                             iconName='mdi.clipboard-search-outline')
        actionL.addWidget(btnScan, 0,0)  # type: ignore
        btnCurate = TextButton('Special', self, [projID], None)
        btnCurate.hide()
        actionL.addWidget(btnCurate, 0,1)         # type: ignore
        self.widgetsAction[projID] = actionW
        btnScan.setStyleSheet("border-width:0")
        btnCurate.setStyleSheet("border-width:0")

        # lists: view list of measurements, ... of this project
        listW, listL = widgetAndLayout('Grid', projectL)
        if self.openProjectId != projID:
          listW.hide()
        for idx, doctype in enumerate(db.dataLabels):
          if doctype[0]!='x':
            if db.dataLabels[doctype] in iconsDocTypes:
              icon = iconsDocTypes[db.dataLabels[doctype]]
            else:
              icon = 'fa.asterisk'
            btn = IconButton(icon, self, [Command.LIST_DOCTYPE,doctype,projID], None,db.dataLabels[doctype])
            listL.addWidget(btn, 0, idx)    # type: ignore
        btn = IconButton(iconsDocTypes['-'], self, [Command.LIST_DOCTYPE,'-',projID], None, 'Unidentified')
        listL.addWidget(btn, 0, len(db.dataLabels)+1)  # type: ignore
        self.widgetsList[projID] = listW

        # show folders as hierarchy
        treeW = QTreeWidget()
        treeW.hide()  #convenience: allow scroll in sidebar
        treeW.setHeaderHidden(True)
        treeW.setColumnCount(1)
        treeW.itemClicked.connect(lambda item: self.execute([Command.SHOW_FOLDER, *item.text(1).split('/')]))
        hierarchy = db.getHierarchy(projID)
        rootItem = treeW.invisibleRootItem()
        count = 0
        for node in PreOrderIter(hierarchy, maxlevel=2):
          if not node.is_root and node.id[0]=='x':
            rootItem.insertChild(count, self.iterateTree(node, projID))
            count += 1
        projectL.addWidget(treeW)
        # finalize layout
        self.projectsListL.addWidget(projectW)
    # Other buttons
    stretch = QWidget()
    self.projectsListL.addWidget(stretch, stretch=2)  # type: ignore
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks a button

    Args:
      command (list): list of commands
    """
    if command[0] is Command.LIST_DOCTYPE:
      self.comm.changeTable.emit(command[1], command[2])
    elif command[0] is Command.SHOW_PROJECT:
      projID = command[1]
      item   = command[2]
      if item=='': #clicked on project-button, not tree view
        self.openProjectId = projID
        for docID, widget in self.widgetsAction.items():
          if docID == projID:
            widget.show()
          else:
            widget.hide()
        for docID, widget in self.widgetsList.items():
          if docID == projID:
            widget.show()
          else:
            widget.hide()
        for docID, [_, projWidget] in self.widgetsProject.items():
          if docID == projID:
            projWidget.setStyleSheet("background-color:"+ getColor(self.comm.backend, 'secondaryLight'))
          else:
            projWidget.setStyleSheet("background-color:"+ getColor(self.comm.backend, 'secondaryDark'))
      self.comm.changeProject.emit(projID, item)
    elif command[0] is Command.SCAN_PROJECT:
      self.comm.backend.scanProject(self.progress, self.openProjectId, '')
      self.comm.changeProject.emit(self.openProjectId,'')
      showMessage(self, 'Information','Scanning finished')
    elif command[0] is Command.SHOW_FOLDER:
      self.comm.changeProject.emit(command[1], command[2])
    else:
      print("**ERROR sidebar menu unknown:",command)
    return


  def iterateTree(self, nodeHier:Node, projectID:str) -> QTreeWidgetItem:
    """
    Recursive function to translate the hierarchical node into a tree-node

    Args:
      nodeHier (Anytree.Node): anytree node
      projectID (str): project id of this tree

    Returns:
      QtTreeWidgetItem: tree node
    """
    #prefill with name, doctype, id
    nodeTree = QTreeWidgetItem([nodeHier.name, f'{projectID}/{nodeHier.id}'])
    children = []
    for childHier in nodeHier.children:
      if childHier.docType[0][0]=='x':
        childTree = self.iterateTree(childHier, projectID)
        children.append(childTree)
    if children:
      nodeTree.insertChildren(0,children)
    return nodeTree


  def resizeEvent(self, event: QResizeEvent) -> None:
    """
    executed upon resize

    Args:
      event (QResizeEvent): event
    """
    self.change()
    return super().resizeEvent(event)


class Command(Enum):
  """ Commands used in this file """
  LIST_DOCTYPE = 1
  SHOW_PROJECT = 2
  SCAN_PROJECT = 3
  SHOW_FOLDER  = 4
