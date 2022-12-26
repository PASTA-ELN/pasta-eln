from PySide6.QtCore import QObject, Signal

class Communicate(QObject):
  def __init__(self, backend):
    super(Communicate, self).__init__()
    self.backend = backend

  #Signals: specify emitter and receiver
  chooseDocType = Signal(str) #send doctype from sidebar to main-table

  # self.redrawSidebar = Signal()

