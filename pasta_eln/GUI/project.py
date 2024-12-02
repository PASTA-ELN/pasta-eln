""" Widget that shows the content of project in a electronic labnotebook """
import logging, importlib
from enum import Enum
from pathlib import Path
from typing import Optional, Any
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QMenu, QMessageBox, QTextEdit              # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction                                   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot, Qt, QItemSelectionModel, QModelIndex                                  # pylint: disable=no-name-in-module
from anytree import PreOrderIter, Node
from .projectTreeView import TreeView
from ..guiStyle import TextButton, Action, Label, showMessage, widgetAndLayout
from ..fixedStringsJson import DO_NOT_RENDER
from ..stringChanges import createDirName
from ..handleDictionaries import doc2markdown
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
    self.allDetails                          = QTextEdit()
    self.actHideDetail                       = QAction()
    self.actionFoldAll                       = QAction()
    self.projID = ''
    self.docProj:dict[str,Any]= {}
    self.showAll= True
    self.showDetailsAll = False
    self.btnAddSubfolder:Optional[TextButton] = None
    self.lineSep = 20


  def projHeader(self) -> None:
    """
    Initialize / Create header of page
    """
    self.docProj = self.comm.backend.db.getDoc(self.projID)
    dataHierarchyNode = self.comm.backend.db.dataHierarchy('x0', 'meta')
    # remove if still there
    for i in reversed(range(self.mainL.count())): #remove old
      self.mainL.itemAt(i).widget().setParent(None)
    logging.debug('ProjectView elements at 2: %i',self.mainL.count())
    # TOP LINE includes name on left, buttons on right
    _, topLineL       = widgetAndLayout('H',self.mainL,'m')
    hidden, menuTextHidden = ('     \U0001F441', 'Mark project as shown') \
                       if [b for b in self.docProj['branch'] if False in b['show']] else \
                       ('', 'Mark project as hidden')
    topLineL.addWidget(Label(self.docProj['name']+hidden, 'h2'))
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
    self.actHideDetail = Action('Hide project details',self, [Command.SHOW_PROJ_DETAILS],visibilityMenu)
    menuTextItems = 'Hide hidden items' if self.showAll else 'Show hidden items'
    minimizeItems = 'Show all item details' if self.showDetailsAll else 'Hide all item details'
    Action( menuTextItems,    self, [Command.HIDE_SHOW_ITEMS],  visibilityMenu)
    Action( menuTextHidden,   self, [Command.HIDE],             visibilityMenu)
    self.actionFoldAll     = Action( minimizeItems,    self, [Command.SHOW_DETAILS],     visibilityMenu)
    visibility.setMenu(visibilityMenu)
    more = TextButton('More',           self, [], buttonL)
    moreMenu = QMenu(self)
    Action('Scan',                      self, [Command.SCAN], moreMenu)
    for doctype in self.comm.backend.db.dataHierarchy('', ''):
      if doctype[0]!='x':
        icon = self.comm.backend.db.dataHierarchy(doctype, 'icon')[0]
        icon = 'fa5s.asterisk' if icon=='' else icon
        Action(f'table of {doctype}',   self, [Command.SHOW_TABLE, doctype], moreMenu, icon=icon)
    Action('table of unidentified',     self, [Command.SHOW_TABLE, '-'],     moreMenu, icon='fa5.file')
    moreMenu.addSeparator()
    if projectAddOns := self.comm.backend.configuration.get('projectAddOns',''):
      for label, description in projectAddOns.items():
        Action(description, self, [Command.ADD_ON, label], moreMenu)
      moreMenu.addSeparator()
    Action('Delete project',            self, [Command.DELETE], moreMenu)
    more.setMenu(moreMenu)

    # Details section
    # self.infoW = QScrollArea()
    # self.infoW.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    # self.infoW.setWidgetResizable(True)
    self.allDetails.setMarkdown(doc2markdown(self.docProj, DO_NOT_RENDER, dataHierarchyNode, self))
    if not self.docProj['gui'][0]:
      self.allDetails.hide()
      self.actHideDetail.setText('Show project details')
    self.allDetails.resizeEvent = self.commentResize # type: ignore
    bgColor = self.comm.palette.get('secondaryDark', 'background-color')
    fgColor = self.comm.palette.get('secondaryText', 'color')
    self.allDetails.setStyleSheet(f"border: none; padding: 0px; {bgColor} {fgColor}")
    self.allDetails.setReadOnly(True)
    self.mainL.addWidget(self.allDetails)
    self.commentResize(None)
    return


  def commentResize(self, _:Any) -> None:
    """ called if comment is resized because widget initially/finally knows its size
    - comment widget is hard coded size it depends on the rendered size
    """
    if self.allDetails is None:
      return
    self.allDetails.document().setTextWidth(self.width())
    height:int = self.allDetails.document().size().toTuple()[1]  # type: ignore[index]
    self.allDetails.setMaximumHeight(height)
    return


  @Slot(str, str)                                   # type: ignore[arg-type]
  def change(self, projID:str, docID:str) -> None:
    """
    What happens when user clicks to change project

    Args:
      projID (str): document id of project; if empty, just refresh
      docID (str): document id of focus item, if not given focus at project
    """
    logging.debug('project:changeProject |%s|%s|',projID,docID)
    #initialize
    for i in reversed(range(self.mainL.count())): #remove old
      self.mainL.itemAt(i).widget().setParent(None)
    logging.debug('ProjectView elements at 1: %i',self.mainL.count())
    if projID!='':
      self.projID         = projID
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
    # collapse / expand depending on stored value
    # by iterating each leaf, and converting item and index
    root = self.model.invisibleRootItem()
    self.setExpandedState(root)
    if selectedIndex is not None:
      self.tree.selectionModel().select(selectedIndex, QItemSelectionModel.Select)
      self.tree.setCurrentIndex(selectedIndex)# Item(selectedItem)
    self.mainL.addWidget(self.tree)
    logging.debug('ProjectView elements at 4: %i',self.mainL.count())
    if len(nodeHier.children)>0 and self.btnAddSubfolder is not None:
      self.btnAddSubfolder.setVisible(False)
    self.tree.expanded.connect(lambda index: self.actionExpandCollapse(index, True))
    self.tree.collapsed.connect(lambda index: self.actionExpandCollapse(index, False))
    return


  def setExpandedState(self, node:QStandardItem) -> None:
    """ Recursive function to set the expanded state of nodes

    Args:
      node (QStandardItem): node to process
    """
    if self.model is None or self.tree is None:
      return
    for iRow in range(node.rowCount()):
      item = node.child(iRow)
      data = item.data(role=Qt.ItemDataRole.UserRole+1)
      if data['hierStack'].split('/')[-1][0]=='x':
        index = self.model.indexFromItem(item)
        self.tree.setExpanded(index, data['gui'][1])
      self.setExpandedState(item)
    return


  def actionExpandCollapse(self, index:QModelIndex, flag:bool) -> None:
    """ Action upon expansion or collapsing of folder (showing its children)

    Args:
      index (QModelIndex): index that send the signal
      flag (bool): true=expand=show-children, false=collapse=hide-children
    """
    if self.model is None:
      return
    gui  = [index.data(Qt.ItemDataRole.UserRole+1)['gui'][0]]+[flag]
    docID = index.data(Qt.ItemDataRole.UserRole+1)['hierStack'].split('/')[-1]
    self.model.itemFromIndex(index).setData({ **index.data(Qt.ItemDataRole.UserRole+1), **{'gui':gui}})
    self.comm.backend.db.setGUI(docID, gui)
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
      oldPath = self.comm.backend.basePath/self.docProj['branch'][0]['path']
      if oldPath.is_dir():
        newPath = self.comm.backend.basePath/createDirName(self.docProj['name'],'x0',0)
        oldPath.rename(newPath)
      self.comm.changeSidebar.emit('redraw')
    elif command[0] is Command.DELETE:
      ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete project?', \
                      QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                      QMessageBox.StandardButton.No)
      if ret==QMessageBox.StandardButton.Yes:
        #delete database and rename folder
        doc = self.comm.backend.db.remove(self.projID)
        if 'branch' in doc and len(doc['branch'])>0 and 'path' in doc['branch'][0]:
          oldPath = self.comm.backend.basePath/doc['branch'][0]['path']
          newPath = self.comm.backend.basePath/('trash_'+doc['branch'][0]['path'])
          nextIteration = 1
          while newPath.is_dir():
            newPath = self.comm.backend.basePath/(f"trash_{doc['branch'][0]['path']}_{nextIteration}")
            nextIteration += 1
          oldPath.rename(newPath)
        # go through children, remove from DB
        children = self.comm.backend.db.getView('viewHierarchy/viewHierarchy', startKey=self.projID)
        for line in children:
          self.comm.backend.db.remove(line['id'])
        #update sidebar, show projects
        self.comm.changeSidebar.emit('redraw')
        self.comm.changeTable.emit('x0','')
    elif command[0] is Command.SCAN:
      for _ in range(2):  #scan twice: convert, extract
        self.comm.backend.scanProject(self.comm.progressBar, self.projID, self.docProj['branch'][0]['path'])
      self.comm.changeProject.emit(self.projID,'')
      showMessage(self, 'Information','Scanning finished')
    elif command[0] is Command.SHOW_PROJ_DETAILS:
      self.docProj['gui'][0] = not self.docProj['gui'][0]
      self.comm.backend.db.setGUI(self.projID, self.docProj['gui'])
      if self.allDetails is not None and self.allDetails.isHidden():
        self.allDetails.show()
        self.actHideDetail.setText('Hide project details')
      elif self.allDetails is not None:
        self.allDetails.hide()
        self.actHideDetail.setText('Show project details')
    elif command[0] is Command.HIDE:
      self.comm.backend.db.hideShow(self.projID)
      self.docProj = self.comm.backend.db.getDoc(self.projID)
      if [b for b in self.docProj['branch'] if False in b['show']]: # hidden->go back to project table
        self.comm.changeSidebar.emit('')
        self.comm.changeTable.emit('x0','') # go back to project table
      else:
        self.change('', '')
        self.comm.changeSidebar.emit('')
    elif command[0] is Command.SHOW_DETAILS and self.tree is not None:
      def recursiveRowIteration(index:QModelIndex) -> None:
        for subRow in range(self.tree.model().rowCount(index)):   # type: ignore[union-attr]
          subIndex = self.tree.model().index(subRow,0, index)     # type: ignore[union-attr]
          subItem  = self.tree.model().itemFromIndex(subIndex)    # type: ignore[union-attr]
          docID    = subItem.data()['hierStack'].split('/')[-1]
          gui      = subItem.data()['gui']
          gui[0]   = self.showDetailsAll
          subItem.setData({ **subItem.data(), **{'gui':gui}})
          self.comm.backend.db.setGUI(docID, gui)
          recursiveRowIteration(subIndex)
      recursiveRowIteration(self.tree.model().index(-1,0))
      self.showDetailsAll = not self.showDetailsAll
      if self.showDetailsAll:
        self.actionFoldAll.setText('Show all item details')
      else:
        self.actionFoldAll.setText('Hide all item details')
    elif command[0] is Command.HIDE_SHOW_ITEMS:
      self.showAll = not self.showAll
      self.change('','')
    elif command[0] is Command.ADD_CHILD:
      self.comm.backend.cwd = self.comm.backend.basePath/self.docProj['branch'][0]['path']
      self.comm.backend.addData('x1', {'name':'new item'}, [self.projID])
      self.change('','') #refresh project
    elif command[0] is Command.SHOW_TABLE:
      self.comm.changeTable.emit(command[1], self.projID)
    elif command[0] is Command.ADD_ON:
      module      = importlib.import_module(command[1])
      module.main(self.comm.backend, self.projID, self)
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
    if not item.data():
      return
    stackOld = item.data()['hierStack'].split('/')[:-1]
    docID    = item.data()['hierStack'].split('/')[-1]
    doc      = db.getDoc(docID)
    if 'branch' not in doc or not stackOld: #skip everything if project or not contain branch
      return
    branchOldList= [i for i in doc['branch'] if i['stack']==stackOld]
    if len(branchOldList)!=1:
      self.change('','')
      return
    branchOld = branchOldList[0]
    childOld = branchOld['child']
    siblingsOld = db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackOld))
    siblingsOld = [i for i in siblingsOld if len(i['key'].split(' '))==len(stackOld)+1 and \
                                                  i['value'][0]>branchOld['child'] and i['value'][0]<9999]
    #gather new information
    stackNew = []  #create reversed
    currentItem = item
    while currentItem.parent() is not None:
      currentItem = currentItem.parent()
      docIDj = currentItem.data()['hierStack'].split('/')[-1]
      stackNew.append(docIDj)
    stackNew = [self.projID] + stackNew[::-1]  #add project id and reverse
    childNew = item.row()
    if branchOld['path'] is not None and not branchOld['path'].startswith('http'):
      if doc['type'][0][0]=='x':
        dirNameNew= createDirName(doc['name'],doc['type'][0],childNew) # create path name: do not create directory on storage yet
      else:
        dirNameNew= Path(branchOld['path']).name                         # use old name
      parentDir = db.getDoc(stackNew[-1])['branch'][0]['path']
      pathNew = f'{parentDir}/{dirNameNew}'
    else:
      pathNew = branchOld['path']
    siblingsNew = db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(stackNew))
    siblingsNew = [i for i in siblingsNew if len(i['key'].split(' '))==len(stackNew)+1 and \
                                                   i['value'][0]>=childNew and i['value'][0]<9999]
    logging.debug('Change project: docID %s | old stack %s child %i | new stack %s child %i path %s'\
                  , docID, str(stackOld), childOld, str(stackNew), childNew, pathNew)
    if stackOld==stackNew and childOld==childNew:  #nothing changed, just redraw
      return
    # change item in question
    db.updateBranch(docID=docID, branch=-99, stack=stackNew, path=pathNew, child=childNew, stackOld=stackOld+[docID])
    item.setData(item.data() | {'hierStack': '/'.join(stackNew+[docID])})
    # change siblings
    for line in siblingsOld:
      db.updateBranch(  docID=line['id'], branch=line['value'][4], child=line['value'][0]-1)
    for line in siblingsNew:
      if line['id']!=docID:
        db.updateBranch(docID=line['id'], branch=line['value'][4], child=line['value'][0]+1)
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
    hierStack = '/'.join([i.id for i in nodeHier.ancestors]+[nodeHier.id])
    gui = nodeHier.gui
    nodeTree = QStandardItem(nodeHier.name)
    nodeTree.setData({"hierStack":hierStack, "docType":nodeHier.docType, "gui":gui})
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
  SHOW_PROJ_DETAILS = 5
  HIDE_SHOW_ITEMS   = 6
  SHOW_DETAILS      = 7
  ADD_CHILD         = 8
  SHOW_TABLE        = 9
  ADD_ON            = 10
