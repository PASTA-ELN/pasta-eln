""" Widget that shows the content of project in a electronic labnotebook """
from pathlib import Path
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QStyledItemDelegate  # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem    # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, Qt                            # pylint: disable=no-name-in-module
from anytree import PreOrderIter
from .widgetProjectLeafRenderer import ProjectLeafRenderer
from .widgetTreeView import TreeView
from .style import TextButton
from .miscTools import createDirName


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


  def modelChanged(self, item):
    """
    After drag-drop, record changes to backend and database directly

    Args:
      item (QStandardItem): item changed, new location
    """
    print('\n')
    #old information
    stackOld = item.text().split('/')[:-1]
    docID    = item.text().split('/')[-1]
    doc      = self.comm.backend.db.getDoc(docID)
    branchOld= [i for i in doc['-branch'] if i['stack']==stackOld][0]
    branchIdx= doc['-branch'].index(branchOld)
    siblingsOld = self.comm.backend.db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackOld))
    siblingsOld = [i for i in siblingsOld if len(i['key'].split(' '))==len(stackOld)+1 and \
                                            i['value'][0]>branchOld['child']]
    print('OLD INFORMATION', docID, stackOld, branchIdx)
    print(siblingsOld)
    #new information
    stackNew = []  #create reversed
    currentItem = item
    while currentItem.parent() is not None:
      currentItem = currentItem.parent()
      stackNew.append(currentItem.text().split('/')[-1])
    stackNew = [self.projID] + stackNew[::-1]  #add project id and reverse
    childNew = item.row()
    dirNameNew= createDirName(doc['-name'],doc['-type'][0],childNew)
    parentDir = self.comm.backend.db.getDoc(stackNew[-1])['-branch'][0]['path']
    pathNew  = parentDir+'/'+dirNameNew
    siblingsNew = self.comm.backend.db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackNew))
    siblingsNew = [i for i in siblingsNew if len(i['key'].split(' '))==len(stackNew)+1 and \
                                             i['value'][0]>=childNew]
    print('\nNEW INFORMATION', docID,stackNew,childNew, pathNew)
    print(siblingsNew)
    #change
    # pathOld = Path(self.comm.backend.basePath)/branchOld['path']
    # if pathOld.exists():
    #   pathOld.rename(Path(self.comm.backend.basePath)/pathNew)

    #change sibling childNum: don't if already 9999
    #fast change using new databasefunction

    #update item.text() to new stack
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
    for i in reversed(range(self.mainL.count())): #remove old
      self.mainL.itemAt(i).widget().setParent(None)
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
      label = '/'.join([i.id for i in nodeHier.ancestors]+[nodeHier.id])
      nodeTree = QStandardItem(label)  #nodeHier.name,'/'.join(nodeHier.docType),nodeHier.id])
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
