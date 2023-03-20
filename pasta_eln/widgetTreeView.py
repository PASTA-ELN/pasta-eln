""" Custom tree view on data model """
import uuid, subprocess, os, platform
from pathlib import Path
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QMenu # pylint: disable=no-name-in-module
from PySide6.QtGui import QAction, QStandardItem                  # pylint: disable=no-name-in-module
from .widgetProjectLeafRenderer import ProjectLeafRenderer
from .style import Action

class TreeView(QTreeView):
  """ Custom tree view on data model """
  def __init__(self, parent, comm, model):
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


  def contextMenuEvent(self, e):
    """
    create context menu

    Args:
      e (QEvent): event
    """
    context = QMenu(self)
    Action('Add child folder',   self.executeAction, context, self, data='addChild')
    Action('Add sibling folder', self.executeAction, context, self, data='addSibling')
    Action('Remove this',        self.executeAction, context, self, data='del')
    context.addSeparator()
    Action('Minimize/Maximize',  self.executeAction, context, self, data='fold')
    Action('Hide',               self.executeAction, context, self, data='hide')
    context.addSeparator()
    Action('Open external program', self.executeAction, context, self, data='openExternal')
    context.exec(e.globalPos())

  #TODO_P2 fix numpy, scipy, lmfit, ... versions

  def executeAction(self):
    """ after selecting a item from context menu """
    menuName = self.sender().data()
    if menuName=='addChild':
      hierStack = self.currentIndex().data().split('/')
      docType= 'x'+str(len(hierStack))
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(hierStack[-1])['-branch'][0]['path'])
      self.comm.backend.addData(docType, {'-name':'folder 1', 'childNum':0}, hierStack)
      self.comm.changeProject.emit('','') #refresh project
    elif menuName=='addSibling':
      childNum = self.currentIndex().row()+1
      hierStack= self.currentIndex().parent().data().split('/')
      docType= 'x'+str(len(hierStack))
      self.comm.backend.cwd = Path(self.comm.backend.db.getDoc(hierStack[-1])['-branch'][0]['path'])
      self.comm.backend.addData(docType, {'-name':'folder '+str(childNum+1), 'childNum':childNum}, hierStack)
      self.comm.changeProject.emit('','') #refresh project
    elif menuName=='del':
      docID = self.currentIndex().data().split('/')[-1] #TODO_P1
      print('clicked context menu remove', docID)
    elif menuName=='fold':
      item = self.model().itemFromIndex(self.currentIndex())
      if item.text().endswith(' -'):
        item.setText(item.text()[:-2])
      else:
        item.setText(item.text()+' -')
    elif menuName=='hide':
      docID = self.currentIndex().data().split('/')[-1]
      print('clicked context menu hide', docID) #TODO_P1
    elif menuName=='openExternal':
      docID = self.currentIndex().data().split('/')[-1]
      doc   = self.comm.backend.db.getDoc(docID)
      path  = Path(self.comm.backend.basePath)/doc['-branch'][0]['path']
      if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', path))
      elif platform.system() == 'Windows':    # Windows
        os.startfile(path)
      else:                                   # linux variants
        subprocess.call(('xdg-open', path))
    else:
      print('**ERROR**: unknown context menu', menuName)
    return

  def treeDoubleClicked(self):
    """ after double-click on tree leaf: open form """
    docID = self.currentIndex().data()
    self.comm.formDoc.emit(self.comm.backend.db.getDoc(docID))
    return
