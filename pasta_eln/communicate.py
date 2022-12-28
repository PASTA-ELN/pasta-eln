""" Communication class that sends signals between widgets, incl. backend"""
from PySide6.QtCore import QObject, Signal   # pylint: disable=no-name-in-module

class Communicate(QObject):
  """ Communication class that sends signals between widgets, incl. backend"""
  def __init__(self, backend):
    super().__init__()
    self.backend = backend

  #Signals: specify emitter and receiver
  chooseDocType = Signal(str) #send doctype from sidebar to main-table
  # redrawSidebar = Signal()
