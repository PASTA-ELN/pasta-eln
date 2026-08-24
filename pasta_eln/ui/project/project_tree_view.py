""" Custom tree view on data model """
import logging
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtCore import QModelIndex, QPoint, QItemSelectionModel, Qt, QTimer, Signal
from PySide6.QtGui import QContextMenuEvent, QDropEvent, QMouseEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QMenu, QMessageBox, QTreeView, QWidget
from ...backend_worker.worker import Task
from ...misc_tools import callAddOn
from ..gui_communicate import Communicate
from ..gui_style import action
from ..message_dialog import showMessage
from .project_leaf_renderer import ProjectLeafRenderer

SCROLL_SPEED = 25

class TreeView(QTreeView):
  """ Custom tree view on data model

  Uses a standard QTreeView with custom event handling and a delegate that
  paints each project item. This is more efficient for large project views and
  requires less code than embedding widgets in every item. The trade-off is
  that per-item buttons are more difficult to implement. Anyhow, buttons could visually
  clutter the interface.
  """
  sameItemClicked = Signal(QModelIndex)

  def __init__(self, parent:QWidget, comm:Communicate, model:QStandardItemModel):
    """Initialize the project tree view with its model and communication state.

    Args:
      parent (QWidget): Widget that owns this tree view.
      comm (Communicate): Shared object used for project actions and backend requests.
      model (QStandardItemModel): Standard item model containing the project hierarchy.
    """
    super().__init__(parent)
    self.aParentWidget: Any = parent
    self.comm = comm
    self.setModel(model)
    self.setHeaderHidden(True)
    self.setStyleSheet(f'''
    QTreeView::branch {{border-image: none;}}
    TreeView {{background-color:{self.comm.palette.getThemeColor("background", "base")};}}
    ''')
    self.setIndentation(40)
    self.renderer = ProjectLeafRenderer(self, self.comm)
    self.setItemDelegate(self.renderer)
    self.renderer.contextMenuRequested.connect(self.showContextMenu)
    self.viewport().setMouseTracking(True)
    self.setExpandsOnDoubleClick(False)
    self.setAcceptDrops(True)
    self.setDropIndicatorShown(True)
    self.setDefaultDropAction(Qt.DropAction.MoveAction)
    self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
    self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    self.verticalScrollBar().setSingleStep(SCROLL_SPEED)
    self.doubleClicked.connect(self.tree2Clicked)


  def mousePressEvent(self, event:QMouseEvent) -> None:
    """Notify the project view when the current item is clicked again."""
    clickedIndex = self.indexAt(event.position().toPoint())
    # save the item that was previously selected
    sameItem = event.button() == Qt.MouseButton.LeftButton and clickedIndex.isValid() and clickedIndex == self.currentIndex()
    # update things
    super().mousePressEvent(event)
    if sameItem:
      self.sameItemClicked.emit(clickedIndex)


  def contextMenuEvent(self, event:QContextMenuEvent) -> None:
    """
    create context menu

    Args:
      event (QContextMenuEvent): context-menu event
    """
    self.showContextMenu(self.indexAt(event.pos()), event.globalPos())
    return


  def showContextMenu(self, clickedIndex:QModelIndex, globalPos:QPoint) -> None:
    """Show the context menu for the item at ``clickedIndex``.

    Args:
      clickedIndex (QModelIndex): index of the item
      globalPos (QPoint): global position of the mouse
    """
    if not clickedIndex.isValid():
      return
    self.setCurrentIndex(clickedIndex)
    item = self.model().itemFromIndex(clickedIndex)                               # type: ignore[attr-defined]
    if item is None:                                                                 #clicked outside any leaf
      return
    folder = item.data()['hierStack'].split('/')[-1][0]=='x'
    context = QMenu(self)
    if folder:
      action('Add child folder',                   self, [Command.ADD_CHILD],      context)
    action('Add sibling folder',                   self, [Command.ADD_SIBLING],    context)
    context.addSeparator()
    action('Hide/show item details',               self, [Command.SHOW_DETAILS], context)
    if folder:
      projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
      if projectAddOns := projectGroup.get('addOns',{}).get('project',''):
        context.addSeparator()
        projectAddOnMenu = context.addMenu('Project add-ons')
        for label, description in projectAddOns.items():
          action(description, self, [Command.ADD_ON, label], projectAddOnMenu)
    addItemMenu = context.addMenu('Add item')
    addItemMenu.setEnabled(folder)
    if folder:
      for docType, details in sorted(self.comm.docTypesTitles.items(), key=lambda item: item[1]['title'].casefold()):
        if not docType.startswith(('x', '-')):
          action(details['title'], self, [Command.ADD_ITEM, docType], addItemMenu)
    context.exec(globalPos)
    return


  def execute(self, command:list[Any]) -> None:
    """
    after selecting a item from context menu

    Args:
      command (list): list of commands
    """
    item = self.model().itemFromIndex(self.currentIndex())                        # type: ignore[attr-defined]
    hierStack = item.data()['hierStack'].split('/')
    if command[0] is Command.ADD_ITEM:
      self.comm.formDoc.emit({'type': [command[1]], '_hierStack': hierStack})
    elif command[0] is Command.ADD_CHILD:
      self.comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':hierStack, 'docType':'x1', 'doc':{'name':'new item'}})

    elif command[0] is Command.ADD_SIBLING:
      hierStack= hierStack[:-1]
      self.comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':hierStack, 'docType':'x1', 'doc':{'name':'new item'}})

    elif command[0] is Command.SHOW_DETAILS:
      gui    = item.data()['gui']
      gui[0] = not gui[0]
      docID  = hierStack[-1]
      def iterate(currentItem:QStandardItem) -> None:
        """ iterate through all branches and leaves and find items matching the docID
        Args:
          currentItem (QStandardItem): item to iterate to its children
        """
        currentIndex = self.model().indexFromItem(currentItem)                    # type: ignore[attr-defined]
        if currentItem.data() is not None and docID==currentItem.data()['hierStack'].split('/')[-1]:
          currentItem.setData({ **currentItem.data(), **{'gui':gui}})
        for row in range(self.model().rowCount(currentIndex)):
          for column in range(self.model().columnCount(currentIndex)):
            childIndex = self.model().index(row, column, currentIndex)
            iterate(self.model().itemFromIndex(childIndex))                       # type: ignore[attr-defined]
      iterate(self.model().invisibleRootItem())                                   # type: ignore[attr-defined]
      # only one change once the DB
      self.comm.uiRequestTask.emit(Task.SET_GUI, {'docID':docID, 'gui':gui})

    elif command[0] is Command.ADD_ON:
      callAddOn(command[1], self.comm, item.data()['hierStack'], self)
    else:
      logging.error('Unknown context menu %s', command, exc_info=True)
    self.comm.uiRequestHierarchy.emit(self.aParentWidget.projID, self.aParentWidget.showAll)
    return


  def scrollToDoc(self, docID:str) -> None:
    """
    Scroll to document with docID

    Args:
      docID (str): document ID
    """
    def iterate(currentItem:QStandardItem) -> QStandardItem | None:
      """ iterate through all branches and leaves and find items matching the docID
      Args:
        currentItem (QStandardItem): item to iterate to its children
      Returns:
        QStandardItem | None: item with docID or None if not found
      """
      currentIndex = self.model().indexFromItem(currentItem)                      # type: ignore[attr-defined]
      if currentItem.data() is not None and docID==currentItem.data()['hierStack'].split('/')[-1]:
        return currentItem
      for row in range(self.model().rowCount(currentIndex)):
        for column in range(self.model().columnCount(currentIndex)):
          childIndex = self.model().index(row, column, currentIndex)
          found = iterate(self.model().itemFromIndex(childIndex))                 # type: ignore[attr-defined]
          if found is not None:
            return found
      return None
    item = iterate(self.model().invisibleRootItem())                              # type: ignore[attr-defined]
    if item is not None:
      parents: list[QModelIndex] = []                                     # list of parents, grandparents, ...
      parent = item.index().parent()
      while parent.isValid():
        parents.append(parent)
        parent = parent.parent()
      # expand all parents such that this item is visible (prevent expanding to interfere with scrolling)
      self.blockSignals(True)
      for parent in reversed(parents):
        self.setExpanded(parent, True)
      self.blockSignals(False)
      # select
      self.selectionModel().select(item.index(), QItemSelectionModel.SelectionFlag.ClearAndSelect |
                                   QItemSelectionModel.SelectionFlag.Rows)
      self.setCurrentIndex(item.index())
      # scroll
      QTimer.singleShot(100, lambda: self.scrollTo(item.index(), QAbstractItemView.ScrollHint.PositionAtCenter))
    return


  def tree2Clicked(self) -> None:
    """
    after double-click on tree leaf: open form
    - no redraw required since renderer asks automatically for update
    """
    item = self.model().itemFromIndex(self.currentIndex())                        # type: ignore[attr-defined]
    docID = item.data()['hierStack'].split('/')[-1]
    self.comm.formDoc.emit({'id':docID})
    return


  def dragEnterEvent(self, event:QDropEvent) -> None:
    """
    Override default: what happens if you drag an item

    Args:
      event (QMouseEvent): event
    """
    event.acceptProposedAction()
    return


  def dropEvent(self, event:QDropEvent) -> None:
    """
    Override default: what happens at end of drag&drop

    Args:
      event (QDropEvent): event
    """
    if event.mimeData().hasUrls():                                                    #file dropped onto pasta
      item = self.model().itemFromIndex(self.indexAt(event.pos()))                # type: ignore[attr-defined]
      if item is None or (item.data()['docType'][0][0]!='x' and item.data()['fPath']!='*'):
        showMessage(self, 'Error', 'You can drop external files only onto folders or items without a file connected.')
        return
      # create a list of all items
      items = [url.toLocalFile() for url in event.mimeData().urls()]
      if not items:
        showMessage(self, 'Error', 'The files / folders you dropped are empty.')
        return
      if item.data()['fPath']=='*' and (len(items)>1 or Path(items[0]).is_dir()):
        showMessage(self, 'Error', 'You can drop only one file onto an item without a file connected.')
        return
      docID = item.data()['hierStack'].split('/')[-1]
      self.comm.uiRequestTask.emit(Task.DROP_EXTERNAL, {'docID':docID, 'items':items,
                                                        'addToExisting':item.data()['fPath']=='*'})# if true, add to existing; if false, create new
      event.ignore()
    elif 'application/x-qstandarditemmodeldatalist' in event.mimeData().formats():
      if event.source() is not self:
        event.ignore()
        return
      selectedIndexes = self.selectionModel().selectedIndexes()
      if not selectedIndexes:
        event.ignore()
        return
      sourceIndex = selectedIndexes[0]
      sourceDocID = sourceIndex.data(Qt.ItemDataRole.UserRole + 1)['hierStack'].split('/')[-1]
      targetIndex = self.indexAt(event.position().toPoint())
      if self.dropIndicatorPosition() == QAbstractItemView.DropIndicatorPosition.OnItem and \
        (not targetIndex.isValid() or not targetIndex.data(Qt.ItemDataRole.UserRole + 1)['docType'][0].startswith('x')):# this is not a folder but an item with no path
        QMessageBox.critical(self, 'Error', 'You can drop items only onto folders.')
        return
      if self.dropIndicatorPosition() in (QAbstractItemView.DropIndicatorPosition.AboveItem,
                                          QAbstractItemView.DropIndicatorPosition.BelowItem ):
        targetIndex = targetIndex.parent()
      if targetIndex != sourceIndex.parent():                               # if not moving within same parent
        for row in range(self.model().rowCount(targetIndex)):
          childIndex = self.model().index(row, 0, targetIndex)
          docIDchild = childIndex.data(Qt.ItemDataRole.UserRole+1)['hierStack'].split('/')[-1]
          if docIDchild == sourceDocID:
            QMessageBox.critical(self, 'Error', 'You can drop this item here because a copy already exists here.')
            return
      super().dropEvent(event)
    else:
      logging.error('Drop unknown data: %s', event.mimeData().formats(), exc_info=True)
    return


class Command(Enum):
  """ Commands used in this file """
  ADD_ITEM         = 1
  ADD_CHILD        = 2
  ADD_SIBLING      = 3
  SHOW_DETAILS     = 5
  ADD_ON           = 9
