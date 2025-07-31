""" Custom tree view on data model """
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtCore import Qt                                              # pylint: disable=no-name-in-module
from PySide6.QtGui import QDropEvent, QEventPoint, QStandardItem, QStandardItemModel# pylint: disable=no-name-in-module
from PySide6.QtWidgets import QAbstractItemView, QMenu, QMessageBox, QTreeView, QWidget# pylint: disable=no-name-in-module
from ..backendWorker.worker import Task
from ..miscTools import callAddOn
from .guiCommunicate import Communicate
from .guiStyle import Action
from .messageDialog import showMessage
from .projectLeafRenderer import ProjectLeafRenderer


class TreeView(QTreeView):
  """ Custom tree view on data model """
  def __init__(self, parent:QWidget, comm:Communicate, model:QStandardItemModel):
    super().__init__(parent)
    self.aParentWidget = parent
    self.comm = comm
    self.setModel(model)
    self.setHeaderHidden(True)
    self.setStyleSheet('QTreeView::branch {border-image: none;}')
    self.setIndentation(40)
    self.renderer = ProjectLeafRenderer(self.comm)
    self.setItemDelegate(self.renderer)
    self.setExpandsOnDoubleClick(False)
    self.setAcceptDrops(True)
    self.setDropIndicatorShown(True)
    self.setDefaultDropAction(Qt.DropAction.MoveAction)
    self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
    self.doubleClicked.connect(self.tree2Clicked)


  def contextMenuEvent(self, p:QEventPoint) -> None:                                  # type: ignore[override]
    """
    create context menu

    Args:
      p (QPoint): point of clicking
    """
    item = self.model().itemFromIndex(self.currentIndex())                        # type: ignore[attr-defined]
    if item is None:                                                                 #clicked outside any leaf
      return
    folder = item.data()['hierStack'].split('/')[-1][0]=='x'
    context = QMenu(self)
    if folder:
      Action('Add child folder',                   self, [Command.ADD_CHILD],      context)
    Action('Add sibling folder',                   self, [Command.ADD_SIBLING],    context)
    Action('Delete item',                          self, [Command.DELETE],         context)
    context.addSeparator()
    Action('Hide/show item details',               self, [Command.SHOW_DETAILS], context)
    Action('Mark item as hidden/shown',            self, [Command.HIDE],           context)
    context.addSeparator()
    if not folder:
      Action('Open file with another application', self, [Command.OPEN_EXTERNAL],    context)
    Action('Open folder in file browser',          self, [Command.OPEN_FILEBROWSER], context)
    if folder:
      projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
      if projectAddOns := projectGroup.get('addOns',{}).get('project',''):
        context.addSeparator()
        for label, description in projectAddOns.items():
          Action(description, self, [Command.ADD_ON, label], context)
    context.exec(p.globalPos())                                                   # type: ignore[attr-defined]
    return


  def execute(self, command:list[Any]) -> None:
    """
    after selecting a item from context menu

    Args:
      command (list): list of commands
    """
    item = self.model().itemFromIndex(self.currentIndex())                        # type: ignore[attr-defined]
    hierStack = item.data()['hierStack'].split('/')
    if command[0] is Command.ADD_CHILD:
      self.comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':hierStack, 'docType':'x1', 'doc':{'name':'new item'}})
    elif command[0] is Command.ADD_SIBLING:
      hierStack= hierStack[:-1]
      self.comm.uiRequestTask.emit(Task.ADD_DOC, {'hierStack':hierStack, 'docType':'x1', 'doc':{'name':'new item'}})
    elif command[0] is Command.DELETE:
      ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete this data?',\
                                 QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
      if ret==QMessageBox.StandardButton.Yes:
        docID = hierStack[-1]
        self.comm.uiRequestTask.emit(Task.DELETE_DOC, {'docID':docID})
        # TODO remove leaf from GUI
        item  = self.model().itemFromIndex(self.currentIndex())                   # type: ignore[attr-defined]
        parent = item.parent()
        if parent is None:                                                                          #top level
          parent = self.model().invisibleRootItem()                               # type: ignore[attr-defined]
          if parent.rowCount()==1:
            self.aParentWidget.btnAddSubfolder.setVisible(True)                   # type: ignore[attr-defined]
        parent.removeRow(item.row())
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
    elif command[0] is Command.HIDE:
      logging.debug('hide document %s',hierStack[-1])
      self.comm.uiRequestTask.emit(Task.HIDE_SHOW, {'docID':hierStack[-1]})
      #TODO: current implementation: you hide one; all others are hidden as well
      # Talk to GW what is the default expectation; system allows for individual hiding
      #
      # after hide, do not hide immediately but wait on next refresh
    elif command[0] is Command.OPEN_EXTERNAL or command[0] is Command.OPEN_FILEBROWSER:
      # depending if non-folder / folder; address different item in hierstack
      docID = hierStack[-2] \
        if command[0] is Command.OPEN_FILEBROWSER and hierStack[-1][0]!='x' \
        else hierStack[-1]
      self.comm.uiRequestTask.emit(Task.OPEN_EXTERNAL, {'docID':docID})
    elif command[0] is Command.ADD_ON:
      callAddOn(command[1], self.comm, item.data()['hierStack'], self)
    else:
      logging.error('Unknown context menu %s', command)
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
      self.scrollTo(item.index(), QAbstractItemView.EnsureVisible)                # type: ignore[attr-defined]
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
    if event.mimeData().hasUrls():                                                     #file droped onto pasta
      item = self.model().itemFromIndex(self.indexAt(event.pos()))                # type: ignore[attr-defined]
      if item is None or item.data()['docType'][0][0]!='x':
        showMessage(self, 'Error', 'You can drop external files only onto folders.')
        return
      # create a list of all files
      files, folders = [], []
      for url in event.mimeData().urls():
        path = url.toLocalFile()
        if Path(path).is_file():
          files.append(path)
        else:
          files +=   list(Path(path).rglob('*'))                                      # type: ignore[arg-type]
          folders += [x[0] for x in os.walk(path)]
      if not (folders+[str(i) for i in files]):
        showMessage(self, 'Error', 'The files seem empty.')
        return
      docID = item.data()['hierStack'].split('/')[-1]
      self.comm.uiRequestTask.emit(Task.DROP_EXTERNAL, {'docID':docID, 'files':files, 'folders':folders})
      event.ignore()
    elif 'application/x-qstandarditemmodeldatalist' in event.mimeData().formats():
      super().dropEvent(event)
    else:
      logging.error('Drop unknown data: %s', event.mimeData().formats())
    return


class Command(Enum):
  """ Commands used in this file """
  ADD_CHILD        = 1
  ADD_SIBLING      = 2
  DELETE           = 3
  SHOW_DETAILS     = 4
  HIDE             = 5
  OPEN_EXTERNAL    = 6
  OPEN_FILEBROWSER = 7
  ADD_ON           = 8
