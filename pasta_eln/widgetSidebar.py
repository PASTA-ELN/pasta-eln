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
      projectIDs = [i['id'] for i in hierarchy]
      for projID in projectIDs:
        #head: show project name as button
        projectW = QWidget()
        projectL = QVBoxLayout(projectW)
        projectL.setContentsMargins(0,0,0,0)
        try:
          name     = [i for i in hierarchy if i['id']==projID][0]['value'][0]
        except:
          name     = 'ERROR OCCURRED'
        btnProject = TextButton(name, self.btnProject, projectL, projID+'/')

        # actions: scan, curate, ...
        actionW = QWidget()
        actionL = QGridLayout(actionW)
        btnScan = TextButton('Scan', self.btnScan, None, projID)
        actionL.addWidget(btnScan, 0,0)
        btnCurate = TextButton('Curate', self.btnCurate, None, projID)
        actionL.addWidget(btnCurate, 0,1)
        projectL.addWidget(actionW)
        self.widgetsAction[projID] = actionW

        # lists: view list of measurements, ... of this project
        listW = QWidget()
        listL = QGridLayout(listW)
        for idx, doctype in enumerate(comm.backend.db.dataLabels):
          if doctype[0]!='x':
            button = LetterButton(comm.backend.db.dataLabels[doctype], self.btnDocType, None, doctype+'/'+projID, style='color: red')
            listL.addWidget(button, int(idx/3), idx%3)
        projectL.addWidget(listW)
        self.widgetsList[projID] = listW

        # show folders as hierarchy
        def iterateTree(nodeHier):
          """
          Recursive function to translate the hierarchical node into a tree-node

          Args:
            nodeHier (Anytree.Node): anytree node

          Returns:
            QtTreeWidgetItem: tree node
          """
          #prefill with name, doctype, id
          nodeTree = QTreeWidgetItem([nodeHier.name, projID+'/'+nodeHier.id ])
          children = []
          for childHier in nodeHier.children:
            if childHier.docType[0][0]=='x':
              childTree = iterateTree(childHier)
              children.append(childTree)
          if len(children)>0:
            nodeTree.insertChildren(0,children)
          return nodeTree

        treeW = QTreeWidget()
        treeW.setHeaderHidden(True)
        treeW.setColumnCount(1)
        treeW.itemClicked.connect(self.btnTree)
        hierarchy = comm.backend.db.getHierarchy(projID)
        treeW.insertTopLevelItem(0, iterateTree(hierarchy))
        projectL.addWidget(treeW)

        # finalize layout
        mainL.addWidget(projectW)
    # Other buttons
    mainL.addStretch(1)


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

  def btnScan(self):
    """
    """
    return
  def btnCurate(self):
    """
    """
    return
  def btnTree(self, item):
    """
    What happpens if user clicks on branch in tree
    """
    projId, docId = item.text(1).split('/')
    self.comm.changeProject.emit(projId, docId)
    return
