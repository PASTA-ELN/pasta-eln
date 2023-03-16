""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QStyledItemDelegate  # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem    # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, Qt                            # pylint: disable=no-name-in-module
from anytree import PreOrderIter
from .widgetProjectLeafRenderer import ProjectLeafRenderer
from .widgetTreeView import TreeView
from .style import TextButton


class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeProject.connect(self.changeProject)
    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)
    self.tree   = None
    self.model  = None
    self.bodyW  = None
    self.projID = ''


  def modelChanged(self):
    """ after drag-drop, record changes """
    def iterItems(root):
      if root is not None:
        stack = [root]
        while stack:
          parent = stack.pop(0)
          for row in range(parent.rowCount()):
            child = parent.child(row, 0)
            yield child
            if child.hasChildren():
              stack.append(child)
    #find new version
    listDB   = self.comm.backend.db.getView('viewHierarchy/viewHierarchy', startKey=self.projID)
    listDBKeys= [i['key'] for i in listDB]
    listChanged = []
    rootItem = self.model.invisibleRootItem()
    for item in iterItems(rootItem):
      hierStack = [item.text()]  #create reversed
      currentItem = item
      while currentItem.parent() is not None:
        currentItem = currentItem.parent()
        hierStack.append(currentItem.text())
      hierStack = [self.projID] + hierStack[::-1]  #add project id and reverse
      if ' '.join(hierStack) not in listDBKeys:
        docID = hierStack[-1]
        doc = self.comm.backend.db.getDoc(docID)
        childNew = item.row()
        stackNew = hierStack[:-1]

        print('changed ',stackNew, childNew, item.text()) #TODO_P1
        print(item.flags(), item.isDragEnabled() )
      elif hierStack[-1]=='x-5ec061a4a9b4475fa19f1025beea9105':
        print('hhe',hierStack,item.text())
        print(item.flags(), item.index().row(), item.row() )
    return


  @Slot(str)
  def changeProject(self, projID, docID):
    """
    What happens when user clicks to change doc-type

    Args:
      projID (str): document id of project
      docID (str): document id of focus item, if not given focus at project
    """
    #initialize
    self.projID = projID
    selectedItem = None
    self.model = QStandardItemModel()
    self.tree = TreeView(self, self.comm, self.model)
    self.model.itemChanged.connect(self.modelChanged)
    rootItem = self.model.invisibleRootItem()


    def iterateTree(nodeHier):
      """
      Recursive function to translate the hierarchical node into a tree-node

      Args:
        nodeHier (Anytree.Node): anytree node

      Returns:
        QtTreeWidgetItem: tree node
      """
      #prefill docID
      nodeTree = QStandardItem(nodeHier.id)  #nodeHier.name,'/'.join(nodeHier.docType),nodeHier.id])
      if nodeHier.id[0]=='x':
        nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
      else:
        nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
      if docID==nodeHier.id:
        nonlocal selectedItem
        selectedItem = nodeTree
      children = []
      for childHier in nodeHier.children:
        childTree = iterateTree(childHier)
        children.append(childTree)
      if len(children)>0:
        nodeTree.appendRows(children)
      return nodeTree

    #Populate model body of change project: start recursion
    nodeHier = self.comm.backend.db.getHierarchy(self.projID)
    for node in PreOrderIter(nodeHier, maxlevel=2):
      if node.is_root:         #Project header
        self.projHeader()
      else:
        rootItem.appendRow(iterateTree(node))
    self.tree.expandAll()
    if selectedItem is not None:
      self.tree.setCurrentItem(selectedItem)
    self.mainL.addWidget(self.tree)
    return


  def btnEvent(self):
    """ Click button on top of project page """
    btnName = self.sender().accessibleName()
    if btnName == 'projHide':
      if self.bodyW.isHidden():
        self.bodyW.show()
      else:
        self.bodyW.hide()
    return


#TODO_P1 save drag-drop; add node at end; context-menu or click each leaf
# hide

  def projHeader(self):
    """
    Create header of page
    """
    doc = self.comm.backend.db.getDoc(self.projID)
    headerW = QWidget()  # Leaf(self.comm, node.id)
    headerL = QVBoxLayout(headerW)
    topbarW = QWidget()
    topbarL = QHBoxLayout(topbarW)
    topbarL.addWidget(QLabel(doc['-name']))
    TextButton('Hide', self.btnEvent, topbarL, 'projHide', checkable=True)
    TextButton('Add child',None, topbarL)
    headerL.addWidget(topbarW)
    self.bodyW   = QWidget()
    bodyL   = QVBoxLayout(self.bodyW)
    tags = ', '.join(doc['tags']) if 'tags' in doc else ''
    bodyL.addWidget(QLabel('Tags: '+tags))
    for key,value in doc.items():
      if key[0] in ['_','-']:
        continue
      bodyL.addWidget(QLabel(key+': '+str(value)))
    headerL.addWidget(self.bodyW)
    self.mainL.addWidget(headerW)
    return
