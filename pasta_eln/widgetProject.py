""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module
from anytree import PreOrderIter
from .widgetProjectLeaf import Leaf

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
    treeW = QTreeWidget()
    treeW.setColumnCount(1)
    treeW.setHeaderHidden(True)
    selectedItem = None

    def iterateTree(nodeHier):
      """
      Recursive function to translate the hierarchical node into a tree-node

      Args:
        nodeHier (Anytree.Node): anytree node

      Returns:
        QtTreeWidgetItem: tree node
      """
      #prefill with name, doctype, id
      nodeTree = QTreeWidgetItem([nodeHier.id])  #nodeHier.name,'/'.join(nodeHier.docType),nodeHier.id])
      if docID==nodeHier.id:
        nonlocal selectedItem
        selectedItem = nodeTree
      children = []
      for childHier in nodeHier.children:
        childTree = iterateTree(childHier)
        children.append(childTree)
      if len(children)>0:
        nodeTree.insertChildren(0,children)
      return nodeTree

    #body of change project: start recursion
    nodeHier = self.comm.backend.db.getHierarchy(projID)
    for idx, node in enumerate(PreOrderIter(nodeHier, maxlevel=2)):
      if node.is_root:
        header = Leaf(self.comm, node.id)
        self.mainL.addWidget(header)
      else:
        treeW.insertTopLevelItem(idx-1, iterateTree(node))
    treeW.expandAll()
    if selectedItem is not None:
      treeW.setCurrentItem(selectedItem)

    # add custom styled leafs
    iterator = QTreeWidgetItemIterator(treeW)
    while iterator.value():
      item = iterator.value()
      docID= item.text(0)
      item.setText(0,'') #remove text
      treeW.setItemWidget(item, 0, Leaf(self.comm, docID))
      iterator += 1

    self.mainL.addWidget(treeW)
    return
