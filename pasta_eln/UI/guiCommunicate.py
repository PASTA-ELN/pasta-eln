""" Communication class that sends signals between widgets and the backend worker"""
import base64
from typing import Any, Callable
from anytree import Node
import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot, QSize                    # pylint: disable=no-name-in-module
from PySide6.QtGui import QTextDocument, QPixmap                                    # pylint: disable=no-name-in-module
from .waitDialog import WaitDialog, Worker
from .palette import Palette
from ..backendWorker.worker import BackendThread
from ..fixedStringsJson import DO_NOT_RENDER, defaultDataHierarchyNode
from ..miscTools import getConfiguration
from ..textTools.handleDictionaries import doc2markdown
from ..textTools.stringChanges import markdownEqualizer

class Communicate(QObject):
  """ Communication class that sends signals between widgets and the backend worker"""
  # General concept of the signals
  #   any widget S (e.g. sidebar) requests a change widget T (e.g. table): emits signal [group A: name starts with 'change']
  #   comm receives signal and sends signal to backend worker [group B]
  #   backend receives signal, processes it, and sends data back to comm [group C in backendWorker]
  #   comm receives data and emits signal that that data was changed [group D: name ends with 'Changed']
  #   widget T reads the data from comm

  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  # group A: signals request a change:
  changeSidebar      = Signal(str)       # redraw sidebar after hide/show of project in table, focus on this projectID
  changeTable        = Signal(str, str)  # send doctype,projectID from sidebar to main-table
                                         #      can also be used for hiding the details on right side if nothing to show
  changeDetails      = Signal(str)       # send docID from main-table to details
                                         #      docID (str): document-id; ''=draw nothing; 'redraw' implies redraw
  changeProject      = Signal(str, str)  # send docID,projectID from sidebar or main-table to projects
  # group B: send request to backend
  commSendConfiguration = Signal(dict, str) # send configuration and project-group-name to backend
  commSendTableRequest  = Signal(str, str, bool)  # send docType, projectID, showAll to backend to get table data
  commSendHierarchyRequest = Signal(str, bool) # send project ID to backend
  commSendDoc        = Signal(str, str)
  # group D: signals that are emitted from this comm that data changed
  docTypesChanged    = Signal()          # redraw main window, e.g. after change of docType titles
  tableChanged       = Signal()          # redraw table, e.g. after change of table data
  hierarchyChanged   = Signal()          # redraw project view
  leafChanged        = Signal(str)       # redraw leaf of docID

  # unclear
  formDoc            = Signal(dict)      # send doc from details to new/edit dialog: dialogForm
  testExtractor      = Signal()          # execute extractorTest in widgetDetails
  stopSequentialEdit = Signal()          # in sequential edit, stop if there is a cancel
  softRestart        = Signal()          # restart GUI

  def __init__(self, projectGroup:str=''):
    super().__init__()
    self.waitDialog            = WaitDialog()
    self.worker:Worker|None    = None
    self.configuration, self.configurationProjectGroup = getConfiguration(projectGroup)

    # Data storage for all widgets
    self.docTypesTitles:dict[str,dict[str,str]] = {}# docType: {'title':title,'icon':icon,'shortcut':shortcut}
    self.docType                                = 'x0'
    self.dataHierarchyNodes                     = {}
    self.projects: pd.DataFrame                 = pd.DataFrame()     # for sidebar
    self.projectID                              = ''
    self.projectDoc                             = {}
    self.table                                  = pd.DataFrame()     # table data: measurements, projects, ...
    self.leafs                                  = {}# docID: {'size':..,'markdown':..,'content':..,'image':..}
    self.leafWidth                              = -1
    self.leafMarkdown                           = {}
    self.showAll                                = True
    self.palette:None|Palette                   = None

    # connect to GUI widget signals: group A
    self.changeTable.connect(self.toChangeTable)
    self.changeProject.connect(self.toChangeHierarchy)

    if self.configuration:
      # Backend worker thread
      self.backendThread = BackendThread(self)
      # connect backend worker to configuration signals: send GUI->backend
      #   has to be here, else worker needs comm which has to be passed through thread, is uninitialized, ...)
      # connect backend worker SLOTS to GUI signals: group B
      self.commSendConfiguration.connect(self.backendThread.worker.initialize)
      self.commSendTableRequest.connect(self.backendThread.worker.returnTable)
      self.commSendHierarchyRequest.connect(self.backendThread.worker.returnHierarchy)
      self.commSendDoc.connect(self.backendThread.worker.returnDoc)

      # connect GUI SLOTS to backend worker signals: group C
      self.backendThread.worker.beSendProjects.connect(self.onGetProjects)
      self.backendThread.worker.beSendDataHierarchyNode.connect(self.onGetDataHierarchyNode)
      self.backendThread.worker.beSendDocTypes.connect(self.onGetDocTypes)
      self.backendThread.worker.beSendTable.connect(self.onGetTable)
      self.backendThread.worker.beSendHierarchy.connect(self.onGetHierarchy)
      self.backendThread.worker.beSendDoc.connect(self.onGetDoc)
      # start thread now that everything is linked up
      self.backendThread.start()
      self.commSendConfiguration.emit(self.configuration, self.configurationProjectGroup)


  def toChangeTable(self, docType:str, projID:str) -> None:
    """ Ask backend worker to supply table data based on docType and projectID
    Args:
      docType (str): document type
      projID (str): project ID for filtering
    """
    self.commSendTableRequest.emit(docType, projID, self.showAll)

  def toChangeHierarchy(self, projID:str, _:str) -> None:
    """ Ask backened worker to supply hierarchy for projID
    Args:
      projID (str): project ID
    """
    self.commSendHierarchyRequest.emit(projID, self.showAll)


  @Slot(dict)
  def onGetDocTypes(self, data: dict[str, dict[str, str]]) -> None:
    """ Handle data received from backend worker
    Args:
      data (dict): dictionary with docType: {'title':title,'icon':icon,'shortcut':shortcut}
    """
    self.docTypesTitles = data
    self.docTypesChanged.emit()

  @Slot(str, list)
  def onGetDataHierarchyNode(self, docType:str, data:list):
    self.dataHierarchyNodes[docType] = data

  @Slot(pd.DataFrame)
  def onGetProjects(self, data: pd.DataFrame) -> None:
    """ Handle data received from backend worker
    Args:
      data (pd.DataFrame): DataFrame with projects
    """
    self.projects = data
    self.changeSidebar.emit('redraw')

  @Slot(pd.DataFrame)
  def onGetTable(self, data: pd.DataFrame) -> None:
    """ Handle data received from backend worker
    Args:
      data (pd.DataFrame): DataFrame with table data
    """
    self.table = data
    self.tableChanged.emit()

  @Slot(Node)
  def onGetHierarchy(self, data:Node, projDoc:dict[str,Any]) -> None:
    """ Handle data received from backend worker
    Args:
      data (Node): any node hierarchy
    """
    self.hierarchy = data
    self.projectDoc= projDoc
    self.hierarchyChanged.emit()

  @Slot(str, str)
  def onGetDoc(self, doc:dict[str,Any], task:str ) -> None:
    if doc['id'] not in self.leafs:
      self.leafs[doc['id']] = {}
    guiStyle = self.configuration['GUI']
    print(doc['id'], task)
    if task=='size':
      # ... after deleting project, its items cannot be found and it would give many false negatives
      if doc['type'][0] not in self.docTypesTitles:
        dataHierarchyNode = defaultDataHierarchyNode
      else:
        dataHierarchyNode = self.dataHierarchyNodes[doc['type'][0]]
      textDoc = QTextDocument()
      markdownStr = doc2markdown(doc, DO_NOT_RENDER, dataHierarchyNode, self)
      textDoc.setMarkdown(markdownStr)
      textDoc.setTextWidth(self.leafWidth)
      heightDetails = int(textDoc.size().toTuple()[1])+guiStyle['frameSize']+20# type: ignore
      heightRightSide = -1
      if 'content' in doc:
        textDoc.setMarkdown(doc['content'])
        heightRightSide = int(textDoc.size().toTuple()[1])                                        # type: ignore
      elif 'image' in doc and doc['image']:
        if doc['image'].startswith('data:image/'):
          pixmap = self.imageFromDoc(doc)
          heightRightSide = pixmap.height()+2*guiStyle['frameSize']
        else:
          heightRightSide = int(guiStyle['imageWidthProject']*3/4+2*guiStyle['frameSize'])
      self.leafs[doc['id']]['size']    = QSize(400, min(max(heightDetails,heightRightSide), guiStyle['maxProjectLeafHeight']))
      self.leafs[doc['id']]['hidden']  = any(b for b in doc['branch'] if False in b['show'])
      self.leafs[doc['id']]['markdown']= markdownStr
      self.leafs[doc['id']]['content'] = markdownEqualizer(doc['content']) if 'content' in doc else ''
      self.leafs[doc['id']]['image']   = doc.get('image','')
      self.leafChanged.emit(doc['id'])



  def shutdownBackendThread(self) -> None:
    """
    Shutdown backend thread
    """
    if self.backendThread is not None:
      self.backendThread.quit()
      self.backendThread.wait()
      self.backendThread = None


  def progressWindow(self, taskFunction:Callable[[Callable[[str,str],None]],Any]) -> None:
    """ Show a progress window and execute function
    Args:
      taskFunction (func): function to execute
    """
    self.waitDialog.show()
    self.worker = Worker(taskFunction)
    self.worker.progress.connect(self.waitDialog.updateProgressBar)
    self.worker.start()

  def imageFromDoc(self, doc:dict[str,Any]) -> QPixmap:
    """ Create image from image in doc

    Args:
      doc (dict): document

    Returns:
      QPixmap: image
    """
    result = QPixmap()
    result.loadFromData(base64.b64decode(doc['image'][22:]))
    result = result.scaledToWidth(self.configuration['GUI']['imageWidthProject'])
    if result.height()>self.configuration['GUI']['maxProjectLeafHeight']:
      result = result.scaledToHeight(self.configuration['GUI']['maxProjectLeafHeight'] -
                                     self.configuration['GUI']['frameSize']*2)
    return result
