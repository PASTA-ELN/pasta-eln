""" Custom tree view on data model """
import subprocess, os, platform, logging, shutil
from pathlib import Path
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
    self.doubleClicked.connect(self.treeDoubleClicked)


  def contextMenuEvent(self, p:QPoint) -> None:
    """
    create context menu

    Args:
      p (QPoint): point of clicking
    """
    folder = self.currentIndex().data().split('/')[-1][0]=='x'
    context = QMenu(self)
    if folder:
      Action('Add child folder',   self.executeAction, context, self, name='addChild')
    Action('Add sibling folder', self.executeAction, context, self, name='addSibling')
    Action('Delete item',        self.executeAction, context, self, name='del')
    context.addSeparator()
    Action('Minimize/Maximize',  self.executeAction, context, self, name='fold')
    Action('Hide',               self.executeAction, context, self, name='hide')
    context.addSeparator()
    if not folder:
      Action('Open file with another application', self.executeAction, context, self, name='openExternal')
    Action('Open folder in file browser', self.executeAction, context, self, name='openFileBrowser')
    context.exec(p.globalPos())
    return


  #TODO_P4 projectTree: drag&drop of external files
  def executeAction(self) -> None:
    # sourcery skip: extract-duplicate-method, extract-method
    """ after selecting a item from context menu """
    menuName = self.sender().data()
    hierStack = self.currentIndex().data().split('/')
    if menuName=='addChild':
      docType= f'x{len(hierStack)}'
      docID = hierStack[-1][:-2] if hierStack[-1].endswith(' -') else hierStack[-1]
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['-branch'][0]['path'])
      docID = self.comm.backend.addData(docType, {'-name':'new folder'}, hierStack)
      # append item to the GUI
      item  = self.model().itemFromIndex(self.currentIndex())
      child = QStandardItem('/'.join(hierStack+[docID]))
      child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled) # type: ignore
      item.appendRow(child)
      #appendRow is not 100% correct:
      # - better: insertRow before the first non-folder, depending on the child number
      #   -> get highest non 9999 childNumber
      # turns out, one can easily move it to correct position with drag&drop
      # TODO_P4 not sure this will be important
    elif menuName=='addSibling':
      hierStack= hierStack[:-1]
      docType= f'x{len(hierStack)}'
      docID = hierStack[-1][:-2] if hierStack[-1].endswith(' -') else hierStack[-1]
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(docID)['-branch'][0]['path'])
      docID = self.comm.backend.addData(docType, {'-name':'new folder'}, hierStack)
      # append item to the GUI
      item  = self.model().itemFromIndex(self.currentIndex())
      parent = item.parent() if item.parent() is not None else self.model().invisibleRootItem()
      child = QStandardItem('/'.join(hierStack+[docID]))
      child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled) # type: ignore
      parent.appendRow(child)
      #++ TODO appendRow is not 100% correct: see above
    elif menuName=='del':
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
    elif menuName=='fold':
      item = self.model().itemFromIndex(self.currentIndex())
      if item.text().endswith(' -'):
        item.setText(item.text()[:-2])
      else:
        item.setText(f'{item.text()} -')
    elif menuName=='hide':
      logging.debug('hide stack %s',str(hierStack))
      self.comm.backend.db.hideShow(hierStack)
      self.comm.changeProject.emit('','') #refresh project
    elif menuName in ['openExternal', 'openFileBrowser']:
      # depending if non-folder / folder; address different item in hierstack
      docID = hierStack[-2] if menuName=='openFileBrowser' and hierStack[-1][0]!='x' else hierStack[-1]
      doc   = self.comm.backend.db.getDoc(docID[:-2] if docID.endswith(' -') else docID)
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
      print('**ERROR**: unknown context menu', menuName)
    return


  def treeDoubleClicked(self) -> None:
    """
    after double-click on tree leaf: open form
    - no redraw required since renderer asks automatically for update
    """
    docID = self.currentIndex().data().split('/')[-1]
    doc   = self.comm.backend.db.getDoc(docID[:-2] if docID.endswith(' -') else docID)
    self.comm.formDoc.emit(doc)
    item  = self.model().itemFromIndex(self.currentIndex())
    item.emitDataChanged()  #force redraw (resizing and repainting) of this item only
    return
