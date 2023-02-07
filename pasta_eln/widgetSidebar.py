""" Sidebar widget that includes the navigation items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QTreeWidget, QTreeWidgetItem  # pylint: disable=no-name-in-module
from anytree import PreOrderIter

from .dialogConfig import Configuration
from .style import TextButton, LetterButton, IconButton

class Sidebar(QWidget):
  """ Sidebar widget that includes the navigation items """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    if hasattr(self.comm.backend, 'configuration'):
      width = self.comm.backend.configuration['GUI']['sidebarWidth']
      self.setMinimumWidth(width)
      self.setMaximumWidth(width)
    if not hasattr(comm.backend, 'db'):  #if no backend
      configWindow = Configuration(comm.backend, 'setup')
      configWindow.exec()

    # GUI elements
    mainL = QVBoxLayout()
    mainL.setContentsMargins(0,0,0,0)
    mainL.setSpacing(7)
    self.setLayout(mainL)
    # storage of all project widgets and layouts
    self.openProjectId = ''
    self.widgetsAction = {}
    self.widgetsList = {}

    if hasattr(comm.backend, 'db'):
      hierarchy = comm.backend.db.getView('viewDocType/x0')
      for project in hierarchy:
        projID = project['id']
        projName = project['value'][0]
        if self.openProjectId == '':
          self.openProjectId = projID
        #head: show project name as button
        projectW = QWidget()
        projectL = QVBoxLayout(projectW)
        projectL.setContentsMargins(0,0,0,0)
        TextButton(projName, self.btnProject, projectL, projID+'/')

        # actions: scan, curate, ...
        actionW = QWidget()
        if self.openProjectId != projID:
          actionW.hide()
        actionL = QGridLayout(actionW)
        btnScan = TextButton('Scan', self.btnScan, None, projID)
        actionL.addWidget(btnScan, 0,0)
        btnCurate = TextButton('Curate', self.btnCurate, None, projID)
        actionL.addWidget(btnCurate, 0,1)
        projectL.addWidget(actionW)
        self.widgetsAction[projID] = actionW

        # lists: view list of measurements, ... of this project
        listW = QWidget()
        if self.openProjectId != projID:
          listW.hide()
        listL = QGridLayout(listW)
        for idx, doctype in enumerate(comm.backend.db.dataLabels):
          if doctype[0]!='x':
            button = LetterButton(comm.backend.db.dataLabels[doctype], self.btnDocType, None, doctype+'/'+projID, style='color: red')
            listL.addWidget(button, int(idx/3), idx%3)
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
