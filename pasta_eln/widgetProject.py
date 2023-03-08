""" Widget that shows the content of project in a electronic labnotebook """
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot   # pylint: disable=no-name-in-module
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
    doc = self.comm.backend.db.getDoc(projID)
    for i in reversed(range(self.mainL.count())):
      self.mainL.itemAt(i).widget().setParent(None)
    treeW = QTreeWidget()
    treeW.setColumnCount(1)
    treeW.setHeaderHidden(True)
    treeW.setStyleSheet('QTreeView::branch {border-image: none;}')
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
      if node.is_root:         #Project header
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


  def btnEvent(self):
    btnName = self.sender().accessibleName()
    if btnName == 'projHide':
      if self.bodyW.isHidden():
        self.bodyW.show()
      else:
        self.bodyW.hide()
    return