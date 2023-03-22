""" Communication class that sends signals between widgets, incl. backend"""
from PySide6.QtCore import QObject, Signal   # pylint: disable=no-name-in-module

class Communicate(QObject):
  """ Communication class that sends signals between widgets, incl. backend"""
  def __init__(self, backend):
    super().__init__()
    self.backend = backend

  # Signals: specify emitter and receiver
  # BE SPECIFIC ABOUT WHAT THIS ACTION DOES
  changeTable = Signal(str, str)         #send doctype,projectID from sidebar to main-table
  changeDetails = Signal(str)            #send docID from main-table to details
  changeProject = Signal(str, str)       #send docID,projectID from sidebar or main-table to projects
  formDoc = Signal(dict)                 #send doc from details to new/edit dialog: dialogForm
