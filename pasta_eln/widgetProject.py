""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QStyledItemDelegate, QAbstractItemView  # pylint: disable=no-name-in-module
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
    self.tree = None
    self.model= None
    self.bodyW= None

  def modelChanged(self):
    print('model changed: save to disk')

  def treeDoubleClicked(self):
    print('tree double clicked, edit leaf')

  def contextMenu(self):
    print('tree double clicked, edit leaf')


  @Slot(str)
  def changeProject(self, projID, docID):
    """
    What happens when user clicks to change doc-type

    Args:
      projID (str): document id of project
      docID (str): document id of focus item, if not given focus at project
    """
    #initialize
    selectedItem = None
    self.tree = TreeView(self)
    self.model = QStandardItemModel()
    self.tree.setModel(self.model)
    self.tree.renderer.setCommunication(self.comm)
    # self.tree.contextMenuEvent().connect(self.contextMenu)  #changeEvent
    self.tree.doubleClicked.connect(self.treeDoubleClicked)
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
      nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
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
    nodeHier = self.comm.backend.db.getHierarchy(projID)
    for node in PreOrderIter(nodeHier, maxlevel=2):
      if node.is_root:         #Project header
        self.projHeader(projID)
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

  def projHeader(self, projID):
    """
    Create header of page

    Args:
      projID (str): docID of project
    """
    doc = self.comm.backend.db.getDoc(projID)
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
