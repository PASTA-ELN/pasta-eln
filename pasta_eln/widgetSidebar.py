""" Sidebar widget that includes the navigation items """
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QTreeWidget, QTreeWidgetItem, QFrame # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot                                      # pylint: disable=no-name-in-module
from anytree import PreOrderIter, Node

from .dialogConfig import Configuration
from .style import TextButton, IconButton, getColor, showMessage
from .communicate import Communicate

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeSidebar.connect(self.redraw)
    if hasattr(self.comm.backend, 'configuration'):
      self.sideBarWidth = self.comm.backend.configuration['GUI']['sidebarWidth']
      self.setFixedWidth(self.sideBarWidth)
    if not hasattr(comm.backend, 'db'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()
    self.openProjectId = ''

    # GUI elements
    self.mainL = QVBoxLayout()
    self.mainL.setContentsMargins(7,15,0,7)
    self.mainL.setSpacing(7)
    self.setLayout(self.mainL)
    self.redraw()
    #TODO_P4 projectView: allow scroll in sidebar, size changegable, drag-and-drop to move
    #   more below and other files


  @Slot()
  def redraw(self, reset:bool=False) -> None:
    """
    Redraw sidebar: e.g. after change of project visibility in table

    Args:
      reset (bool): reset which project is open
    """
    logging.debug('sidebar:redraw |')
    # Delete old widgets from layout and create storage
    for i in reversed(range(self.mainL.count())):
      self.mainL.itemAt(i).widget().setParent(None) # type: ignore
    if reset:
      self.openProjectId = ''
    self.widgetsAction = {}
    self.widgetsList = {}
    self.widgetsProject = {} #title bar and widget that contains all of project

    if hasattr(self.comm.backend, 'db'):
      hierarchy = self.comm.backend.db.getView('viewDocType/x0')
      #TODO_P5 for now, sorted by last change of project itself: future create a view that does that automatically
      lastChangeDate = [self.comm.backend.db.getDoc(project['id'])['-date'] for project in hierarchy]
      for project in [x for _, x in sorted(zip(lastChangeDate, hierarchy))]:
        projID = project['id']
        projName = project['value'][0]
        if self.openProjectId == '':
          self.openProjectId = projID
        #head: show project name as button
        projectW = QFrame()
        # projectW.setMinimumHeight(300) #convenience: allow scroll in sidebar
        projectL = QVBoxLayout(projectW)
        projectL.setContentsMargins(3,3,3,3)
        maxLabelCharacters = int((self.sideBarWidth-50)/7.1)
        label = projName if len(projName)<maxLabelCharacters else projName[:maxLabelCharacters-3]+'...'
        btnProj = TextButton(label, self.btnProject, projectL, projID+'/')
        btnProj.setStyleSheet("border-width:0")
        self.widgetsProject[projID] = [btnProj, projectW]

        # actions: scan, curate, ...
        actionW = QWidget()
        if self.openProjectId != projID: #depending which project is open
          actionW.hide()
          projectW.setStyleSheet("background-color:"+ getColor(self.comm.backend, 'secondaryDark'))
        else:
          projectW.setStyleSheet("background-color:"+ getColor(self.comm.backend, 'secondaryLight'))
        actionL = QGridLayout(actionW)
        actionL.setContentsMargins(0,0,0,0)
        btnScan = IconButton('mdi.clipboard-search-outline', self.btnScan, None, projID, 'Scan', self.comm.backend, text='Scan')
        actionL.addWidget(btnScan, 0,0)
        btnCurate = IconButton('mdi.filter-plus-outline', self.btnCurate, None, projID, 'Special', self.comm.backend, text='Special')
        btnCurate.hide()
        actionL.addWidget(btnCurate, 0,1)
        projectL.addWidget(actionW)
        self.widgetsAction[projID] = actionW
        btnScan.setStyleSheet("border-width:0")
        btnCurate.setStyleSheet("border-width:0")

        # lists: view list of measurements, ... of this project
        listW = QWidget()
        listW.setContentsMargins(0,0,0,0)
        if self.openProjectId != projID:
          listW.hide()
        listL = QGridLayout(listW)
        iconTable = {"Measurements":"fa.thermometer-3","Samples":"fa5s.vial","Procedures":"fa.list-ol","Instruments":"ri.scales-2-line"}
        for idx, doctype in enumerate(self.comm.backend.db.dataLabels):
          if doctype[0]!='x':
            button = IconButton(iconTable[self.comm.backend.db.dataLabels[doctype]], self.btnDocType, None, \
                     doctype+'/'+projID, self.comm.backend.db.dataLabels[doctype],self.comm.backend)
            button.setStyleSheet("border-width:0")
            listL.addWidget(button, 0, idx)
        button = IconButton('fa.file-o', self.btnDocType, None, '-/'+projID, 'Unidentified', self.comm.backend)
        button.setStyleSheet("border-width:0")
        listL.addWidget(button, 0, len(self.comm.backend.db.dataLabels)+1)
        projectL.addWidget(listW)
        self.widgetsList[projID] = listW

        # show folders as hierarchy
        #TODO_P4 allow to adjust height
        treeW = QTreeWidget()
        treeW.hide()  #convenience: allow scroll in sidebar
        treeW.setHeaderHidden(True)
        treeW.setColumnCount(1)
        treeW.itemClicked.connect(self.btnTree)
        hierarchy = self.comm.backend.db.getHierarchy(projID)
        rootItem = treeW.invisibleRootItem()
        count = 0
        for node in PreOrderIter(hierarchy, maxlevel=2):
          if not node.is_root and node.id[0]=='x':
            rootItem.insertChild(count, self.iterateTree(node, projID))
            count += 1
        projectL.addWidget(treeW)
        # finalize layout
        self.mainL.addWidget(projectW)
    # Other buttons
    stretch = QWidget()

    self.mainL.addWidget(stretch, stretch=2)
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
    nodeTree = QTreeWidgetItem([nodeHier.name, projectID+'/'+nodeHier.id ])
    children = []
    for childHier in nodeHier.children:
      if childHier.docType[0][0]=='x':
        childTree = self.iterateTree(childHier, projectID)
        children.append(childTree)
    if len(children)>0:
      nodeTree.insertChildren(0,children)
    return nodeTree


  def btnDocType(self) -> None:
    """
    What happens when user clicks to change doc-type
    """
    btnName = self.sender().accessibleName()
    item, projID = btnName.split('/')
    self.comm.changeTable.emit(item, projID)
    return


  def btnProject(self) -> None:
    """
    What happens when user clicks to view project
    """
    btnName = self.sender().accessibleName()
    projID, item = btnName.split('/')
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
    return


  def btnScan(self) -> None:
    """
    What happens if user clicks button "Scan"
    """
    self.comm.backend.scanProject(self.openProjectId)
    #TODO_P3 scanning for progress bar
    self.comm.changeProject.emit(self.openProjectId,'')
    self.comm.changeSidebar.emit()
    showMessage(self, 'Information','Scanning finished')
    return

  def btnCurate(self) -> None:
    """
    What happens if user clicks button "Special"
    -> pull data from server and include
    """
    return
  def btnTree(self, item:QTreeWidgetItem) -> None:
    """
    What happpens if user clicks on branch in tree
    """
    projId, docId = item.text(1).split('/')
    self.comm.changeProject.emit(projId, docId)
    return
