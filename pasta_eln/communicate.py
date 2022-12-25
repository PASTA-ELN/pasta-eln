from PySide6.QtCore import QObject, Signal

class Communicate(QObject):
  def __init__(self, backend):
    self.backend = backend

    #signals
    self.redrawSidebar = Signal(str)

