""" Custom tree view on data model """
import subprocess, os, platform, logging
from pathlib import Path
from PySide6.QtWidgets import QWidget, QTreeView, QAbstractItemView, QMenu # pylint: disable=no-name-in-module
from PySide6.QtGui import QStandardItemModel  # pylint: disable=no-name-in-module
from PySide6.QtCore import QPoint  # pylint: disable=no-name-in-module
from .widgetProjectLeafRenderer import ProjectLeafRenderer
from .style import Action, showMessage
from .communicate import Communicate

class TreeView(QTreeView):
  """ Custom tree view on data model """
  def __init__(self, parent:QWidget, comm:Communicate, model:QStandardItemModel):
    super().__init__(parent)
    self.comm = comm
    self.setModel(model)
    self.setHeaderHidden(True)
    self.setStyleSheet('QTreeView::branch {border-image: none;}')
    self.setIndentation(50)
    self.renderer = ProjectLeafRenderer()
    self.renderer.setCommunication(self.comm)
    self.setItemDelegate(self.renderer)
    self.setDragDropMode(QAbstractItemView.InternalMove)
    self.doubleClicked.connect(self.treeDoubleClicked)
    #TODO_P4 design of project tree
    # The gray boxes that represent folders/tasks, files or other items are too dark and have too little contrast
    # with black text on them (especially with small font). The boxes are also placed slightly too tight together,
    # I would increase the spacing between them by 1.5-2 times.


  def contextMenuEvent(self, p:QPoint) -> None:
    """
    create context menu

    Args:
      p (QPoint): point of clicking
    """
    context = QMenu(self)
    Action('Add child folder',   self.executeAction, context, self, name='addChild')
    Action('Add sibling folder', self.executeAction, context, self, name='addSibling')
    Action('Remove this',        self.executeAction, context, self, name='del')
    context.addSeparator()
    Action('Minimize/Maximize',  self.executeAction, context, self, name='fold')
    Action('Hide',               self.executeAction, context, self, name='hide')
    context.addSeparator()
    Action('Open with another application', self.executeAction, context, self, name='openExternal')
    context.exec(p.globalPos())
    return

  #TODO_P4 projectTree: drag&drop of external files
  def executeAction(self) -> None:
    """ after selecting a item from context menu """
    menuName = self.sender().data()
    if menuName=='addChild':
      hierStack = self.currentIndex().data().split('/')
      if hierStack[-1][0]=='x':
        docType= 'x'+str(len(hierStack))
        self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(hierStack[-1])['-branch'][0]['path'])
        self.comm.backend.addData(docType, {'-name':'new folder'}, hierStack)
        self.comm.changeProject.emit('','') #refresh project
      else:
        showMessage(self, 'Error', 'You cannot create a child of a non-folder!')
    elif menuName=='addSibling':
      hierStack= self.currentIndex().data().split('/')[:-1]
      docType= 'x'+str(len(hierStack))
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(hierStack[-1])['-branch'][0]['path'])
      self.comm.backend.addData(docType, {'-name':'new folder'}, hierStack)
      self.comm.changeProject.emit('','') #refresh project
    elif menuName=='del':
      docID = self.currentIndex().data().split('/')[-1]
      doc = self.comm.backend.db.remove(docID)
      for branch in doc['-branch']:
        oldPath = Path(self.comm.backend.basePath)/branch['path']
        if oldPath.exists():
          oldPath.rename( oldPath.parent/('trash_'+oldPath.name) )
      self.comm.changeProject.emit('','') #refresh project
    elif menuName=='fold':
      item = self.model().itemFromIndex(self.currentIndex())
      if item.text().endswith(' -'):
        item.setText(item.text()[:-2])
      else:
        item.setText(item.text()+' -')
    elif menuName=='hide':
      stack = self.currentIndex().data().split('/')
      logging.debug('hide stack '+str(stack))
      self.comm.backend.db.hideShow(stack)
      self.comm.changeProject.emit('','') #refresh project
    elif menuName=='openExternal':
      docID = self.currentIndex().data().split('/')[-1]
      doc   = self.comm.backend.db.getDoc(docID)
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
    """ after double-click on tree leaf: open form """
    docID = self.currentIndex().data().split('/')[-1]
    doc   = self.comm.backend.db.getDoc(docID)
    self.comm.formDoc.emit(doc)
    self.comm.changeProject.emit('','')
    return
