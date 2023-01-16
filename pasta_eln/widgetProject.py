""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module
from anytree import PreOrderIter, PostOrderIter

class Project(QTreeWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    comm.changeProject.connect(self.changeProject)
    self.setColumnCount(1)
    self.setHeaderLabels(["Name"])


  @Slot(str)
  def changeProject(self, projID, docID):
    """
    What happens when user clicks to change doc-type

    Args:
      projID (str): document id of project
      docID (str): document id of focus item, if not given focus at project
    """
    selectedItem = None

    def iterateTree(nodeHier):
      """
      Recursive function to translate the hierarchical node into a tree-node

      Args:
        nodeHier (Anytree.Node): anytree node

      Returns:
        QtTreeWidgetItem: tree node
      """
      nodeTree = QTreeWidgetItem([nodeHier.name+' | '+'/'.join(nodeHier.docType)+' | '+nodeHier.id])
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

    nodeHier = self.comm.backend.db.getHierarchy(projID)
    self.insertTopLevelItem(0, iterateTree(nodeHier))
    self.expandAll()
    if selectedItem is not None:
      self.setCurrentItem(selectedItem)
    return
