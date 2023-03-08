""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTreeView, QStyledItemDelegate, QAbstractItemView  # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Slot, Qt  # pylint: disable=no-name-in-module
from anytree import PreOrderIter
from .widgetProjectLeaf import Leaf
from .style import TextButton


class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeProject.connect(self.changeProject)
    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)


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
    self.tree  = QTreeView(self)
    self.tree.setHeaderHidden(True)
    self.tree.setStyleSheet('QTreeView::branch {border-image: none;}')
    self.model = QStandardItemModel()
    self.tree.setModel(self.model)
    self.tree.setDragDropMode(QAbstractItemView.InternalMove)
    rootItem = self.model.invisibleRootItem()

    def iterateTree(nodeHier):
      """
      Recursive function to translate the hierarchical node into a tree-node

      Args:
        nodeHier (Anytree.Node): anytree node

      Returns:
        QtTreeWidgetItem: tree node
      """
      #prefill with name, doctype, id
      nodeTree = QStandardItem(nodeHier.id)  #nodeHier.name,'/'.join(nodeHier.docType),nodeHier.id])
      nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
      #New version
      print(self.comm, nodeHier.id)
      # leaf = Leaf(self.comm, nodeHier.id)  #TODO_P1 INCOMPLETE
      leaf = str(self.comm.backend.db.getDoc(nodeHier.id))  #nodeHier.name
      # https://stackoverflow.com/questions/40452400/qt-python-qtreeview-custom-widget-setdata-lose-reference-after-drag-and-dr
      nodeTree.setData(leaf, Qt.DisplayRole)
      nodeTree.setData(nodeHier.name, Qt.ToolTipRole)
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
    for idx, node in enumerate(PreOrderIter(nodeHier, maxlevel=2)):
      if node.is_root:         #Project header
        headerW = self.projHeader(projID)
      else:
        rootItem.appendRow(iterateTree(node))
    self.tree.expandAll()
    if selectedItem is not None:
      self.tree.setCurrentItem(selectedItem)
    iterator = QTreeView
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
    return headerW