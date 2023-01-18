""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module
from .widgetProjectLeaf import Leaf

class Project(QTreeWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeProject.connect(self.changeProject)

  @Slot(str)
  def changeProject(self, projID, docID):
    """
    What happens when user clicks to change doc-type

    Args:
      projID (str): document id of project
      docID (str): document id of focus item, if not given focus at project
    """
    #initialize
    self.clear()
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
      self.setColumnCount(1)
      self.setHeaderLabels([''])
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
    self.insertTopLevelItem(0, iterateTree(nodeHier))
    self.expandAll()
    if selectedItem is not None:
      self.setCurrentItem(selectedItem)

    # do something fancy
    iterator = QTreeWidgetItemIterator(self)
    while iterator.value():
      item = iterator.value()
      docID= item.text(0)
      item.setText(0,'') #remove text
      self.setItemWidget(item, 0, Leaf(self.comm, docID))
      iterator += 1
    return
