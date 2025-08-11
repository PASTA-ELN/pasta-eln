""" Communication class that sends signals between widgets and the backend worker"""
import os
from pathlib import Path
from typing import Any
from PySide6.QtCore import QObject, Signal, Slot
from ..backendWorker.worker import BackendThread, Task
from ..miscTools import getConfiguration
from .palette import Palette
from .waitDialog import WaitDialog, Worker


class Communicate(QObject):
  """ Communication class that sends signals between widgets and the backend worker"""
  # General concept of the signals
  # - signals are defined either
  #   - here (signals / data send within the GUI or send data from GUI to backend worker)
  #   - in backendWorker/worker.py (signals = data send from backend worker to GUI)
  # - try to connect straight to those signals
  #   - only data that is common to two or more widgets is saved here here

  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  # signals request a change within the UI elements:
  changeSidebar      = Signal(str)       # redraw sidebar after hide/show of project in table, focus on this projectID
  changeTable        = Signal(str, str)    # send doctype,projectID from sidebar to main-table
                                           #      can also be used for hiding the details on right side if nothing to show
  changeDetails      = Signal(str)       # send docID from main-table to details
                                         #      docID (str): document-id; ''=draw nothing; 'redraw' implies redraw
  changeProject      = Signal(str, str)  # send docID,projectID from sidebar or main-table to projects
  stopSequentialEdit = Signal()          # in sequential edit, stop if there is a cancel
  # send data or data-request to backend
  commSendConfiguration = Signal(dict, str)     # send configuration and project-group-name to backend
  uiRequestDataHierarchy= Signal(str)           # get all entries in the data hierarchy for this docType
  uiRequestTable        = Signal(str, str, bool)# table: send docType, projectID, showAll to backend to get table
  uiRequestHierarchy    = Signal(str, bool)     # send project ID to backend
  uiRequestDoc          = Signal(str)           # request doc
  uiRequestTask         = Signal(Task, dict)    # request to execute a task
  uiSendSQL             = Signal(list)          # request to execute SQL commands directly
  # signals that are emitted from this comm that data changed
  docTypesChanged    = Signal()          # redraw main window, e.g. after change of docType titles

  # unclear
  formDoc            = Signal(dict)      # send doc from details to new/edit dialog: dialogForm
  testExtractor      = Signal()          # execute extractorTest in widgetDetails
  softRestart        = Signal()          # restart GUI

  def __init__(self, projectGroup:str=''):
    super().__init__()
    self.waitDialog            = WaitDialog()
    self.worker:Worker|None    = None
    self.palette                                = Palette(None, 'none')               #reset to real one later
    self.configuration, self.projectGroup = getConfiguration(projectGroup)
    if not self.configuration:
      return
    self.basePath = Path(self.configuration['projectGroups'][self.projectGroup]['local']['path'])

    # Data storage for all widgets
    self.docTypesTitles:dict[str,dict[str,str]] = {}# docType: {'title':title,'icon':icon,'shortcut':shortcut}
    self.dataHierarchyNodes:dict[str,list[Any]] = {}
    self.projectID                              = ''

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
      self.uiRequestTask.connect(self.backendThread.worker.returnTaskReport)
      self.uiSendSQL.connect(self.backendThread.worker.executeSQL)

      # connect GUI SLOTS to backend worker signals: group C
      self.backendThread.worker.beSendDataHierarchyNode.connect(self.onGetDataHierarchyNode)
      self.backendThread.worker.beSendDocTypes.connect(self.onGetDocTypes)

      # connect waiting dialog
      self.uiRequestTask.connect(self.progressWindow)
      self.backendThread.worker.beSendTaskReport.connect(self.waitDialog.hide)

      # start thread now that everything is linked up
      self.backendThread.start()
      self.commSendConfiguration.emit(self.configuration, self.projectGroup)


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
    """ Handle data received from backend worker
    Args:
      docType (str): document type
      data (list): list of nodes in the hierarchy for this docType
    """
    self.dataHierarchyNodes[docType] = data


  def shutdownBackendThread(self) -> None:
    """
    Shutdown backend thread
    """
    if self.backendThread is not None:
      self.backendThread.quit()
      self.backendThread.wait()
      del self.backendThread
    self.waitDialog.close()


  def progressWindow(self, task:Task, _:dict[str,Any]) -> None:
    """ Show a progress window and execute function
    Args:
      task (Task): task to execute
    """

    if task.msgWaitDialog == '' or 'PYTEST_CURRENT_TEST' in os.environ:
      return
    self.waitDialog.text.setMarkdown(task.msgWaitDialog)
    self.waitDialog.text.setFixedHeight(30)
    self.waitDialog.setFixedHeight(100)
    self.waitDialog.progressBar.setRange(0, 0)  # Indeterminate
    self.waitDialog.show()
