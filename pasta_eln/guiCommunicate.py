""" Communication class that sends signals between widgets, incl. backend"""
from typing import Any, Optional, Callable
from PySide6.QtCore import QObject, Signal  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QProgressBar  # pylint: disable=no-name-in-module
from .backend import Backend
from .GUI.waitDialog import WaitDialog, Worker


class Communicate(QObject):
  """ Communication class that sends signals between widgets, incl. backend"""
  def __init__(self, backend:Backend, palette:Any):
    super().__init__()
    self.backend               = backend
    self.palette               = palette
    self.projectID             = ''

  def progressWindow(self, taskFunction:Callable[[Callable[[str,str],None]],Any]) -> None:
    """ Show a progress window and execute function
    Args:
      taskFunction (func): function to execute
    """
    self.progressWindow = WaitDialog()
    self.progressWindow.show()
    self.worker = Worker(taskFunction)
    self.worker.progress.connect(self.progressWindow.updateProgressBar)
    self.worker.start()
    return



  # Signals: specify emitter and receiver
  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  changeSidebar      = Signal(str)       # redraw sidebar after hide/show of project in table, focus on this projectID
  changeTable        = Signal(str, str)  # send doctype,projectID from sidebar to main-table
                                         #      can also be used for hiding the details on right side if nothing to show
  changeDetails      = Signal(str)       # send docID from main-table to details
                                         #      docID (str): document-id; ''=draw nothing; 'redraw' implies redraw
  changeProject      = Signal(str, str)  # send docID,projectID from sidebar or main-table to projects
  formDoc            = Signal(dict)      # send doc from details to new/edit dialog: dialogForm
  testExtractor      = Signal()          # execute extractorTest in widgetDetails
  stopSequentialEdit = Signal()          # in sequential edit, stop if there is a cancel
