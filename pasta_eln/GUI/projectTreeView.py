""" Custom tree view on data model """
import logging
import os
import platform
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtCore import Qt  # pylint: disable=no-name-in-module
from PySide6.QtGui import (QDropEvent, QEventPoint, QStandardItem,  # pylint: disable=no-name-in-module
                           QStandardItemModel)
from PySide6.QtWidgets import (QAbstractItemView, QMenu, QMessageBox, QTreeView,  # pylint: disable=no-name-in-module
                               QWidget)
from ..guiCommunicate import Communicate
from ..guiStyle import Action, showMessage
from ..miscTools import callAddOn
from .projectLeafRenderer import ProjectLeafRenderer


class TreeView(QTreeView):
  """ Custom tree view on data model """
  def __init__(self, parent:QWidget, comm:Communicate, model:QStandardItemModel):
    super().__init__(parent)
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


  def contextMenuEvent(self, p:QEventPoint) -> None:                                                         # type: ignore[override]
    """
    create context menu

    Args:
      p (QPoint): point of clicking
    """
    item = self.model().itemFromIndex(self.currentIndex())                                                   # type: ignore[attr-defined]
    if item is None:  #clicked outside any leaf
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
      projectGroup = self.comm.backend.configuration['projectGroups'][self.comm.backend.configurationProjectGroup]
      if projectAddOns := projectGroup.get('addOns',{}).get('project',''):
        context.addSeparator()
        for label, description in projectAddOns.items():
          Action(description, self, [Command.ADD_ON, label], context)
    context.exec(p.globalPos())                                                                              # type: ignore[attr-defined]
    return


  def execute(self, command:list[Any]) -> None:
    """
    after selecting a item from context menu

    Args:
      command (list): list of commands
    """
    item = self.model().itemFromIndex(self.currentIndex())                                                   # type: ignore[attr-defined]
    hierStack = item.data()['hierStack'].split('/')
    if command[0] is Command.ADD_CHILD:
      docType= 'x1'
      docID = hierStack[-1]
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['branch'][0]['path'])
      docID = self.comm.backend.addData(docType, {'name':'new item'}, hierStack)['id']
      # append item to the GUI
      item  = self.model().itemFromIndex(self.currentIndex())                                                # type: ignore[attr-defined]
      child = QStandardItem('/'.join(hierStack+[docID]))
      child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled) # type: ignore
      item.appendRow(child)
      self.comm.changeProject.emit('','') #refresh project
      #appendRow is not 100% correct:
      # - better: insertRow before the first non-folder, depending on the child number
      #   -> get highest non 9999 childNumber
      # turns out, one can easily move it to correct position with drag&drop
      # -  not sure this will be important
    elif command[0] is Command.ADD_SIBLING:
      hierStack= hierStack[:-1]
      docType= 'x1'
      docID  = hierStack[-1]
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['branch'][0]['path'])
      docID = self.comm.backend.addData(docType, {'name':'new item'}, hierStack)['id']
      # append item to the GUI
      item  = self.model().itemFromIndex(self.currentIndex())                                                # type: ignore[attr-defined]
      parent = item.parent() if item.parent() is not None else self.model().invisibleRootItem()              # type: ignore[attr-defined]
      child = QStandardItem('/'.join(hierStack+[docID]))
      child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled) # type: ignore
      parent.appendRow(child)
      self.comm.changeProject.emit('','') #refresh project
      #++ TODO appendRow is not 100% correct: see above
    elif command[0] is Command.DELETE:
      ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete this data?',\
                                 QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
      if ret==QMessageBox.StandardButton.Yes:
        docID = hierStack[-1]
        doc = self.comm.backend.db.remove(docID)
        for branch in doc['branch']:
          if branch['path'] is not None:
            oldPath = Path(self.comm.backend.basePath)/branch['path']
            if oldPath.exists():
              newFileName = f'trash_{oldPath.name}'
              if (oldPath.parent/newFileName).exists():  #ensure target does not exist
                endText = ' was marked for deletion. Save it or its content now to some place on harddisk. It will be deleted now!!!'
                showMessage(self, 'Warning', f'Warning! \nThe folder {oldPath.parent/newFileName}{endText}')
                if (oldPath.parent/newFileName).is_file():
                  (oldPath.parent/newFileName).unlink()
                elif (oldPath.parent/newFileName).is_dir():
                  shutil.rmtree(oldPath.parent/newFileName)
              oldPath.rename( oldPath.parent/newFileName)
        # go through children
        children = self.comm.backend.db.getView('viewHierarchy/viewHierarchyAll', startKey='/'.join(doc['branch'][0]['stack']+[docID,'']))
        for line in children:
          self.comm.backend.db.remove(line['id'], stack='/'.join(doc['branch'][0]['stack']+[docID,'']))
        # remove leaf from GUI
        item  = self.model().itemFromIndex(self.currentIndex())                                              # type: ignore[attr-defined]
        parent = item.parent()
        if parent is None: #top level
          parent = self.model().invisibleRootItem()                                                           # type: ignore[attr-defined]
        parent.removeRow(item.row())
    elif command[0] is Command.SHOW_DETAILS:
      item = self.model().itemFromIndex(self.currentIndex())                                                 # type: ignore[attr-defined]
      gui  = item.data()['gui']
      docID = item.data()['hierStack'].split('/')[-1]
      gui[0] = not gui[0]
      item.setData({ **item.data(), **{'gui':gui}})
      self.comm.backend.db.setGUI(docID, gui)
    elif command[0] is Command.HIDE:
      logging.debug('hide document %s',hierStack[-1])
      self.comm.backend.db.hideShow(hierStack[-1])
      # self.comm.changeProject.emit('','') #refresh project
      # after hide, do not hide immediately but wait on next refresh
    elif command[0] is Command.OPEN_EXTERNAL or command[0] is Command.OPEN_FILEBROWSER:
      # depending if non-folder / folder; address different item in hierstack
      docID = hierStack[-2] \
        if command[0] is Command.OPEN_FILEBROWSER and hierStack[-1][0]!='x' \
        else hierStack[-1]
      doc   = self.comm.backend.db.getDoc(docID)
      if doc['branch'][0]['path'] is None:
        showMessage(self, 'ERROR', 'Cannot open file that is only in the database','Warning')
      else:
        path  = Path(self.comm.backend.basePath)/doc['branch'][0]['path']
        if platform.system() == 'Darwin':       # macOS
          subprocess.call(('open', path))
        elif platform.system() == 'Windows':    # Windows
          os.startfile(path) # type: ignore[attr-defined]
        else:                                   # linux variants
          subprocess.call(('xdg-open', path))
    elif command[0] is Command.ADD_ON:
      callAddOn(command[1], self.comm.backend, item.data()['hierStack'], self)
    else:
      print('**ERROR**: unknown context menu', command)
    return


  def tree2Clicked(self) -> None:
    """
    after double-click on tree leaf: open form
    - no redraw required since renderer asks automatically for update
    """
    item = self.model().itemFromIndex(self.currentIndex())                                                   # type: ignore[attr-defined]
    docID = item.data()['hierStack'].split('/')[-1]
    doc   = self.comm.backend.db.getDoc(docID)
    self.comm.formDoc.emit(doc)
    docNew = self.comm.backend.db.getDoc(docID)
    item.setText(docNew['name'])
    item.setData(item.data() | {'docType':docNew['type'], 'gui':docNew['gui']})
    item.emitDataChanged()  #force redraw (resizing and repainting) of this item only
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
    if event.mimeData().hasUrls():  #file rometo to pasta
      item = self.model().itemFromIndex(self.indexAt(event.pos()))                                           # type: ignore[attr-defined]
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
          files +=   list(Path(path).rglob('*'))                                                             # type: ignore[arg-type]
          folders += [x[0] for x in os.walk(path)]
      if not (folders+[str(i) for i in files]):
        showMessage(self, 'Error', 'The files seem empty.')
        return
      commonBase   = os.path.commonpath(folders+[str(i) for i in files])
      docID = item.data()['hierStack'].split('/')[-1]
      doc = self.comm.backend.db.getDoc(docID)
      targetFolder = Path(self.comm.backend.cwd/doc['branch'][0]['path'])
      # create folders and copy files
      for folder in folders:
        (targetFolder/(Path(folder).relative_to(commonBase))).mkdir(parents=True, exist_ok=True)
      for fileStr in files:
        file = Path(fileStr)
        if file.is_file():
          shutil.copy(file, targetFolder/(file.relative_to(commonBase)))
      # scan
      for _ in range(2):  #scan twice: convert, extract
        self.comm.backend.scanProject(None, docID, targetFolder.relative_to(self.comm.backend.basePath))
      self.comm.changeProject.emit(item.data()['hierStack'].split('/')[0],'')
      showMessage(self, 'Information','Drag & drop is finished')
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
