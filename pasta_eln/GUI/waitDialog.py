""" Dialog that shows a message and the progress-bar """
import re
from typing import Any, Callable
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialogButtonBox, QProgressBar, QTextBrowser, QVBoxLayout, QWidget


class WaitDialog(QWidget):
  """ Dialog that shows a message and the progress-bar """
  def __init__(self) -> None:
    """ Initialization """
    super().__init__()
    self.count  = 0
    self.mainL = QVBoxLayout()
    self.setMinimumWidth(400)
    self.setMinimumHeight(500)
    self.setWindowTitle('Wait for processes to finish')
    self.setLayout(self.mainL)

    self.text = QTextBrowser()
    self.text.setFixedHeight(450)
    self.text.setMarkdown('Default text')
    self.mainL.addWidget(self.text)
    self.progressBar = QProgressBar(self)
    self.progressBar.setMaximum(100)
    self.progressBar.setValue(0)
    self.mainL.addWidget(self.progressBar)
    self.mainL.addStretch(1)

    #final button box
    self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    self.buttonBox.clicked.connect(self.close)
    self.buttonBox.hide()
    self.mainL.addWidget(self.buttonBox)


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
      print(f"**ERROR unknown data {dType} {data}")
    self.progressBar.setValue(self.count)
    if self.count > 99:
      self.buttonBox.show()
    return



class Worker(QThread):
  """A generic worker thread that runs a given function."""
  progress = Signal(str, str)  # Signal to update the progress bar

  def __init__(self, task_function:Callable[[Callable[[str,str], None]], Any]):
    super().__init__()
    self.task_function = task_function  # Function to execute

  def run(self) -> None:
    """Runs the assigned function, providing a callback for progress updates."""
    try:
      self.task_function(self.progress.emit)  # Pass progress emitter as callback
    except Exception:
      pass
    return
