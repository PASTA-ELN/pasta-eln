""" Sidebar widget that includes the navigation items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QTreeWidget, QTreeWidgetItem, QFrame  # pylint: disable=no-name-in-module
from PySide6.QtCore import QSize                                         # pylint: disable=no-name-in-module
from anytree import PreOrderIter

from .dialogConfig import Configuration
from .style import TextButton, LetterButton, IconButton, getColor

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    if hasattr(self.comm.backend, 'configuration'):
      width = self.comm.backend.configuration['GUI']['sidebarWidth']
      self.setFixedWidth(width)#64
    if not hasattr(comm.backend, 'db'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()

    # GUI elements
    mainL = QVBoxLayout()
    mainL.setContentsMargins(7,15,0,7)
    mainL.setSpacing(7)
    self.setLayout(mainL)
    # storage of all project widgets and layouts
    self.openProjectId = ''
    self.widgetsAction = {}
    self.widgetsList = {}
    self.widgetsProject = {}

    if hasattr(comm.backend, 'db'):
      hierarchy = comm.backend.db.getView('viewDocType/x0')
      for project in hierarchy:
        projID = project['id']
        projName = project['value'][0]
        if self.openProjectId == '':
          self.openProjectId = projID
        #head: show project name as button
        projectW = QFrame()
        projectL = QVBoxLayout(projectW)
        projectL.setContentsMargins(3,3,3,3)
        btnProj = TextButton(projName, self.btnProject, projectL, projID+'/')
        self.widgetsProject[projID] = btnProj
        btnProj.setStyleSheet("border-width:0")
        projectW.setStyleSheet("background-color:"+ getColor(self.comm.backend, 'secondary'))

        # actions: scan, curate, ...
        actionW = QWidget()
        if self.openProjectId != projID:
          actionW.hide()
        actionL = QGridLayout(actionW)
        actionL.setContentsMargins(0,0,0,0)
        btnScan = IconButton('mdi.clipboard-search-outline', self.btnScan, None, projID, 'Scan', self.comm.backend, text='Scan')
        actionL.addWidget(btnScan, 0,0)
        btnCurate = IconButton('mdi.filter-plus-outline', self.btnCurate, None, projID, 'Curate', self.comm.backend, text='Curate')
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
        for idx, doctype in enumerate(comm.backend.db.dataLabels):
          if doctype[0]!='x':
            button = IconButton(iconTable[comm.backend.db.dataLabels[doctype]], self.btnDocType, None, doctype+'/'+projID, comm.backend.db.dataLabels[doctype],self.comm.backend)
            listL.addWidget(button, 0, idx)
            button.setStyleSheet("border-width:0")

        projectL.addWidget(listW)
        self.widgetsList[projID] = listW

        # show folders as hierarchy
        treeW = QTreeWidget()
        treeW.setHeaderHidden(True)
        treeW.setColumnCount(1)
        treeW.itemClicked.connect(self.btnTree)
        hierarchy = comm.backend.db.getHierarchy(projID)
        treeW.insertTopLevelItem(0, self.iterateTree(hierarchy, projID))
        projectL.addWidget(treeW)

        # finalize layout
        mainL.addWidget(projectW)
    # Other buttons
    mainL.addStretch(1)


  def iterateTree(self, nodeHier, projectID):
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
    self.comm.changeProject.emit(projID, item)
    return


  def btnScan(self):
    """
    What happens if user clicks button "Scan"
    """
    return
  def btnCurate(self):
    """
    What happens if user clicks button "Curate"
    """
    return
  def btnTree(self, item):
    """
    What happpens if user clicks on branch in tree
    """
    projId, docId = item.text(1).split('/')
    self.comm.changeProject.emit(projId, docId)
    return
  def btnCollapse(self):
    """
    What happens if user clicks on collapse button
    """
    return
