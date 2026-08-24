""" Widget that shows the content of project in a electronic labnotebook """
import logging
import os
from enum import Enum
from typing import Any
from anytree import Node, PreOrderIter
from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, Slot
from PySide6.QtGui import QAction, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QInputDialog, QMenu, QTextEdit, QVBoxLayout, QWidget
from ...backend_worker.worker import Task
from ...fixed_strings_json import DO_NOT_RENDER
from ...misc_tools import callAddOn
from ...text_tools.handle_dictionaries import doc2markdown
from ...text_tools.string_changes import createDirName
from ..gui_communicate import Communicate
from ..gui_style import SPACE, Button, ButtonStyle, Label, Widget, action
from ..message_dialog import showMessage
from .project_tree_view import TreeView


class Project(Widget):
  """ Widget that shows the content of project in a electronic labnotebook """
  def __init__(self, comm:Communicate):
    """Initialize the project widget and connect it to shared communication state.

    Args:
      comm (Communicate): Shared object for project, backend, and GUI communication.
    """
    super().__init__()
    self.comm = comm
    self.comm.changeProject.connect(self.change)
    self.comm.changeDetails.connect(self.onDetailsChanged)
    self.comm.backendThread.worker.beSendHierarchy.connect(self.onGetData)
    self.hierarchy = Node('__none__')
    self.docProj:dict[str,Any] = {}
    self.projID = ''
    self.docIDHighlight = ''
    self.detailsDocID = ''
    self.showAll= self.comm.configuration['GUI']['showHidden']=='Yes'

    self.mainL = QVBoxLayout()
    self.setLayout(self.mainL)
    self.tree :TreeView | None             = None
    self.model:QStandardItemModel | None   = None
    self._modelItemChangedConnected        = False
    self.allDetails:QTextEdit | None       = None
    self.actHideDetail                     = QAction()
    self.actionFoldAll                     = QAction()
    self.showDetailsAll                    = False
    self.btnAddSubfolder:Button | None     = None
    self.btnMore:        Button | None     = None
    self.btnVisibility:  Button | None     = None
    self.lineSep = 20
    self.metaRole = Qt.ItemDataRole.UserRole + 1


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


  def paint(self) -> None:
    """
    What happens when user clicks to change project that is shown
    """
    if self.isHidden() and 'PYTEST_CURRENT_TEST' not in os.environ:
      return
    self._clearProjectWidgets()
    logging.debug('ProjectView elements at 1: %i',self.mainL.count())
    selectedIndex = None
    self.model = QStandardItemModel()
    self.tree = TreeView(self, self.comm, self.model)
    # self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
    # self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
    self.model.itemChanged.connect(self.modelChanged)
    self._modelItemChangedConnected = True
    self.tree.selectionModel().currentChanged.connect(self.onTreeSelectionChanged)
    self.tree.sameItemClicked.connect(self.onTreeSameItemClicked)
    rootItem = self.model.invisibleRootItem()
    #Populate model body of change project: start recursion
    if self.hierarchy is None:
      self.mainL.addWidget(self.tree)
      return
    if self.hierarchy is not None and self.hierarchy.name == '__ERROR_in_getHierarchy__':
      showMessage(self, 'Error', 'There is an error in the project hierarchy: a parent of a node is incorrect.', 'Critical')
      return
    for node in PreOrderIter(self.hierarchy, maxlevel=2):
      if node is None or node.is_root:                                                        # Project header
        self.paintProjectHeader()
      else:
        rootItem.appendRow(self.iterateTree(node))
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
    self.tree.expanded.connect(self.onTreeExpanded)
    self.tree.collapsed.connect(self.onTreeCollapsed)
    if self.docIDHighlight:
      self.tree.scrollToDoc(self.docIDHighlight)
      self.docIDHighlight = ''                                                         # reset after scrolling
    return


  def paintProjectHeader(self) -> None:
    """
    Paint header of page
    """
    if not self.docProj:
      return
    # TOP LINE includes name on left, buttons on right
    topLineW = QWidget(self)
    topLineL = QHBoxLayout(topLineW)
    topLineL.setSpacing(SPACE.M)
    topLineL.setContentsMargins(0, 0, 0, 0)
    self.mainL.addWidget(topLineW)
    hidden, menuTextHidden = ('     \U0001F441', 'Mark project as shown') \
                       if [b for b in self.docProj['branch'] if False in b['show']] else \
                       ('', 'Mark project as hidden')
    topLineL.addWidget(Label(self.docProj['name']+hidden, 'h2'))
    showStatus = '(Show all items)' if self.showAll else '(Hide hidden items)'
    topLineL.addWidget(QLabel(showStatus))
    topLineL.addStretch(1)
    # buttons in top line
    self.btnAddSubfolder = Button('Add subfolder', self, Command.ADD_CHILD, topLineL,
                                  icon='ri.folder-add-line', style=ButtonStyle.HIGHLIGHTED)
    self.btnVisibility = Button('Visibility', self, layout=topLineL,
                                icon='ri.eye-line', style=ButtonStyle.PRIMARY)
    visibilityMenu = QMenu(self)
    self.actHideDetail = action('Hide project details',self, [Command.SHOW_PROJ_DETAILS],visibilityMenu)
    menuTextItems = 'Hide hidden items' if self.showAll else 'Show hidden items'
    minimizeItems = 'Show all item details' if self.showDetailsAll else 'Hide all item details'
    action( menuTextItems,    self, [Command.HIDE_SHOW_ITEMS],  visibilityMenu)
    action( menuTextHidden,   self, [Command.HIDE],             visibilityMenu)
    self.actionFoldAll     = action( minimizeItems,    self, [Command.SHOW_DETAILS],     visibilityMenu)
    self.btnVisibility.setMenu(visibilityMenu)
    self.btnMore = Button('More', self, layout=topLineL,
                          icon='ri.more-fill', style=ButtonStyle.PRIMARY)
    moreMenu = QMenu(self)
    action('Edit project',              self, Command.EDIT,            moreMenu, icon='ri.edit-2-fill')
    action('Scan',                      self, Command.SCAN,            moreMenu, icon='fa5s.search')
    action('Show project on side',      self, Command.SHOW_IN_DETAILS, moreMenu, icon='ri.information-line')
    projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
    if projectAddOns := projectGroup.get('addOns',{}).get('project',''):
      for label, description in sorted(projectAddOns.items(), key=lambda item: item[1].casefold()):
        action(description, self, [Command.ADD_ON, label], moreMenu)
    self.btnMore.setMenu(moreMenu)

    self.allDetails = QTextEdit(self)
    self.allDetails.setMarkdown(doc2markdown(self.docProj, DO_NOT_RENDER, self.comm.dataHierarchyNodes['x0'],
                                             self))
    if not self.docProj['gui'][0]:
      self.allDetails.hide()
      self.actHideDetail.setText('Show project details')
    self.allDetails.resizeEvent = self.commentResize                                            # type: ignore
    bgColor = f"background-color: {self.comm.palette.getThemeColor('background', 'base')};"
    fgColor = self.comm.palette.get('secondaryText', 'color')
    self.allDetails.setStyleSheet(f"border: none; padding: 0px; {bgColor} {fgColor}")
    self.allDetails.setReadOnly(True)
    self.mainL.addWidget(self.allDetails)
    if sum(node.docType[0].startswith('x') for node in PreOrderIter(self.hierarchy)) <= 5:
      hint = 'Drag files onto a folder to add them.'
      if not self.hierarchy.children:
        hint = 'Add a subfolder, then drag files onto it.'
      hintLabel = QLabel(hint)
      hintLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
      hintLabel.setFrameShape(QFrame.Shape.StyledPanel)
      hintLabel.setStyleSheet(
          f'padding: {SPACE.M}px; border: 1px solid {self.comm.palette.getThemeColor("primary", "base")}; '
          f'background-color: {self.comm.palette.getThemeColor("background", "popup")};')
      self.mainL.addWidget(hintLabel)
    self.commentResize(None)
    return


  def execute(self, command: Command | list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command: command emitted by a button or legacy menu action
    """
    commandType = command if isinstance(command, Command) else command[0]
    payload = [] if isinstance(command, Command) else command[1:]
    if commandType is Command.IMPORT_FILES:
      folders = [node for node in PreOrderIter(self.hierarchy) if node.docType[0].startswith('x')]
      labels = ['/'.join(node.name for node in (*node.ancestors, node)) for node in folders]
      selectedFolder = self.projID                                             # use project id as the default
      # if the user has selected another folder, use that as default....
      if self.tree is not None and self.tree.currentIndex().isValid():
        item = self.model.itemFromIndex(self.tree.currentIndex()) if self.model is not None else None
        if item is not None and item.data()["docType"][0].startswith('x'):
          selectedFolder = item.data()['hierStack'].split('/')[-1]
      current = next((index for index, node in enumerate(folders) if node.id == selectedFolder), 0)
      label, accepted = QInputDialog.getItem(self, 'Import files', 'Destination folder:', labels, current, False)
      if accepted:
        folder = folders[labels.index(label)]
        self.comm.uiRequestTask.emit(Task.DROP_EXTERNAL,
                                    {'docID': folder.id, 'items': payload[0], 'addToExisting': False})
    elif commandType is Command.EDIT:
      self.comm.formDoc.emit({'id':self.docProj['id']})
      self.change(self.projID,'')
      #collect information and then change
      oldPath = self.comm.basePath/self.docProj['branch'][0]['path']
      if oldPath.is_dir():
        newPath = self.comm.basePath/createDirName(self.docProj, 0, self.comm.basePath)
        if oldPath != newPath:
          oldPath.rename(newPath)
      self.comm.changeSidebar.emit('redraw')
    elif commandType is Command.SHOW_IN_DETAILS:
      self.comm.changeDetails.emit(self.projID)
    elif commandType is Command.SCAN:
      self.comm.uiRequestTask.emit(Task.SCAN, {'docID':self.projID})
      self.comm.changeProject.emit(self.projID,'')
    elif commandType is Command.SHOW_PROJ_DETAILS:
      self.docProj['gui'][0] = not self.docProj['gui'][0]
      self.comm.uiRequestTask.emit(Task.SET_GUI, {'docID':self.projID, 'gui':self.docProj['gui']})
      if self.allDetails is not None and self.allDetails.isHidden():
        self.allDetails.show()
        self.actHideDetail.setText('Hide project details')
      elif self.allDetails is not None:
        self.allDetails.hide()
        self.actHideDetail.setText('Show project details')
    elif commandType is Command.HIDE:
      self.comm.uiRequestTask.emit(Task.HIDE_SHOW, {'docID':self.projID})
      self.comm.uiRequestHierarchy.emit(self.projID, self.showAll)
      self.comm.changeSidebar.emit('')
    elif commandType is Command.SHOW_DETAILS and self.tree is not None:
      def recursiveRowIteration(index:QModelIndex) -> None:
        """Visit descendants of a tree index and apply the current row action.

        Args:
          index (QModelIndex): Parent index whose child rows should be traversed.
        """
        for subRow in range(self.tree.model().rowCount(index)):                     # type: ignore[union-attr]
          subIndex = self.tree.model().index(subRow,0, index)                       # type: ignore[union-attr]
          subItem  = self.tree.model().itemFromIndex(subIndex)                      # type: ignore[union-attr]
          meta = subItem.data(self.metaRole)
          if not isinstance(meta, dict):
            continue
          docID    = meta['hierStack'].split('/')[-1]
          gui      = meta['gui']
          gui[0]   = self.showDetailsAll
          subItem.setData({ **meta, **{'gui':gui}}, self.metaRole)
          self.comm.uiRequestTask.emit(Task.SET_GUI, {'docID':docID, 'gui':gui})
          recursiveRowIteration(subIndex)
      recursiveRowIteration(self.tree.model().index(-1,0))
      self.showDetailsAll = not self.showDetailsAll
      if self.showDetailsAll:
        self.actionFoldAll.setText('Show all item details')
      else:
        self.actionFoldAll.setText('Hide all item details')
    elif commandType is Command.HIDE_SHOW_ITEMS:
      self.showAll = not self.showAll
      self.comm.uiRequestHierarchy.emit(self.projID, self.showAll)
    elif commandType is Command.ADD_CHILD:
      self.comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':[self.projID], 'docType':'x1', 'doc':{'name':'new item'}})
      self.comm.uiRequestHierarchy.emit(self.projID, self.showAll)

    elif commandType is Command.ADD_ON:
      callAddOn(payload[0], self.comm, self.projID, self)
    else:
      logging.error('Project menu unknown: %s',command, exc_info=True)
    return


  def _clearProjectWidgets(self) -> None:
    """Disconnect and delete old project widgets on the GUI thread."""
    if self.tree is not None:
      try:
        self.tree.selectionModel().currentChanged.disconnect(self.onTreeSelectionChanged)
      except (RuntimeError, TypeError):
        pass
      try:
        self.tree.sameItemClicked.disconnect(self.onTreeSameItemClicked)
      except (RuntimeError, TypeError):
        pass
      try:
        self.tree.expanded.disconnect(self.onTreeExpanded)
      except (RuntimeError, TypeError):
        pass
      try:
        self.tree.collapsed.disconnect(self.onTreeCollapsed)
      except (RuntimeError, TypeError):
        pass
    if self.model is not None and self._modelItemChangedConnected:
      try:
        self.model.itemChanged.disconnect(self.modelChanged)
      except (RuntimeError, TypeError):
        pass
      self._modelItemChangedConnected = False
    while self.mainL.count():
      item = self.mainL.takeAt(0)
      widget = None if item is None else item.widget()
      if widget is not None:
        widget.deleteLater()
    self.tree = None
    self.model = None
    self.allDetails = None


  def commentResize(self, _:Any) -> None:
    """ called if comment is resized because widget initially/finally knows its size
    - comment widget is hard coded size it depends on the rendered size
    """
    if self.allDetails is None:
      return
    self.allDetails.document().setTextWidth(self.width()-20)
    height = int(self.allDetails.document().size().toTuple()[1])
    self.allDetails.setMaximumHeight(height+12)
    self.allDetails.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return


  @Slot(QModelIndex)
  def onTreeExpanded(self, index:QModelIndex) -> None:
    """Persist the expanded state of a folder item."""
    self.actionExpandCollapse(index, True)


  @Slot(QModelIndex)
  def onTreeCollapsed(self, index:QModelIndex) -> None:
    """Persist the collapsed state of a folder item."""
    self.actionExpandCollapse(index, False)


  @Slot(QModelIndex, QModelIndex)
  def onTreeSelectionChanged(self, current:QModelIndex, _:QModelIndex) -> None:
    """Show the selected project item in the shared details pane."""
    if not current.isValid():                                # hide details when user clicks in between leaves
      self.comm.changeDetails.emit('')
      return
    meta = current.data(self.metaRole)
    docID = meta['hierStack'].split('/')[-1]
    self.comm.changeDetails.emit(docID)


  @Slot(str)
  def onDetailsChanged(self, docID:str) -> None:
    """Track in this project.py the document currently shown in the shared details pane."""
    self.detailsDocID = docID


  @Slot(QModelIndex)
  def onTreeSameItemClicked(self, index:QModelIndex) -> None:
    """Toggle details when the current project item is clicked again
    -'' = close when self.detailsDocID == docID
    - docID = open else
    """
    docID = index.data(self.metaRole)['hierStack'].split('/')[-1]
    self.comm.changeDetails.emit('' if self.detailsDocID == docID else docID)


  def setExpandedState(self, node:QStandardItem) -> None:
    """ Recursive function to set the expanded state of nodes

    Args:
      node (QStandardItem): node to process
    """
    if self.model is None or self.tree is None:
      return
    for iRow in range(node.rowCount()):
      item = node.child(iRow)
      data = item.data(self.metaRole)
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
    meta = index.data(self.metaRole)
    if not isinstance(meta, dict):
      return
    gui  = [meta['gui'][0]]+[flag]
    docID = meta['hierStack'].split('/')[-1]
    self.model.itemFromIndex(index).setData({ **meta, **{'gui':gui}}, self.metaRole)
    self.comm.uiRequestTask.emit(Task.SET_GUI, {'docID':docID, 'gui':gui})
    return


  def modelChanged(self, item:QStandardItem) -> None:
    """
    Autocalled after drag-drop and other changes, record changes to backend and database directly

    Args:
      item (QStandardItem): item changed, new location
    """
    meta = item.data(self.metaRole)
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
      metaParent = currentItem.data(self.metaRole)
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
    nodeTree.setData({'hierStack':hierStack, 'docType':nodeHier.docType, 'gui':gui, 'childNum':nodeHier.childNum,
                      'fPath':nodeHier.fPath}, self.metaRole)
    if nodeHier.id[0]=='x' or nodeHier.fPath == '*':
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
  EDIT              = 1
  SHOW_IN_DETAILS   = 2
  SCAN              = 3
  HIDE              = 4
  SHOW_PROJ_DETAILS = 5
  HIDE_SHOW_ITEMS   = 6
  SHOW_DETAILS      = 7
  ADD_CHILD         = 8
  ADD_ON            = 10
  IMPORT_FILES      = 11
