""" Dialog that shows a message and the progress-bar. The content is markdown! """
import logging
import re
from collections.abc import Callable
from enum import Enum, auto
from typing import Any
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QProgressBar, QTextBrowser, QVBoxLayout
from .widget import SPACE, Button, ButtonStyle


class WaitDialog(QDialog):
  """ Dialog that shows a message and the progress-bar. The content is markdown! """
  def __init__(self) -> None:
    """ Initialization """
    super().__init__()
    self.comm:Any = None
    self.setModal(True)
    self.count  = 0
    self.mainL = QVBoxLayout(self)
    self.mainL.setContentsMargins(SPACE.M, SPACE.M, SPACE.M, SPACE.M)
    self.mainL.setSpacing(SPACE.S)
    self.setMinimumWidth(500)
    self.setMinimumHeight(600)
    self.setWindowTitle('Wait for processes...')

    self.text = QTextBrowser()
    self.text.setFixedHeight(450)
    self.text.setMarkdown('Default text')
    self.mainL.addWidget(self.text)
    self.progressBar = QProgressBar(self)
    self.progressBar.setMaximum(100)
    self.progressBar.setValue(0)
    self.mainL.addWidget(self.progressBar)
    self.mainL.addStretch(1)

    # Completion action is shown only once the worker has finished.
    self.closeButton = Button('Close', self, Command.CLOSE, self.mainL, style=ButtonStyle.HIGHLIGHTED)
    self.closeButton.hide()


  def updateProgressBar(self, dType:str, data:str) -> None:
    """ update dialog
    - "text" and "append" will update the text
    - "count" and "incr" will update the progress-bar which runs until 100

    Args:
      dType (str): what to update and how "text", "append", "count", "incr"
      data (str): value to update with
    """
    if dType=='text':
      self.text.setMarkdown(data)
    elif dType=='append':
      self.text.setMarkdown(self.text.toMarkdown().strip()+data)
    elif dType=='incr' and re.match(r'^\d+$',data):
      self.count += int(data)
    elif dType=='count' and re.match(r'^\d+$',data):
      self.count = int(data)
    else:
      logging.error('Unknown data %s %s', dType, data, exc_info=True)
    self.progressBar.setValue(self.count)
    if self.count > 99:
      self.closeButton.show()
    return


  def execute(self, command:'Command') -> None:
    """Handle completion actions from the dialog footer."""
    if command is Command.CLOSE:
      self.close()


class Command(Enum):
  """Commands available in the wait dialog."""
  CLOSE = auto()



class Worker(QThread):
  """A generic worker thread that runs a given function."""
  progress = Signal(str, str)                                              # Signal to update the progress bar

  def __init__(self, taskFunction:Callable[[Callable[[str,str],None]],Any]):
    super().__init__()
    self.taskFunction = taskFunction                                                     # Function to execute

  def run(self) -> None:
    """Runs the assigned function, providing a callback for progress updates."""
    try:
      self.taskFunction(self.progress.emit)                                # Pass progress emitter as callback
    except Exception:
      pass
    return
