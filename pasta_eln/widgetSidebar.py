""" Sidebar widget that includes the navigation items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QFrame, QProgressBar # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, Qt                                    # pylint: disable=no-name-in-module
from anytree import PreOrderIter, Node

from .dialogConfig import Configuration
from .style import TextButton, IconButton, getColor, showMessage, widgetAndLayout, spacesMap, iconsDocTypes
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
    mainL = QVBoxLayout()
    mainL.setContentsMargins(spacesMap['s'],spacesMap['s'],spacesMap['0'],spacesMap['s'])
    mainL.setSpacing(0)
    _, self.projectL = widgetAndLayout('V', mainL, spacing='s')
    self.progress = QProgressBar(self)
    self.progress.hide()
    self.comm.progressBar = self.progress
    mainL.addWidget(self.progress)
    self.setLayout(mainL)
    self.redraw()
    #++ TODO projectView: allow scroll in sidebar, size changegable, drag-and-drop to move
    #   more below and other files


  @Slot(str)
  def redraw(self, projectID:str='') -> None:
    """
    Redraw sidebar: e.g. after change of project visibility in table

    Args:
      projectID (str): projectID on which to focus: '' string=draw default; 'redraw' implies redraw; id implies id
    """
    # Delete old widgets from layout and create storage
    for i in reversed(range(self.projectL.count())):
      self.projectL.itemAt(i).widget().setParent(None) # type: ignore
    if projectID != 'redraw':
      self.openProjectId = projectID
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
        actionW, actionL = widgetAndLayout('Grid', projectL)
        if self.openProjectId != projID: #depending which project is open
          actionW.hide()
          projectW.setStyleSheet("background-color:"+ getColor(self.comm.backend, 'secondaryDark'))
        else:
          projectW.setStyleSheet("background-color:"+ getColor(self.comm.backend, 'secondaryLight'))
        btnScan = IconButton('mdi.clipboard-search-outline', self.btnScan, None, projID, 'Scan', self.comm.backend, text='Scan')
        actionL.addWidget(btnScan, 0,0)  # type: ignore
        btnCurate = IconButton('mdi.filter-plus-outline', self.btnCurate, None, projID, 'Special', self.comm.backend, text='Special')
        btnCurate.hide()
        actionL.addWidget(btnCurate, 0,1)         # type: ignore
        self.widgetsAction[projID] = actionW
        btnScan.setStyleSheet("border-width:0")
        btnCurate.setStyleSheet("border-width:0")

        # lists: view list of measurements, ... of this project
        listW, listL = widgetAndLayout('Grid', projectL)
        if self.openProjectId != projID:
          listW.hide()
        for idx, doctype in enumerate(self.comm.backend.db.dataLabels):
          if doctype[0]!='x':
            button = IconButton(iconsDocTypes[self.comm.backend.db.dataLabels[doctype]], self.btnDocType, None, \
                     doctype+'/'+projID, self.comm.backend.db.dataLabels[doctype],self.comm.backend)
            listL.addWidget(button, 0, idx)    # type: ignore
        button = IconButton(iconsDocTypes['-'], self.btnDocType, None, '-/'+projID, 'Unidentified', self.comm.backend)
        listL.addWidget(button, 0, len(self.comm.backend.db.dataLabels)+1)  # type: ignore
        self.widgetsList[projID] = listW

        # show folders as hierarchy
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
        self.projectL.addWidget(projectW)
    # Other buttons
    stretch = QWidget()

    self.projectL.addWidget(stretch, stretch=2)  # type: ignore
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
    self.comm.backend.scanProject(self.progress, self.openProjectId, '')
    self.comm.changeProject.emit(self.openProjectId,'')
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
