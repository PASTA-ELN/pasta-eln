""" Backend worker thread for separating GUI and backend operations
CONNECT TO ALL SIGNALS IN COMMUNICATE
"""
import logging
from typing import Any, Optional
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Slot


class BackendWorker(QObject):
  """
  Backend worker that runs in a separate thread to handle all backend operations
  """
  # Signals to send data back to GUI
  beSendDocTypes = Signal(list)           # Send processed data back

  def __init__(self):
    super().__init__()
    self.configuration: Optional[dict] = None
    print('BackendWorker initialized')

  @Slot(dict)
  def initialize(self, configuration:dict) -> None:
    """ Initialize the backend worker with the given configuration """
    self.configuration = configuration
    print(f'BackendWorker initialized with configuration: {self.configuration}')

    # Example: Send processed data back
    self.beSendDocTypes.emit(list(configuration.keys()))


  def exit(self) -> None:
    """ Exit the worker thread """
    self.deleteLater()


class BackendThread(QThread):
  """
  Thread that manages the backend worker
  """
  def __init__(self, parent=None):
    """ Initialize the backend thread with a parent QObject
    Args:
      parent (QObject): Parent QObject for the thread
    """
    super().__init__(parent)
    self.worker = BackendWorker()
    self.worker.moveToThread(self)
    self.finished.connect(self.worker.exit)

  def run(self) -> None:
    """
    Run the thread event loop
    """
    self.exec()