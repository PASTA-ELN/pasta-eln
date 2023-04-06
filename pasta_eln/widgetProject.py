""" Widget that shows the content of project in a electronic labnotebook """
import logging
from pathlib import Path
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QStyledItemDelegate, QAbstractItemView, \
                              QMenu, QMessageBox # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem    # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, Qt, QItemSelectionModel      # pylint: disable=no-name-in-module
from anytree import PreOrderIter
from .widgetProjectLeafRenderer import ProjectLeafRenderer
from .widgetProjectTreeView import TreeView
from .style import TextButton, Action, showMessage
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
    self.taskID = ''
    self.docProj= {}
    self.showAll= False


  @Slot(str)
  def changeProject(self, projID, docID):
    """
    What happens when user clicks to change doc-type

    Args:
      projID (str): document id of project; if empty, just refresh
      docID (str): document id of focus item, if not given focus at project
    """
    #initialize
    for i in reversed(range(self.mainL.count())): #remove old
      self.mainL.itemAt(i).widget().setParent(None)
    if projID!='':
      self.projID = projID
      self.taskID = docID
    selectedIndex = None
    self.model = QStandardItemModel()
    self.tree = TreeView(self, self.comm, self.model)
    # self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
    # self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
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
      if self.taskID==nodeHier.id:
        nonlocal selectedIndex
        selectedIndex = nodeTree.index()
      children = []
      for childHier in nodeHier.children:
        childTree = iterateTree(childHier)
        children.append(childTree)
      if len(children)>0:
        nodeTree.appendRows(children)
      return nodeTree

    #Populate model body of change project: start recursion
    nodeHier = self.comm.backend.db.getHierarchy(self.projID, allItems=self.showAll)
    for node in PreOrderIter(nodeHier, maxlevel=2):
      if node.is_root:         #Project header
        self.projHeader()
      else:
        rootItem.appendRow(iterateTree(node))
    self.tree.expandAll()
    if selectedIndex is not None:
      self.tree.selectionModel().select(selectedIndex, QItemSelectionModel.Select)
      #TODO_P3 convenience: selection does not scroll; one cannot select a row
      self.tree.setCurrentIndex(selectedIndex)# Item(selectedItem)
    self.mainL.addWidget(self.tree)
    return


  def modelChanged(self, item):
    """
    After drag-drop, record changes to backend and database directly

    Args:
      item (QStandardItem): item changed, new location
    """
    #gather old information
    db       = self.comm.backend.db
    stackOld = item.text().split('/')[:-1]
    docID    = item.text().split('/')[-1]
    if docID.endswith(' -'):
      docID = docID[:-2]
    doc      = db.getDoc(docID)
    branchOld= [i for i in doc['-branch'] if i['stack']==stackOld][0]
    childOld = branchOld['child']
    branchIdx= doc['-branch'].index(branchOld)
    siblingsOld = db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackOld))
    siblingsOld = [i for i in siblingsOld if len(i['key'].split(' '))==len(stackOld)+1 and \
                                            i['value'][0]>branchOld['child']]
    logging.debug('OLD INFORMATION '+docID+' '+str(stackOld)+'  '+str(branchIdx))
    #gather new information
    stackNew = []  #create reversed
    currentItem = item
    while currentItem.parent() is not None:
      currentItem = currentItem.parent()
      stackNew.append(currentItem.text().split('/')[-1])
    stackNew = [self.projID] + stackNew[::-1]  #add project id and reverse
    childNew = item.row()
    dirNameNew= createDirName(doc['-name'],doc['-type'][0],childNew)
    parentDir = db.getDoc(stackNew[-1])['-branch'][0]['path']
    pathNew  = parentDir+'/'+dirNameNew
    siblingsNew = db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackNew))
    siblingsNew = [i for i in siblingsNew if len(i['key'].split(' '))==len(stackNew)+1 and \
                                             i['value'][0]>=childNew]
    logging.debug('NEW INFORMATION '+docID+' '+str(stackNew)+'  '+str(childNew)+' '+pathNew)
    if stackOld==stackNew and childOld==childNew:  #nothing changed, just redraw
      return
    # change siblings
    for line in siblingsOld:
      if line['value'][0]<9999:
        pathOldSib, pathNewSib = db.updateBranch(docID=line['id'], branch=line['value'][3], child=line['value'][0]-1)
        (Path(self.comm.backend.basePath)/pathOldSib).rename(Path(self.comm.backend.basePath)/pathNewSib)
    for line in siblingsNew:
      if line['value'][0]<9999:
        pathOldSib, pathNewSib = db.updateBranch(docID=line['id'], branch=line['value'][3], child=line['value'][0]+1)
        (Path(self.comm.backend.basePath)/pathOldSib).rename(Path(self.comm.backend.basePath)/pathNewSib)
    #change item in question
    pathOld = Path(self.comm.backend.basePath)/branchOld['path']
    if pathOld.exists():
      pathOld.rename(Path(self.comm.backend.basePath)/pathNew)
    db.updateBranch(docID=docID, branch=branchIdx, stack=stackNew, path=pathNew, child=childNew)
    item.setText('/'.join(stackNew+[docID]))     #update item.text() to new stack
    return


  def btnEvent(self):
    """ Click button on top of project page """
    btnName = self.sender().accessibleName()
    if btnName == 'projHide':
      if self.bodyW.isHidden():
        self.bodyW.show()
      else:
        self.bodyW.hide()
    elif btnName == 'hideShow':
      self.showAll = not self.showAll
      self.changeProject('','')
    elif btnName == 'addChild':
      self.comm.backend.cwd = Path(self.comm.backend.basePath)/self.docProj['-branch'][0]['path']
      self.comm.backend.addData('x1', {'-name':'folder 1', 'childNum':0}, [self.projID])
      self.comm.changeProject.emit('','') #refresh project
    return


  def projHeader(self):
    """
    Create header of page
    """
    self.docProj = self.comm.backend.db.getDoc(self.projID)
    headerW = QWidget()  # Leaf(self.comm, node.id)
    headerL = QVBoxLayout(headerW)
    topbarW = QWidget()
    topbarL = QHBoxLayout(topbarW)
    hidden = '     \U0001F441' if len([b for b in self.docProj['-branch'] if False in b['show']])>0 else ''
    topbarL.addWidget(QLabel(self.docProj['-name']+hidden))
    TextButton('Reduce',    self.btnEvent, topbarL, 'projHide', checkable=True)
    TextButton('Hide/Show', self.btnEvent, topbarL, 'hideShow')
    TextButton('Add child', self.btnEvent, topbarL, 'addChild')
    more = TextButton('More',None, topbarL)
    moreMenu = QMenu(self)
    Action('Scan',   self.executeAction, moreMenu, self, name='scanProject')
    Action('Edit',   self.executeAction, moreMenu, self, name='editProject')
    Action('Delete', self.executeAction, moreMenu, self, name='deleteProject')
    more.setMenu(moreMenu)

    headerL.addWidget(topbarW)
    self.bodyW   = QWidget()
    bodyL   = QVBoxLayout(self.bodyW)
    tags = ', '.join(self.docProj['tags']) if 'tags' in self.docProj else ''
    bodyL.addWidget(QLabel('Tags: '+tags))
    for key,value in self.docProj.items():
      if key[0] in ['_','-']:
        continue
      bodyL.addWidget(QLabel(key+': '+str(value)))
    headerL.addWidget(self.bodyW)
    self.mainL.addWidget(headerW)
    return


  def executeAction(self):
    """ Any action by the buttons at the top of the page """
    menuName = self.sender().data()
    if menuName=='editProject':
      self.comm.formDoc.emit(self.docProj)
      self.comm.changeProject.emit(self.projID,'')
      #collect information and then change
      oldPath = self.comm.backend.basePath/self.docProj['-branch'][0]['path']
      if oldPath.exists():
        newPath = self.comm.backend.basePath/createDirName(self.docProj['-name'],'x0',0)
        oldPath.rename(newPath)
    elif menuName=='deleteProject':
      ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete project?',\
                                 QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
      if ret==QMessageBox.StandardButton.Yes:
        #delete database and rename folder
        doc = self.comm.backend.db.remove(self.projID)
        if '-branch' in doc and len(doc['-branch'])>0 and 'path' in doc['-branch'][0]:
          oldPath = self.comm.backend.basePath/doc['-branch'][0]['path']
          newPath = self.comm.backend.basePath/('trash_'+doc['-branch'][0]['path'])
          oldPath.rename(newPath)
        #update sidebar, show projects
        self.comm.changeSidebar.emit()
        self.comm.changeTable.emit('x0','')
    elif menuName == 'scanProject':
      self.comm.backend.scanProject(self.projID, self.docProj['-branch'][0]['path'])
      self.comm.changeProject.emit(self.projID,'')
      showMessage(self, 'Information','Scanning finished')
    else:
      print("undefined menu / action",menuName)
    return
