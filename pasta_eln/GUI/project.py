""" Widget that shows the content of project in a electronic labnotebook """
import logging, re
from enum import Enum
from typing import Optional, Any
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QMenu, QMessageBox, QTextEdit, QScrollArea # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, Qt, QItemSelectionModel, QModelIndex # pylint: disable=no-name-in-module
from anytree import PreOrderIter, Node
from .projectTreeView import TreeView
from ..guiStyle import TextButton, Action, Label, showMessage, widgetAndLayout, iconsDocTypes, getColor
from ..miscTools import createDirName
from ..guiCommunicate import Communicate

class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    comm.changeProject.connect(self.change)
    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)
    self.tree:Optional[TreeView]             = None
    self.model:Optional[QStandardItemModel]  = None
    self.infoW:Optional[QWidget]             = None
    self.actHideDetail = QAction()
    self.actionHideItems   = QAction()
    self.actionHideProject = QAction()
    self.actionFoldAll     = QAction()
    self.projID = ''
    self.taskID = ''
    self.docProj:dict[str,Any]= {}
    self.showAll= True
    self.foldedAll = False
    self.btnAddSubfolder:Optional[TextButton] = None
    self.lineSep = 20


  def projHeader(self) -> None:
    """
    Initialize / Create header of page
    """
    self.docProj = self.comm.backend.db.getDoc(self.projID)
    # TOP LINE includes name on left, buttons on right
    _, topLineL       = widgetAndLayout('H',self.mainL,'m')
    hidden, menuTextHidden = ('     \U0001F441', 'Mark project as shown') \
                       if [b for b in self.docProj['-branch'] if False in b['show']] else \
                       ('', 'Mark project as hidden')
    topLineL.addWidget(Label(self.docProj['-name']+hidden, 'h2'))
    showStatus = '(Show all items)' if self.showAll else '(Hide hidden items)'
    topLineL.addWidget(QLabel(showStatus))
    topLineL.addStretch(1)
    # buttons in top line
    buttonW, buttonL = widgetAndLayout('H', spacing='m')
    topLineL.addWidget(buttonW, alignment=Qt.AlignTop)  # type: ignore
    self.btnAddSubfolder = TextButton('Add subfolder', self, [Command.ADD_CHILD], buttonL)
    TextButton('Edit project',                         self, [Command.EDIT],      buttonL)
    visibility = TextButton(          'Visibility',    self, [],                  buttonL)
    visibilityMenu = QMenu(self)
    self.actHideDetail = Action('Hide project details',self, [Command.REDUCE_HEIGHT_HEAD],visibilityMenu)
    menuTextItems = 'Hide hidden items' if self.showAll else 'Show hidden items'
    minimizeItems = 'Show all item details' if self.foldedAll else 'Hide all item details'
    self.actionHideItems   = Action( menuTextItems,    self, [Command.HIDE_SHOW_ITEMS],  visibilityMenu)
    self.actionHideProject = Action( menuTextHidden,   self, [Command.HIDE],             visibilityMenu)
    self.actionFoldAll     = Action( minimizeItems,    self, [Command.FOLD_ALL_ITEMS],   visibilityMenu)
    visibility.setMenu(visibilityMenu)
    more = TextButton('More',           self, [], buttonL)
    moreMenu = QMenu(self)
    Action('Scan',                      self, [Command.SCAN], moreMenu)
    for doctype in self.comm.backend.db.dataLabels:
      if doctype[0]!='x':
        if self.comm.backend.db.dataLabels[doctype] in iconsDocTypes:
          icon = iconsDocTypes[self.comm.backend.db.dataLabels[doctype]]
        else:
          icon = 'fa.asterisk'
        Action(f'table of {doctype}',   self, [Command.SHOW_TABLE, doctype], moreMenu, icon=icon)
    Action('table of unidentified',     self, [Command.SHOW_TABLE, '-'],     moreMenu, icon=iconsDocTypes['-'])
    moreMenu.addSeparator()
    Action('Delete',                    self, [Command.DELETE], moreMenu)
    more.setMenu(moreMenu)

    # Details section
    self.infoW = QScrollArea()
    self.infoW.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.infoW.setWidgetResizable(True)
    infoW_, infoL = widgetAndLayout('V')
    self.infoW.setWidget(infoW_)
    self.mainL.addWidget(self.infoW)
    # details
    tags = ', '.join([f'#{i}' for i in self.docProj['-tags']]) if '-tags' in self.docProj else ''
    infoL.addWidget(QLabel(f'Tags: {tags}'))
    countLines = 0
    for key,value in self.docProj.items():
      if key[0] in {'_','-'} or 'from ' in key or key in {'comment'}:
        continue
      labelW = QLabel(f'{key.title()}: {str(value)}')
      infoL.addWidget(labelW)
      countLines += 1
    # comment
    commentW, commentL         = widgetAndLayout('H', infoL, 's')
    labelW = QLabel('Comment:')
    # labelW.setStyleSheet('padding-top: 5px') #make "Comment:" text aligned with other content, not with text-edit
    commentL.addWidget(labelW, alignment=Qt.AlignTop)   # type: ignore[call-arg]
    comment = QTextEdit()
    comment.setMarkdown(re.sub(r'(^|\n)(#+)', r'\1##\2', self.docProj['comment'].strip()))
    bgColor = getColor(self.comm.backend, 'secondaryDark')
    fgColor = getColor(self.comm.backend, 'primaryText')
    comment.setStyleSheet(f"border: none; padding: 0px; background-color: {bgColor}; color: {fgColor}")
    comment.setReadOnly(True)
    comment.document().setTextWidth(commentW.width())
    height:int = comment.document().size().toTuple()[1] # type: ignore[index]
    comment.setFixedHeight(height)
    commentL.addWidget(comment)
    infoW_.setMaximumHeight(height + (countLines+1)*self.lineSep     +2)
    self.infoW.setMaximumHeight(height + (countLines+1)*self.lineSep +5)
    return


  @Slot(str, str)
  def change(self, projID:str, docID:str) -> None:
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
      self.tree.setCurrentIndex(selectedIndex)# Item(selectedItem)
    self.mainL.addWidget(self.tree)
    if len(nodeHier.children)>0 and self.btnAddSubfolder is not None:
      self.btnAddSubfolder.setVisible(False)
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.EDIT:
      self.comm.formDoc.emit(self.docProj)
      self.change(self.projID,'')
      #collect information and then change
      oldPath = self.comm.backend.basePath/self.docProj['-branch'][0]['path']
      if oldPath.exists():
        newPath = self.comm.backend.basePath/createDirName(self.docProj['-name'],'x0',0)
        oldPath.rename(newPath)
    elif command[0] is Command.DELETE:
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
    elif command[0] is Command.SCAN:
      self.comm.backend.scanProject(self.comm.progressBar, self.projID, self.docProj['-branch'][0]['path'])
      self.comm.changeSidebar.emit('redraw')
      showMessage(self, 'Information','Scanning finished')
    elif command[0] is Command.REDUCE_HEIGHT_HEAD:
      if self.infoW is not None and self.infoW.isHidden():
        self.infoW.show()
        self.actHideDetail.setText('Hide project details')
      elif self.infoW is not None:
        self.infoW.hide()
        self.actHideDetail.setText('Show project details')
    elif command[0] is Command.HIDE:
      self.comm.backend.db.hideShow(self.projID)
      self.docProj = self.comm.backend.db.getDoc(self.projID)
      if [b for b in self.docProj['-branch'] if False in b['show']]: # hidden->go back to project table
        self.comm.changeSidebar.emit('')
        self.comm.changeTable.emit('x0','') # go back to project table
      else:
        self.change('', '')
        self.comm.changeSidebar.emit('')
    elif command[0] is Command.FOLD_ALL_ITEMS and self.tree is not None:
      self.foldedAll = not self.foldedAll
      def recursiveRowIteration(index:QModelIndex) -> None:
        for subRow in range(self.tree.model().rowCount(index)):   # type: ignore[union-attr]
          subIndex = self.tree.model().index(subRow,0, index)     # type: ignore[union-attr]
          subItem  = self.tree.model().itemFromIndex(subIndex)    # type: ignore[union-attr]
          if self.foldedAll       and not subItem.text().endswith(' -'):
            subItem.setText(f'{subItem.text()} -')
          elif not self.foldedAll and subItem.text().endswith(' -'):
            subItem.setText(subItem.text()[:-2])
          recursiveRowIteration(subIndex)
        return
      recursiveRowIteration(self.tree.model().index(-1,0))
      if self.foldedAll:
        self.actionFoldAll.setText('Show all item details')
      else:
        self.actionFoldAll.setText('Hide all item details')
    elif command[0] is Command.HIDE_SHOW_ITEMS:
      self.showAll = not self.showAll
      self.change('','')
    elif command[0] is Command.ADD_CHILD:
      self.comm.backend.cwd = self.comm.backend.basePath/self.docProj['-branch'][0]['path']
      label = self.comm.backend.db.ontology['x1']['label'].lower()[:-1]
      self.comm.backend.addData('x1', {'-name':f'new {label}'}, [self.projID])
      self.change('','') #refresh project
    elif command[0] is Command.SHOW_TABLE:
      self.comm.changeTable.emit(command[1], self.projID)
    else:
      print("**ERROR project menu unknown:",command)
    return


  def modelChanged(self, item:QStandardItem) -> None:
    """
    Autocalled after drag-drop and other changes, record changes to backend and database directly

    Args:
      item (QStandardItem): item changed, new location
    """
    #gather old information
    db       = self.comm.backend.db
    stackOld = item.text().split('/')[:-1]
    docID    = item.text().split('/')[-1]
    maximized = True
    if docID.endswith(' -'):
      docID = docID[:34]
      maximized = False
    doc      = db.getDoc(docID)
    if '-branch' not in doc or not stackOld: #skip everything if project or not contain branch
      return
    branchOldList= [i for i in doc['-branch'] if i['stack']==stackOld]
    if len(branchOldList)!=1:
      self.change('','')
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
      stackNew.append(docIDj[:34] if docIDj.endswith(' -') else docIDj)
    stackNew = [self.projID] + stackNew[::-1]  #add project id and reverse
    childNew = item.row()
    if branchOld['path'] is not None and not branchOld['path'].startswith('http'):
      dirNameNew= createDirName(doc['-name'],doc['-type'][0],childNew) # determine path: do not create yet
      parentDir = db.getDoc(stackNew[-1])['-branch'][0]['path']
      pathNew = f'{parentDir}/{dirNameNew}'
    else:
      pathNew = branchOld['path']
    siblingsNew = db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackNew))
    siblingsNew = [i for i in siblingsNew if len(i['key'].split(' '))==len(stackNew)+1 and \
                                                   i['value'][0]>=childNew and i['value'][0]<9999]
    logging.debug('Change project: docID %s branch %i | old stack %s child %i | new stack %s child %i path %s'\
                  , docID, branchIdx, str(stackOld), childOld, str(stackNew), childNew, pathNew)
    if stackOld==stackNew and childOld==childNew:  #nothing changed, just redraw
      return
    # change item in question
    db.updateBranch(docID=docID, branch=branchIdx, stack=stackNew, path=pathNew, child=childNew)
    item.setText('/'.join(stackNew+[docID]) if maximized else '/'.join(stackNew+[f'{docID} -']) )     #update item.text() to new stack
    # change siblings
    for line in siblingsOld:
      db.updateBranch(docID=line['id'], branch=line['value'][3], child=line['value'][0]-1)
    for line in siblingsNew:
      if line['id']!=docID:
        db.updateBranch(docID=line['id'], branch=line['value'][3], child=line['value'][0]+1)
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
    if self.foldedAll:
      label += ' -'
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


class Command(Enum):
  """ Commands used in this file """
  EDIT   = 1
  DELETE = 2
  SCAN   = 3
  HIDE   = 4
  REDUCE_HEIGHT_HEAD = 5
  HIDE_SHOW_ITEMS    = 6
  FOLD_ALL_ITEMS     = 7
  ADD_CHILD          = 8
  SHOW_TABLE         = 9
