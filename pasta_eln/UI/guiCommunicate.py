""" Communication class that sends signals between widgets and the backend worker"""
from typing import Any, Callable
import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot                           # pylint: disable=no-name-in-module
from .waitDialog import WaitDialog, Worker
from .palette import Palette
from ..backendWorker.worker import BackendThread
from ..miscTools import getConfiguration

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
  # group D: signals that are emitted from this comm that data changed
  docTypesChanged    = Signal()          # redraw main window, e.g. after change of docType titles
  tableChanged       = Signal()          # redraw table, e.g. after change of table data

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
    self.palette:None|Palette  = None
    self.projects: pd.DataFrame = pd.DataFrame()
    self.docTypesTitles:dict[str,dict[str,str]] = {}  # docType: {'title': title, 'icon': icon, 'shortcut': shortcut}
    self.table                  = pd.DataFrame()  # table data: measurements, projects
    self.projectID              = ''
    self.docType                = 'x0'
    self.showAll                = True

    # connect to GUI widget signals: group A
    self.changeTable.connect(self.toChangeTable)

    if self.configuration:
      # Backend worker thread
      self.backendThread = BackendThread(self)
      # connect backend worker to configuration signals: send GUI->backend
      #   has to be here, because otherwise worker needs comm which has to be passed through thread, is uninitialized, ...)
      self.commSendConfiguration.connect(self.backendThread.worker.initialize)
      self.commSendTableRequest.connect(self.backendThread.worker.returnTable)

      self.backendThread.worker.beSendProjects.connect(self.onGetProjects)
      self.backendThread.worker.beSendDocTypes.connect(self.onGetDocTypes)
      self.backendThread.worker.beSendTable.connect(self.onGetTable)
      # start thread now that everything is linked up
      self.backendThread.start()
      self.commSendConfiguration.emit(self.configuration, self.configurationProjectGroup)


  def toChangeTable(self, docType:str, projID:str) -> None:
    """
    ask backend worker to supply new table data based on docType and projectID

    Args:
      docType (str): document type
      projID (str): project ID for filtering
    """
    self.commSendTableRequest.emit(docType, projID, self.showAll)


  @Slot(dict)
  def onGetDocTypes(self, data: dict[str, dict[str, str]]) -> None:
    """Handle data received from backend worker"""
    self.docTypesTitles = data
    self.docTypesChanged.emit()


  @Slot(pd.DataFrame)
  def onGetProjects(self, data: pd.DataFrame) -> None:
    """Handle data received from backend worker"""
    self.projects = data
    self.changeSidebar.emit('redraw')  # redraw sidebar to show projects

  @Slot(pd.DataFrame)
  def onGetTable(self, data: pd.DataFrame) -> None:
    """Handle data received from backend worker"""
    self.table = data
    self.tableChanged.emit()



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
    return


