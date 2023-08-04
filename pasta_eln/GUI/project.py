""" Widget that shows the content of project in a electronic labnotebook """
import logging
from typing import Optional, Any
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QMenu, QMessageBox, QTextEdit # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, Qt, QItemSelectionModel, QModelIndex # pylint: disable=no-name-in-module
from anytree import PreOrderIter, Node
from .projectTreeView import TreeView
from ..guiStyle import TextButton, IconButton, Action, Label, showMessage, widgetAndLayout, iconsDocTypes
from ..miscTools import createDirName
from ..guiCommunicate import Communicate

class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeProject.connect(self.changeProject)
    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)
    self.tree:Optional[TreeView]             = None
    self.model:Optional[QStandardItemModel]  = None
    self.infoW:Optional[QWidget]             = None
    self.projID = ''
    self.taskID = ''
    self.docProj:dict[str,Any]= {}
    self.showAll= False
    self.foldedAll = False
    self.btnAddSubfolder:Optional[TextButton] = None


  @Slot(str, str)
  def changeProject(self, projID:str, docID:str) -> None:
    """
    What happens when user clicks to change doc-type

    Args:
      projID (str): document id of project; if empty, just refresh
      docID (str): document id of focus item, if not given focus at project
    """
    logging.debug('project:changeProject |%s|%s|',projID,docID)
    #initialize
    for i in reversed(range(self.mainL.count())): #remove old
      self.mainL.itemAt(i).widget().setParent(None)  # type: ignore
    if projID!='':
      self.projID         = projID
      self.taskID         = docID
      self.comm.projectID = projID
    selectedIndex = None
    self.model = QStandardItemModel()
    self.tree = TreeView(self, self.comm, self.model)
    # self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
    # self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
    self.model.itemChanged.connect(self.modelChanged)
    rootItem = self.model.invisibleRootItem()
    #Populate model body of change project: start recursion
    nodeHier = self.comm.backend.db.getHierarchy(self.projID, allItems=self.showAll)
    for node in PreOrderIter(nodeHier, maxlevel=2):
      if node.is_root:         #Project header
        self.projHeader()
      else:
        rootItem.appendRow(self.iterateTree(node))
    # self.tree.expandAll()
    if selectedIndex is not None:
      self.tree.selectionModel().select(selectedIndex, QItemSelectionModel.Select)
      #TODO_P4 projectTree: selection does not scroll; one cannot select a row
      self.tree.setCurrentIndex(selectedIndex)# Item(selectedItem)
    self.mainL.addWidget(self.tree)
    if len(nodeHier.children)>0 and self.btnAddSubfolder is not None:
      self.btnAddSubfolder.setVisible(False)
    return


  def modelChanged(self, item:QStandardItem) -> None:
    """
    After drag-drop, record changes to backend and database directly

    Args:
      item (QStandardItem): item changed, new location
    """
    #gather old information
    db       = self.comm.backend.db
    stackOld = item.text().split('/')[:-1]
    docID    = item.text().split('/')[-1]
    maximized = True
    if docID.endswith(' -'):
      docID = docID[:-2]
      maximized = False
    doc      = db.getDoc(docID)
    if '-branch' not in doc:
      return
    branchOldList= [i for i in doc['-branch'] if i['stack']==stackOld]
    if len(branchOldList)!=1:
      self.changeProject('','')
      return
    branchOld = branchOldList[0]
    childOld = branchOld['child']
    branchIdx= doc['-branch'].index(branchOld)
    siblingsOld = db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackOld))
    siblingsOld = [i for i in siblingsOld if len(i['key'].split(' '))==len(stackOld)+1 and \
                                                  i['value'][0]>branchOld['child'] and i['value'][0]<9999]
    #gather new information
    stackNew = []  #create reversed
    currentItem = item
    while currentItem.parent() is not None:
      currentItem = currentItem.parent()
      docIDj = currentItem.text().split('/')[-1]
      stackNew.append(docIDj[:-2] if docIDj.endswith(' -') else docIDj)
    stackNew = [self.projID] + stackNew[::-1]  #add project id and reverse
    childNew = item.row()
    if not branchOld['path'].startswith('http'):
      dirNameNew= createDirName(doc['-name'],doc['-type'][0],childNew)
      parentDir = db.getDoc(stackNew[-1])['-branch'][0]['path']
      pathNew = f'{parentDir}/{dirNameNew}'
    else:
      pathNew = branchOld['path']
    siblingsNew = db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackNew))
    siblingsNew = [i for i in siblingsNew if len(i['key'].split(' '))==len(stackNew)+1 and \
                                                   i['value'][0]>=childNew and i['value'][0]<9999]
    logging.debug('Change project: docID -old- -new- %s|%s  %i|%s %i %s', docID, str(stackOld), branchIdx, str(stackNew), childNew, pathNew)
    if stackOld==stackNew and childOld==childNew:  #nothing changed, just redraw
      return
    # change item in question
    db.updateBranch(docID=docID, branch=branchIdx, stack=stackNew, path=pathNew, child=childNew)
    item.setText('/'.join(stackNew+[docID]) if maximized else '/'.join(stackNew+[docID+' -']) )     #update item.text() to new stack
    # change siblings
    for line in siblingsOld:
      db.updateBranch(docID=line['id'], branch=line['value'][3], child=line['value'][0]-1)
    for line in siblingsNew:
      if line['id']!=docID:
        db.updateBranch(docID=line['id'], branch=line['value'][3], child=line['value'][0]+1)
    return


  def projHeader(self) -> None:
    """
    Create header of page
    """
    self.docProj = self.comm.backend.db.getDoc(self.projID)
    _, topLineL       = widgetAndLayout('H',self.mainL)  #topLine includes name on left, buttons on right
    hidden = '     \U0001F441' if [b for b in self.docProj['-branch'] if False in b['show']] else ''
    topLineL.addWidget(Label(self.docProj['-name']+hidden, 'h2'))
    topLineL.addStretch(1)

    buttonW, buttonL = widgetAndLayout('H', spacing='m')
    topLineL.addWidget(buttonW, alignment=Qt.AlignTop)  # type: ignore
    self.btnAddSubfolder = TextButton('Add subfolder', self.executeAction, buttonL, name='addChild')
    TextButton('Edit project',      self.executeAction, buttonL, name='editProject')
    visibility = TextButton('Visibility',None, buttonL)
    visibilityMenu = QMenu(self)
    Action('Hide/show project details', self.executeAction, visibilityMenu, self, name='projReduceWidth')
    Action('Hide/show hidden subitems', self.executeAction, visibilityMenu, self, name='hideShow')
    Action('Hide/show entire project',  self.executeAction, visibilityMenu, self, name='projHideShow')
    Action('Minimize/Maximize subitems',self.executeAction, visibilityMenu, self, name='allFold')
    visibility.setMenu(visibilityMenu)
    more = TextButton('More',None, buttonL)
    moreMenu = QMenu(self)
    Action('Scan',                  self.executeAction, moreMenu, self, name='scanProject')
    for doctype in self.comm.backend.db.dataLabels:
      if doctype[0]!='x':
        icon = iconsDocTypes[self.comm.backend.db.dataLabels[doctype]]
        Action(f'table of {doctype}', self.executeAction, moreMenu, self, name=f'_doctype_{doctype}', icon=icon)
    Action('table of unidentified', self.executeAction, moreMenu, self, name='_doctype_-', icon=iconsDocTypes['-'])
    moreMenu.addSeparator()
    Action('Delete',                self.executeAction, moreMenu, self, name='deleteProject')
    more.setMenu(moreMenu)

    self.infoW, infoL         = widgetAndLayout('V', self.mainL)
    tags = ', '.join([f'#{i}' for i in self.docProj['-tags']]) if '-tags' in self.docProj else ''
    infoL.addWidget(QLabel(f'Tags: {tags}'))
    for key,value in self.docProj.items():
      if key[0] in ['_','-'] or (key=='comment' and '\n' in value):
        continue
      infoL.addWidget(QLabel(f'{key}: {str(value)}'))
    if 'comment' in self.docProj and '\n' in self.docProj['comment']:     #format nicely
      # comment = QTextEdit()  #TODO_P2 render comment nicely without screwing up the rest
      # comment.setMarkdown(self.docProj['comment'])
      # comment.setReadOnly(True)
      # comment.setFixedHeight(200)
      # infoL.addWidget(comment)
      infoL.addWidget(QLabel(self.docProj['comment']))
    return


  #TODO_P4 projectTree: select multiple items to edit... What is use case
  #TODO_P4 projectTree: allow right click on measurement to change recipe
  def executeAction(self) -> None:
    """ Any action by the buttons at the top of the page """
    if hasattr(self.sender(), 'data'):  #action
      menuName = self.sender().data()
    else:                               #button
      menuName = self.sender().accessibleName()
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
        self.comm.changeSidebar.emit('redraw')
        self.comm.changeTable.emit('x0','')
    elif menuName == 'scanProject':
      self.comm.backend.scanProject(self.comm.progressBar, self.projID, self.docProj['-branch'][0]['path'])
      self.comm.changeSidebar.emit('redraw')
      showMessage(self, 'Information','Scanning finished')
    elif menuName == 'projReduceWidth':
      if self.infoW is not None and self.infoW.isHidden():
        self.infoW.show()
      elif self.infoW is not None:
        self.infoW.hide()
    elif menuName == 'projHideShow':
      self.comm.backend.db.hideShow(self.projID)
      self.comm.changeSidebar.emit('')
      self.comm.changeTable.emit('x0','') # go back to project table
    elif menuName == 'allFold' and self.tree is not None:
      self.foldedAll = not self.foldedAll
      def recursiveRowIteration(index:QModelIndex) -> None:
        if self.tree is not None:
          for subRow in range(self.tree.model().rowCount(index)):
            subIndex = self.tree.model().index(subRow,0, index)
            subItem  = self.tree.model().itemFromIndex(subIndex)
            if self.foldedAll:
              subItem.setText(f'{subItem.text()} -')
            elif subItem.text().endswith(' -'):
              subItem.setText(subItem.text()[:-2])
            recursiveRowIteration(subIndex)
        return
      recursiveRowIteration(self.tree.model().index(-1,0))
    elif menuName == 'hideShow':
      self.showAll = not self.showAll
      self.changeProject('','')
    elif menuName == 'addChild':
      self.comm.backend.cwd = self.comm.backend.basePath/self.docProj['-branch'][0]['path']
      self.comm.backend.addData('x1', {'-name':'new folder'}, [self.projID])
      self.comm.changeProject.emit('','') #refresh project
    elif menuName.startswith('_doctype_'):
      self.comm.changeTable.emit(menuName[9:], self.projID)
    else:
      print(f"undefined menu / action |{menuName}|")
    return


  def iterateTree(self, nodeHier:Node) -> QStandardItem:
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
      nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled) # type: ignore
    else:
      nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled) # type: ignore
    children = []
    for childHier in nodeHier.children:
      childTree = self.iterateTree(childHier)
      children.append(childTree)
    if children:
      nodeTree.appendRows(children)
    return nodeTree