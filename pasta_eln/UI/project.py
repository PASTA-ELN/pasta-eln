""" Widget that shows the content of project in a electronic labnotebook """
import logging
import os
from enum import Enum
from typing import Any, Optional
from anytree import Node, PreOrderIter
from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, Slot
from PySide6.QtGui import QAction, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QLabel, QMenu, QMessageBox, QTextEdit, QVBoxLayout, QWidget
from ..backendWorker.worker import Task
from ..fixedStringsJson import DO_NOT_RENDER
from ..miscTools import callAddOn
from ..textTools.handleDictionaries import doc2markdown
from ..textTools.stringChanges import createDirName
from .guiCommunicate import Communicate
from .guiStyle import Action, Label, TextButton, widgetAndLayout
from .messageDialog import showMessage
from .projectTreeView import TreeView


class Project(QWidget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm:Communicate):
    super().__init__()
    self.comm = comm
    self.comm.changeProject.connect(self.change)
    self.comm.backendThread.worker.beSendHierarchy.connect(self.onGetData)
    self.hierarchy = Node('__none__')
    self.docProj:dict[str,Any] = {}
    self.projID = ''
    self.docIDHighlight = ''
    self.showAll= self.comm.configuration['GUI']['showHidden']=='Yes'

    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)
    self.tree :Optional[TreeView]            = None
    self.model:Optional[QStandardItemModel]  = None
    self.allDetails                          = QTextEdit()
    self.actHideDetail                       = QAction()
    self.actionFoldAll                       = QAction()
    self.showDetailsAll = False
    self.btnAddSubfolder:Optional[TextButton] = None
    self.btnEditProject:Optional[TextButton]  = None
    self.btnMore:Optional[TextButton]         = None
    self.btnVisibility:Optional[TextButton]   = None
    self.lineSep = 20
    self.META_ROLE = Qt.ItemDataRole.UserRole + 1


  @Slot(Node, dict)
  def onGetData(self, hierarchy:Node, doc:dict[str,Any]) -> None:
    """
    Callback function to handle the received data

    Args:
      hierarchy (Node): hierarchy of the project
      doc (pd.DataFrame): DataFrame containing table
    """
    if doc:
      self.docProj = doc
    self.hierarchy = hierarchy
    self.paint()


  @Slot(str, str)
  def change(self, projID:str, docID:str) -> None:
    """ Change project to projID and docID
    Args:
      projID (str): project ID
      docID (str): document ID
    """
    self.docIDHighlight = docID
    self.projID = projID
    self.comm.uiRequestHierarchy.emit(projID, self.showAll)


  def projHeader(self) -> None:
    """
    Initialize / Create header of page
    """
    # remove if still there
    for i in reversed(range(self.mainL.count())):                                                  #remove old
      self.mainL.itemAt(i).widget().setParent(None)
    logging.debug('ProjectView elements at 2: %i',self.mainL.count())
    if not self.docProj:
      return
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
    self.btnAddSubfolder = TextButton('Add subfolder', self, [Command.ADD_CHILD], topLineL)
    self.btnEditProject =  TextButton('Edit project',  self, [Command.EDIT],      topLineL)
    self.btnVisibility = TextButton(  'Visibility',    self, [],                  topLineL)
    visibilityMenu = QMenu(self)
    self.actHideDetail = Action('Hide project details',self, [Command.SHOW_PROJ_DETAILS],visibilityMenu)
    menuTextItems = 'Hide hidden items' if self.showAll else 'Show hidden items'
    minimizeItems = 'Show all item details' if self.showDetailsAll else 'Hide all item details'
    Action( menuTextItems,    self, [Command.HIDE_SHOW_ITEMS],  visibilityMenu)
    Action( menuTextHidden,   self, [Command.HIDE],             visibilityMenu)
    self.actionFoldAll     = Action( minimizeItems,    self, [Command.SHOW_DETAILS],     visibilityMenu)
    self.btnVisibility.setMenu(visibilityMenu)
    self.btnMore = TextButton('More',           self, [], topLineL)
    moreMenu = QMenu(self)
    Action('Scan',                      self, [Command.SCAN], moreMenu)
    for docType, value in self.comm.docTypesTitles.items():
      if docType[0]!='x':
        icon = 'fa5s.asterisk' if value['icon']=='' else value['icon']
        Action(f'list of {value["title"].lower()}',   self, [Command.SHOW_TABLE, docType], moreMenu, icon=icon)
    Action('list of unidentified',     self, [Command.SHOW_TABLE, '-'],     moreMenu, icon='fa5.file')
    moreMenu.addSeparator()
    projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
    if projectAddOns := projectGroup.get('addOns',{}).get('project',''):
      for label, description in projectAddOns.items():
        Action(description, self, [Command.ADD_ON, label], moreMenu)
      moreMenu.addSeparator()
    Action('Delete project',            self, [Command.DELETE], moreMenu)
    self.btnMore.setMenu(moreMenu)

    # Details section
    # self.infoW = QScrollArea()
    # self.infoW.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    # self.infoW.setWidgetResizable(True)
    self.allDetails.setMarkdown(doc2markdown(self.docProj, DO_NOT_RENDER, self.comm.dataHierarchyNodes['x0'],
                                             self))
    if not self.docProj['gui'][0]:
      self.allDetails.hide()
      self.actHideDetail.setText('Show project details')
    self.allDetails.resizeEvent = self.commentResize                                            # type: ignore
    bgColor = self.comm.palette.get('secondaryDark', 'background-color')
    fgColor = self.comm.palette.get('secondaryText', 'color')
    #TODO: Debug/solve on windows: For none: no color is set, as it should; but then the Windows10 color is white not the default background
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
    self.allDetails.document().setTextWidth(self.width()-20)
    height:int = self.allDetails.document().size().toTuple()[1]                          # type: ignore[index]
    self.allDetails.setMaximumHeight(height+12)
    self.allDetails.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return


  def paint(self) -> None:
    """
    What happens when user clicks to change project that is shown
    """
    if self.isHidden() and 'PYTEST_CURRENT_TEST' not in os.environ:
      return
    #initialize
    for i in reversed(range(self.mainL.count())):                                                  #remove old
      self.mainL.itemAt(i).widget().setParent(None)
    logging.debug('ProjectView elements at 1: %i',self.mainL.count())
    selectedIndex = None
    self.model = QStandardItemModel()
    self.tree = TreeView(self, self.comm, self.model)
    # self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
    # self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
    self.model.itemChanged.connect(self.modelChanged)
    rootItem = self.model.invisibleRootItem()
    #Populate model body of change project: start recursion
    if self.hierarchy is not None and self.hierarchy.name == '__ERROR_in_getHierarchy__':
      showMessage(self, 'Error', 'There is an error in the project hierarchy: a parent of a node is incorrect.', 'Critical')
      return
    try:
      for node in PreOrderIter(self.hierarchy, maxlevel=2):
        if node is None or node.is_root:                                                      # Project header
          self.projHeader()
        else:
          rootItem.appendRow(self.iterateTree(node))
    except AttributeError:
      self.tree = TreeView(self, self.comm, QStandardItemModel())    # if hierarchy is None, create empty tree
    # collapse / expand depending on stored value
    # by iterating each leaf, and converting item and index
    root = self.model.invisibleRootItem()
    self.setExpandedState(root)
    if selectedIndex is not None:
      self.tree.selectionModel().select(selectedIndex, QItemSelectionModel.Select)
      self.tree.setCurrentIndex(selectedIndex)
    self.mainL.addWidget(self.tree)
    logging.debug('ProjectView elements at 4: %i',self.mainL.count())
    if self.hierarchy is not None and len(self.hierarchy.children)>0 and self.btnAddSubfolder is not None:
      self.btnAddSubfolder.setVisible(False)
    self.tree.expanded.connect(lambda index: self.actionExpandCollapse(index, True))
    self.tree.collapsed.connect(lambda index: self.actionExpandCollapse(index, False))
    if self.docIDHighlight:
      self.tree.scrollToDoc(self.docIDHighlight)
      self.docIDHighlight = ''                                                         # reset after scrolling
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
      data = item.data(self.META_ROLE)
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
    meta = index.data(self.META_ROLE)
    if not isinstance(meta, dict):
      return
    gui  = [meta['gui'][0]]+[flag]
    docID = meta['hierStack'].split('/')[-1]
    self.model.itemFromIndex(index).setData({ **meta, **{'gui':gui}}, self.META_ROLE)
    self.comm.uiRequestTask.emit(Task.SET_GUI, {'docID':docID, 'gui':gui})
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.EDIT:
      self.comm.formDoc.emit({'id':self.docProj['id']})
      self.change(self.projID,'')
      #collect information and then change
      oldPath = self.comm.basePath/self.docProj['branch'][0]['path']
      if oldPath.is_dir():
        newPath = self.comm.basePath/createDirName(self.docProj, 0, self.comm.basePath)
        oldPath.rename(newPath)
      self.comm.changeSidebar.emit('redraw')
    elif command[0] is Command.DELETE:
      ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete project?', \
                                 QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
                                 QMessageBox.StandardButton.No)
      if ret==QMessageBox.StandardButton.Yes:
        self.comm.uiRequestTask.emit(Task.DELETE_DOC, {'docID':self.projID})
        #update sidebar, show projects
        self.comm.changeTable.emit('x0','')
    elif command[0] is Command.SCAN:
      self.comm.uiRequestTask.emit(Task.SCAN, {'docID':self.projID})
      self.comm.changeProject.emit(self.projID,'')
    elif command[0] is Command.SHOW_PROJ_DETAILS:
      self.docProj['gui'][0] = not self.docProj['gui'][0]
      self.comm.uiRequestTask.emit(Task.SET_GUI, {'docID':self.projID, 'gui':self.docProj['gui']})
      if self.allDetails is not None and self.allDetails.isHidden():
        self.allDetails.show()
        self.actHideDetail.setText('Hide project details')
      elif self.allDetails is not None:
        self.allDetails.hide()
        self.actHideDetail.setText('Show project details')
    elif command[0] is Command.HIDE:
      self.comm.uiRequestTask.emit(Task.HIDE_SHOW, {'docID':self.projID})
      self.comm.uiRequestHierarchy.emit(self.projID, self.showAll)
      self.comm.changeSidebar.emit('')
    elif command[0] is Command.SHOW_DETAILS and self.tree is not None:
      def recursiveRowIteration(index:QModelIndex) -> None:
        for subRow in range(self.tree.model().rowCount(index)):                     # type: ignore[union-attr]
          subIndex = self.tree.model().index(subRow,0, index)                       # type: ignore[union-attr]
          subItem  = self.tree.model().itemFromIndex(subIndex)                      # type: ignore[union-attr]
          meta = subItem.data(self.META_ROLE)
          if not isinstance(meta, dict):
            continue
          docID    = meta['hierStack'].split('/')[-1]
          gui      = meta['gui']
          gui[0]   = self.showDetailsAll
          subItem.setData({ **meta, **{'gui':gui}}, self.META_ROLE)
          self.comm.uiRequestTask.emit(Task.SET_GUI, {'docID':docID, 'gui':gui})
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
      self.comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':[self.projID], 'docType':'x1', 'doc':{'name':'new item'}})
    elif command[0] is Command.SHOW_TABLE:
      self.comm.changeTable.emit(command[1], self.projID)
    elif command[0] is Command.ADD_ON:
      callAddOn(command[1], self.comm, self.projID, self)
    else:
      logging.error('Project menu unknown: %s',command, exc_info=True)
    return


  def modelChanged(self, item:QStandardItem) -> None:
    """
    Autocalled after drag-drop and other changes, record changes to backend and database directly

    Args:
      item (QStandardItem): item changed, new location
    """
    meta = item.data(self.META_ROLE)
    if not isinstance(meta, dict):
      return
    # gather old information
    stackOld = meta['hierStack'].split('/')[:-1]
    docID    = meta['hierStack'].split('/')[-1]
    childOld = meta['childNum']
    # gather new information
    stackNew = []                                                                             #create reversed
    currentItem = item
    while currentItem.parent() is not None:
      currentItem = currentItem.parent()
      metaParent = currentItem.data(self.META_ROLE)
      docIDj = metaParent['hierStack'].split('/')[-1]
      stackNew.append(docIDj)
    stackNew = [self.projID] + stackNew[::-1]                                      #add project id and reverse
    childNew = item.row()
    # compare
    logging.debug('Change project: docID %s | old stack %s child %i | new stack %s child %i'\
                  , docID, str(stackOld), childOld, str(stackNew), childNew)
    if stackOld==stackNew and childOld==childNew:                                #nothing changed, just redraw
      return
    self.comm.uiRequestTask.emit(Task.MOVE_LEAVES, {'docID':docID, 'stackOld':stackOld, 'stackNew':stackNew,
                                                    'childOld':childOld, 'childNew':childNew})
    item.setData(item.data() | {'hierStack': '/'.join(stackNew+[docID]), 'childNum':childNew})
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
    nodeTree.setData({'hierStack':hierStack, 'docType':nodeHier.docType, 'gui':gui, 'childNum':nodeHier.childNum}, self.META_ROLE)
    if nodeHier.id[0]=='x':
      nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)# type: ignore
    else:
      nodeTree.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)          # type: ignore
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
