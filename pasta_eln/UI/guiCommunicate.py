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
from ..miscTools import getConfiguration

class Communicate(QObject):
  """ Communication class that sends signals between widgets and the backend worker"""
  # General concept of the signals
  #   - signals are defined either
  #     - here (signals / data send within the GUI or send data from GUI to backend worker)
  #     - in backendWorker/worker.py (signals = data send from backend worker to GUI)

  #   any widget S (e.g. sidebar) requests a change widget T (e.g. table): emits signal [group A: name starts with 'change']
  #   comm receives signal and sends signal to backend worker [group B]
  #   backend receives signal, processes it, and sends data back to comm [group C in backendWorker]
  #   comm receives data and emits signal that that data was changed [group D: name ends with 'Changed']
  #   widget T reads the data from comm

  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  # signals request a change:
  changeSidebar      = Signal(str)       # redraw sidebar after hide/show of project in table, focus on this projectID
  changeTable        = Signal(str, str)  # send doctype,projectID from sidebar to main-table
                                         #      can also be used for hiding the details on right side if nothing to show
  changeDetails      = Signal(str)       # send docID from main-table to details
                                         #      docID (str): document-id; ''=draw nothing; 'redraw' implies redraw
  changeProject      = Signal(str, str)  # send docID,projectID from sidebar or main-table to projects
  # send data or data-request to backend
  commSendConfiguration = Signal(dict, str) # send configuration and project-group-name to backend
  uiRequestTable        = Signal(str, str, bool)  # send docType, projectID, showAll to backend to get table data
  uiRequestHierarchy    = Signal(str, bool) # send project ID to backend
  uiRequestDoc          = Signal(str)
  # group D: signals that are emitted from this comm that data changed
  docTypesChanged    = Signal()          # redraw main window, e.g. after change of docType titles

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
    self.dataHierarchyNodes:dict[str,list[Any]] = {}
    self.projectID                              = ''
    self.palette                                = Palette(None, 'none')               #reset to real one later

    if self.configuration:
      # Backend worker thread
      self.backendThread = BackendThread(self)
      # connect backend worker to configuration signals: send GUI->backend
      #   has to be here, else worker needs comm which has to be passed through thread, is uninitialized, ...)
      # connect backend worker SLOTS to GUI signals: group B
      self.commSendConfiguration.connect(self.backendThread.worker.initialize)
      self.uiRequestTable.connect(self.backendThread.worker.returnTable)
      self.uiRequestHierarchy.connect(self.backendThread.worker.returnHierarchy)
      self.uiRequestDoc.connect(self.backendThread.worker.returnDoc)

      # connect GUI SLOTS to backend worker signals: group C
      self.backendThread.worker.beSendDataHierarchyNode.connect(self.onGetDataHierarchyNode)
      self.backendThread.worker.beSendDocTypes.connect(self.onGetDocTypes)
      # start thread now that everything is linked up
      self.backendThread.start()
      self.commSendConfiguration.emit(self.configuration, self.configurationProjectGroup)

  @Slot(dict)
  def onGetDocTypes(self, data: dict[str, dict[str, str]]) -> None:
    """ Handle data received from backend worker
    Args:
      data (dict): dictionary with docType: {'title':title,'icon':icon,'shortcut':shortcut}
    """
    self.docTypesTitles = data
    self.docTypesChanged.emit()

  @Slot(str, list)
  def onGetDataHierarchyNode(self, docType:str, data:list[Any]) -> None:
    self.dataHierarchyNodes[docType] = data


  def shutdownBackendThread(self) -> None:
    """
    Shutdown backend thread
    """
    if self.backendThread is not None:
      self.backendThread.quit()
      self.backendThread.wait()
      del self.backendThread


  def progressWindow(self, taskFunction:Callable[[Callable[[str,str],None]],Any]) -> None:
    """ Show a progress window and execute function
    Args:
      taskFunction (func): function to execute
    """
    self.waitDialog.show()
    self.worker = Worker(taskFunction)
    self.worker.progress.connect(self.waitDialog.updateProgressBar)
    self.worker.start()
