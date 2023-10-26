""" Custom tree view on data model """
import subprocess, os, platform, logging, shutil
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtWidgets import QWidget, QTreeView, QAbstractItemView, QMenu, QMessageBox # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel, QStandardItem  # pylint: disable=no-name-in-module
from PySide6.QtCore import QPoint, Qt  # pylint: disable=no-name-in-module
from .projectLeafRenderer import ProjectLeafRenderer
from ..guiStyle import Action, showMessage
from ..guiCommunicate import Communicate

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
    self.setDragDropMode(QAbstractItemView.InternalMove)
    self.doubleClicked.connect(self.tree2Clicked)


  def contextMenuEvent(self, p:QPoint) -> None:
    """
    create context menu

    Args:
      p (QPoint): point of clicking
    """
    folder = self.currentIndex().data().split('/')[-1][0]=='x'
    context = QMenu(self)
    if folder:
      Action('Add child folder',                   self, [Command.ADD_CHILD],      context)
    Action('Add sibling folder',                   self, [Command.ADD_SIBLING],    context)
    Action('Delete item',                          self, [Command.DELETE],         context)
    context.addSeparator()
    Action('Hide/show item details',               self, [Command.MAX_MIN_HEIGHT], context)
    Action('Mark item as hidden/shown',            self, [Command.HIDE],           context)
    context.addSeparator()
    if not folder:
      Action('Open file with another application', self, [Command.OPEN_EXTERNAL],    context)
    Action('Open folder in file browser',          self, [Command.OPEN_FILEBROWSER], context)
    context.exec(p.globalPos())
    return


  def execute(self, command:list[Any]) -> None:
    """
    after selecting a item from context menu

    Args:
      command (list): list of commands
    """
    hierStack = self.currentIndex().data().split('/')
    if command[0] is Command.ADD_CHILD:
      docType= f'x{len(hierStack)}'
      docID = hierStack[-1][:34] if hierStack[-1].endswith(' -') else hierStack[-1]
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['-branch'][0]['path'])
      label = self.comm.backend.db.dataHierarchy[docType]['label'].lower()[:-1]
      docID = self.comm.backend.addData(docType, {'-name':f'new {label}'}, hierStack)
      # append item to the GUI
      item  = self.model().itemFromIndex(self.currentIndex())
      child = QStandardItem('/'.join(hierStack+[docID]))
      child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled) # type: ignore
      item.appendRow(child)
      #appendRow is not 100% correct:
      # - better: insertRow before the first non-folder, depending on the child number
      #   -> get highest non 9999 childNumber
      # turns out, one can easily move it to correct position with drag&drop
      # -  not sure this will be important
    elif command[0] is Command.ADD_SIBLING:
      hierStack= hierStack[:-1]
      docType= f'x{len(hierStack)}'
      docID = hierStack[-1][:34] if hierStack[-1].endswith(' -') else hierStack[-1]
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['-branch'][0]['path'])
      label = self.comm.backend.db.dataHierarchy[docType]['label'].lower()[:-1]
      docID = self.comm.backend.addData(docType, {'-name':f'new {label}'}, hierStack)
      # append item to the GUI
      item  = self.model().itemFromIndex(self.currentIndex())
      parent = item.parent() if item.parent() is not None else self.model().invisibleRootItem()
      child = QStandardItem('/'.join(hierStack+[docID]))
      child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled) # type: ignore
      parent.appendRow(child)
      #++ TODO appendRow is not 100% correct: see above
    elif command[0] is Command.DELETE:
      ret = QMessageBox.critical(self, 'Warning', 'Are you sure you want to delete this data?',\
                                 QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
      if ret==QMessageBox.StandardButton.Yes:
        docID = hierStack[-1]
        doc = self.comm.backend.db.remove(docID)
        for branch in doc['-branch']:
          oldPath = Path(self.comm.backend.basePath)/branch['path']
          if oldPath.exists():
            newFileName = f'trash_{oldPath.name}'
            if (oldPath.parent/newFileName).exists():  #ensure target does not exist
              endText = ' was marked for deletion. Save it or its content now to some place on harddisk. It will be deleted now!!!'
              showMessage(self, 'Warning', f'Warning! \nThe folder {oldPath.parent/newFileName}{endText}')
              if (oldPath.parent/newFileName).exists():
                shutil.rmtree(oldPath.parent/newFileName)
            oldPath.rename( oldPath.parent/newFileName)
        # go through children
        children = self.comm.backend.db.getView('viewHierarchy/viewHierarchy', startKey=' '.join(doc['-branch'][0]['stack']+[docID,'']))
        for line in children:
          self.comm.backend.db.remove(line['id'])
        # remove leaf from GUI
        item  = self.model().itemFromIndex(self.currentIndex())
        parent = item.parent()
        if parent is None: #top level
          parent = self.model().invisibleRootItem()
        parent.removeRow(item.row())
    elif command[0] is Command.MAX_MIN_HEIGHT:
      item = self.model().itemFromIndex(self.currentIndex())
      if item.text().endswith(' -'):
        item.setText(item.text()[:-2])
      else:
        item.setText(f'{item.text()} -')
    elif command[0] is Command.HIDE:
      logging.debug('hide stack %s',str(hierStack))
      self.comm.backend.db.hideShow(hierStack)
      # self.comm.changeProject.emit('','') #refresh project
      # after hide, not immediately hidden but on next refresh
      # TODO Comment out for now to keep consistent with hide via context menu directly or form (which does
      # not know it is a project )
    elif command[0] is Command.OPEN_EXTERNAL or command[0] is Command.OPEN_FILEBROWSER:
      # depending if non-folder / folder; address different item in hierstack
      docID = hierStack[-2] \
        if command[0] is Command.OPEN_FILEBROWSER and hierStack[-1][0]!='x' \
        else hierStack[-1]
      doc   = self.comm.backend.db.getDoc(docID[:34] if docID.endswith(' -') else docID)
      if doc['-branch'][0]['path'] is None:
        showMessage(self, 'ERROR', 'Cannot open file that is only in the database','Warning')
      else:
        path  = Path(self.comm.backend.basePath)/doc['-branch'][0]['path']
        if platform.system() == 'Darwin':       # macOS
          subprocess.call(('open', path))
        elif platform.system() == 'Windows':    # Windows
          os.startfile(path) # type: ignore[attr-defined]
        else:                                   # linux variants
          subprocess.call(('xdg-open', path))
    else:
      print('**ERROR**: unknown context menu', command)
    return


  def tree2Clicked(self) -> None:
    """
    after double-click on tree leaf: open form
    - no redraw required since renderer asks automatically for update
    """
    docID = self.currentIndex().data().split('/')[-1]
    doc   = self.comm.backend.db.getDoc(docID[:34] if docID.endswith(' -') else docID)
    self.comm.formDoc.emit(doc)
    item  = self.model().itemFromIndex(self.currentIndex())
    item.emitDataChanged()  #force redraw (resizing and repainting) of this item only
    return


class Command(Enum):
  """ Commands used in this file """
  ADD_CHILD        = 1
  ADD_SIBLING      = 2
  DELETE           = 3
  MAX_MIN_HEIGHT   = 4
  HIDE             = 5
  OPEN_EXTERNAL    = 6
  OPEN_FILEBROWSER = 7
