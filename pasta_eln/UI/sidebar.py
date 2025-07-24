""" Sidebar widget that includes the navigation items """
import logging
from enum import Enum
from typing import Any
from anytree import Node
import pandas as pd
from PySide6.QtCore import Slot                                            # pylint: disable=no-name-in-module
from PySide6.QtGui import QResizeEvent                                     # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QFrame, QTreeWidgetItem, QVBoxLayout, QWidget# pylint: disable=no-name-in-module
from .guiCommunicate import Communicate
from .guiStyle import IconButton, TextButton, space, widgetAndLayout, widgetAndLayoutGrid
from .messageDialog import showMessage

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    self.comm.changeSidebar.connect(self.paint)
    self.comm.backendThread.worker.beSendProjects.connect(self.onGetData)
    self.openProjectId = ''
    self.projects = pd.DataFrame()
    self.sideBarWidth = self.comm.configuration['GUI']['sidebarWidth']

    # GUI elements
    mainL = QVBoxLayout()
    self.setFixedWidth(self.sideBarWidth)
    mainL.setContentsMargins(space['s'],space['s'],space['0'],space['s'])
    mainL.setSpacing(15)
    if self.comm.configuration['GUI']['showProjectBtn']=='Yes':
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
    self.paint()


  @Slot(pd.DataFrame)
  def onGetData(self, projects:pd.DataFrame) -> None:
    """
    Callback function to handle the received projects data

    Args:
      projects (pd.DataFrame): DataFrame containing project information
    """
    self.projects = projects
    self.paint('redraw')


  @Slot(str)
  def paint(self, projectChoice:str='') -> None:
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
    # fill sidebar
    if self.projects.empty:
      return
    if 'status' in self.projects.columns and len(self.projects)>5:
      temp = self.projects[self.projects['status']=='active']
      if len(temp)>2:
        self.projects = temp
    self.projects = self.projects.sort_values('name', axis=0).reset_index(drop=True)
    maxProjects = int((self.height()-120)/50)-1
    for index, project in self.projects.iterrows():
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

      # actions: scan, curate, ..
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
      self.btnDocTypes = []
      for idx, (doctype, value) in enumerate(self.comm.docTypesTitles.items()):
        if doctype[0]!='x' and '/' not in doctype:
          icon = 'fa5s.asterisk' if value['icon']=='' else value['icon']
          self.btnDocTypes.append(IconButton(icon, self, [Command.LIST_DOCTYPE,doctype,projID], None, value['title']))
          listL.addWidget(self.btnDocTypes[-1], 0, idx)
      self.btnUnknown = IconButton('fa5.file', self, [Command.LIST_DOCTYPE,'-',projID], None, 'Unidentified')
      listL.addWidget(self.btnUnknown, 0, len(self.comm.docTypesTitles)+1)
      self.widgetsList[projID] = listW

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
    self.paint('redraw')
    return super().resizeEvent(event)


class Command(Enum):
  """ Commands used in this file """
  LIST_DOCTYPE = 1
  SHOW_PROJECT = 2
  SCAN_PROJECT = 3
  LIST_PROJECTS= 4
