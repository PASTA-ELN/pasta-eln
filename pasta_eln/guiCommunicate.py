""" Communication class that sends signals between widgets, incl. backend"""
from typing import Any, Callable
from PySide6.QtCore import QObject, Signal, Slot                           # pylint: disable=no-name-in-module
from .UI.waitDialog import WaitDialog, Worker
from .UI.palette import Palette
from .backendWorker.worker import BackendThread
from .miscTools import getConfiguration


class Communicate(QObject):
  """ Communication class that sends signals between widgets, incl. backend"""
  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  # Signals: specify emitter and receiver
  changeSidebar      = Signal(str)       # redraw sidebar after hide/show of project in table, focus on this projectID
  changeTable        = Signal(str, str)  # send doctype,projectID from sidebar to main-table
                                         #      can also be used for hiding the details on right side if nothing to show
  changeDetails      = Signal(str)       # send docID from main-table to details
                                         #      docID (str): document-id; ''=draw nothing; 'redraw' implies redraw
  changeProject      = Signal(str, str)  # send docID,projectID from sidebar or main-table to projects
  formDoc            = Signal(dict)      # send doc from details to new/edit dialog: dialogForm
  testExtractor      = Signal()          # execute extractorTest in widgetDetails
  stopSequentialEdit = Signal()          # in sequential edit, stop if there is a cancel
  softRestart        = Signal()          # restart GUI
  # send to backend
  commSendConfiguration = Signal(dict, str) # send configuration and project-group-name to backend

  def __init__(self, projectGroup:str=''):
    super().__init__()
    self.palette:None|Palette  = None
    self.projectID             = ''
    self.waitDialog            = WaitDialog()
    self.worker:Worker|None    = None
    self.configuration, self.configurationProjectGroup = getConfiguration(projectGroup)

    # Backend worker thread
    self.backendThread = BackendThread(self)
    # connect backend worker to configuration signals: send GUI->backend
    #   has to be here, because otherwise worker needs comm which has to be passed through thread, is uninitialized, ...)
    self.commSendConfiguration.connect(self.backendThread.worker.initialize)

    self.backendThread.start()
    self.commSendConfiguration.emit(self.configuration, self.configurationProjectGroup)

  @Slot(dict)
  def onGetDocTypes(self, data: dict) -> None:
    """Handle data received from backend worker"""
    print('Communicate.onGetDocTypes: received data from backend worker:', data)


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


