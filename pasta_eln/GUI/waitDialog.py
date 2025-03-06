""" Dialog that shows a message and the progress-bar """
from typing import Any, Callable
from PySide6.QtCore import QTimer
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QProgressBar, QTextEdit, QVBoxLayout


class WaitDialog(QDialog):
  """ Dialog that shows a message and the progress-bar """
  def __init__(self, callback:Callable[[Any], list[tuple[str, int]]]):
    """
    Initialization

    Args:
      callback (func): function that wants to receive the update function
    """
    super().__init__()
    self.callback = callback
    self.count  = 0
    self.callback = callback
    self.mainL = QVBoxLayout()
    self.setMinimumWidth(400)
    self.setMinimumHeight(500)
    self.setWindowTitle('Wait for processes to finish')
    self.setLayout(self.mainL)

    self.text = QTextEdit()
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
    self.buttonBox.clicked.connect(self.closeDialog)
    self.buttonBox.hide()
    self.mainL.addWidget(self.buttonBox)


  def showEvent(self, event:QShowEvent) -> None:
    """Called when the dialog is shown

    Args:
      event (QEvent): event called
    """
    super().showEvent(event)
    QTimer.singleShot(100, lambda: self.callback(self.updateProgressBar))  # Small delay to ensure it's fully rendered
    return


  def updateProgressBar(self, dType:str, data:str|int) -> None:
    """ update dialog
    - "text" and "append" will update the text
    - "count" and "incr" will update the progress-bar which runs until 100

    Args:
      dType (str): what to update and how "text", "append", "count", "incr"
      data (str): str- or int-value to update with
    """
    if dType=='text' and isinstance(data, str):
      self.text.setMarkdown(data)
    elif dType=='append' and isinstance(data, str):
      self.text.setMarkdown(self.text.toMarkdown().strip()+data)
    elif dType=='incr' and isinstance(data, int):
      self.count += data
    elif dType=='count' and isinstance(data, int):
      self.count = data
    else:
      print(f"**ERROR unknown data {dType} {data}")
    print(f"Waiting ... {dType}  {data if isinstance(data, int) else data.replace('\n','')}")
    self.progressBar.setValue(self.count)
    if self.count == 100:
      self.buttonBox.show()
    return


  def closeDialog(self) -> None:
    """ Close dialog can only be accept """
    self.accept()
    return
