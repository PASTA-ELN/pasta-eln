""" Sidebar widget that includes the navigation items """
import logging
from enum import Enum
from typing import Any
from anytree import Node
from PySide6.QtCore import Slot                                            # pylint: disable=no-name-in-module
from PySide6.QtGui import QResizeEvent                                     # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QFrame, QTreeWidgetItem, QVBoxLayout, QWidget# pylint: disable=no-name-in-module
from ..guiCommunicate import Communicate
from .config import Configuration
from .guiStyle import IconButton, TextButton, space, widgetAndLayout, widgetAndLayoutGrid
from .messageDialog import showMessage

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeSidebar.connect(self.change)
    if hasattr(self.comm.backend, 'configuration'):
      self.sideBarWidth = self.comm.backend.configuration['GUI']['sidebarWidth']
      self.setFixedWidth(self.sideBarWidth)
    if not hasattr(comm.backend, 'db'):                                                        # if no backend
      configWindow = Configuration(comm, 'setup')
      configWindow.exec()
    self.openProjectId = ''

    # GUI elements
    mainL = QVBoxLayout()
    mainL.setContentsMargins(space['s'],space['s'],space['0'],space['s'])
    mainL.setSpacing(15)
    if self.comm.backend.configuration['GUI']['showProjectBtn']=='Yes':
      TextButton('List projects', self, [Command.LIST_PROJECTS], mainL, 'Show list of all projects')
    _, self.projectsListL = widgetAndLayout('V', mainL, spacing='m')
    self.setLayout(mainL)

    self.widgetsAction:dict[str,QWidget] = {}
    self.widgetsList:dict[str,QWidget]   = {}
    self.widgetsProject:dict[str,Any]    = {}               #title bar and widget that contains all of project
    self.btnProjects:list[TextButton]    = []                               # list of buttons to show projects
    self.btnScan:TextButton|None         = None
    self.btnDocTypes:list[IconButton]    = []                         # list of buttons to show docType tables
    self.btnUnknown:IconButton|None      = None
    self.change()


  @Slot(str)
  def change(self, projectChoice:str='') -> None:
    """
    Redraw sidebar: e.g. after change of project visibility in table

    Args:
      projectChoice (str): projectID on which to focus: '' string=draw default=none; 'redraw' implies redraw; id implies id
    """
    # Delete old widgets from layout and create storage
    for i in reversed(range(self.projectsListL.count())):
      self.projectsListL.itemAt(i).widget().setParent(None)
    if projectChoice != 'redraw':
      self.openProjectId = projectChoice
    self.widgetsAction = {}
    self.widgetsList = {}
    self.widgetsProject = {}                                #title bar and widget that contains all of project
    backend = self.comm.backend

    if hasattr(backend, 'db'):
      db = self.comm.backend.db
      hierarchy = db.getView('viewDocType/x0')
      if 'status' in hierarchy.columns and len(hierarchy)>5:
        temp = hierarchy[hierarchy['status']=='active']
        if len(temp)>2:
          hierarchy = temp
      hierarchy = hierarchy.sort_values('name', axis=0).reset_index(drop=True)
      maxProjects = int((self.height()-120)/50)-1
      for index, project in hierarchy.iterrows():
        if index>maxProjects:
          break
        projID = project['id']
        projName = project['name']
        #head: show project name as button
        projectW = QFrame()
        # projectW.setMinimumHeight(300) # convenience: allow scroll in sidebar
        projectL = QVBoxLayout(projectW)
        projectL.setSpacing(3)
        projectL.setContentsMargins(3,3,3,3)
        maxLabelCharacters = int((self.sideBarWidth-50)/7.1)
        label = (projName if len(projName) < maxLabelCharacters else f'{projName[:maxLabelCharacters - 3]}...')
        self.btnProjects.append(TextButton(label, self, [Command.SHOW_PROJECT, projID, ''], projectL))
        self.widgetsProject[projID] = [self.btnProjects[-1], projectW]

        # actions: scan, curate, ...
        actionW, actionL = widgetAndLayoutGrid(projectL)
        if self.openProjectId != projID:                                      #depending which project is open
          actionW.hide()
          projectW.setStyleSheet(self.comm.palette.get('secondaryDark', 'background-color'))
        else:
          projectW.setStyleSheet(self.comm.palette.get('secondaryLight','background-color'))
        self.btnScan = TextButton('Scan', self, [Command.SCAN_PROJECT, projID], None, 'Scan', \
                             iconName='mdi.clipboard-search-outline')
        actionL.addWidget(self.btnScan, 0,0)
        # btnCurate = TextButton('Special', self, [projID], None)
        # btnCurate.hide()
        # actionL.addWidget(btnCurate, 0,1)
        self.widgetsAction[projID] = actionW

        # lists: view list of measurements, ... of this project
        listW, listL = widgetAndLayoutGrid(projectL,  spacing='s')
        if self.openProjectId != projID:
          listW.hide()
        docTypes = db.dataHierarchy('', '')
        self.btnDocTypes = []
        for idx, doctype in enumerate(docTypes):
          if doctype[0]!='x' and '/' not in doctype:
            icon = self.comm.backend.db.dataHierarchy(doctype,'icon')[0]
            icon = 'fa5s.asterisk' if icon=='' else icon
            tooltip = db.dataHierarchy(doctype,'title')[0]
            self.btnDocTypes.append(IconButton(icon, self, [Command.LIST_DOCTYPE,doctype,projID], None, tooltip))
            listL.addWidget(self.btnDocTypes[-1], 0, idx)
        self.btnUnknown = IconButton('fa5.file', self, [Command.LIST_DOCTYPE,'-',projID], None, 'Unidentified')
        listL.addWidget(self.btnUnknown, 0, len(docTypes)+1)
        self.widgetsList[projID] = listW

        # show folders as hierarchy
        # Commented out temporarily until getHierarchy is fast
        # - parentNode = find_by_attr(dataTree, parentID, name='id')
        # - is slow if many entries, find better system
        # treeW = QTreeWidget()
        # treeW.hide()  #convenience: allow scroll in sidebar
        # treeW.setHeaderHidden(True)
        # treeW.setColumnCount(1)
        # treeW.itemClicked.connect(lambda item: self.execute([Command.SHOW_FOLDER, *item.text(1).split('/')]))
        # hierarchy, _ = db.getHierarchy(projID)
        # rootItem = treeW.invisibleRootItem()
        # count = 0
        # for node in PreOrderIter(hierarchy, maxlevel=2):
        #   if not node.is_root and node.id[0]=='x':
        #     rootItem.insertChild(count, self.iterateTree(node, projID))
        #     count += 1
        # projectL.addWidget(treeW)
        # finalize layout
        self.projectsListL.addWidget(projectW)
    # Other buttons
    stretch = QWidget()
    self.projectsListL.addWidget(stretch, stretch=2)
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks a button

    Args:
      command (list): list of commands
    """
    if command[0] is Command.LIST_DOCTYPE:
      self.comm.changeTable.emit(command[1], command[2])
    elif command[0] is Command.LIST_PROJECTS:
      self.comm.changeTable.emit('x0', '')
    elif command[0] is Command.SHOW_PROJECT:
      projID = command[1]
      item   = command[2]
      if item=='':                                                   #clicked on project-button, not tree view
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
            projWidget.setStyleSheet(self.comm.palette.get('secondaryLight','background-color'))
          else:
            projWidget.setStyleSheet(self.comm.palette.get('secondaryDark','background-color'))
      self.comm.changeProject.emit(projID, item)
    elif command[0] is Command.SCAN_PROJECT:
      for _ in range(2):                                                         #scan twice: convert, extract
        self.comm.backend.scanProject(None, self.openProjectId)
      self.comm.changeProject.emit(self.openProjectId,'')
      showMessage(self, 'Information','Scanning finished')
    elif command[0] is Command.SHOW_FOLDER:
      self.comm.changeProject.emit(command[1], command[2])
    else:
      logging.error('Sidebar menu unknown: %s',command)
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
    self.change('redraw')
    return super().resizeEvent(event)


class Command(Enum):
  """ Commands used in this file """
  LIST_DOCTYPE = 1
  SHOW_PROJECT = 2
  SCAN_PROJECT = 3
  SHOW_FOLDER  = 4
  LIST_PROJECTS= 5
