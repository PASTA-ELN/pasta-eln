""" Upload for Zenodo and Dataverse """
import json
from enum import Enum
from typing import Any
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QCheckBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout,
                               QWidget)
from ...backend_worker.worker import Task
from ...configuration_file import saveConfiguration
from ..gui_communicate import Communicate
from ..gui_style import SPACE, Button, ButtonStyle, Label
from ..message_dialog import showMessage


class UploadGUI(QDialog):
  """ Upload for Zenodo and Dataverse """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication object
    """
    super().__init__()
    self.comm    = comm
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)
    self.finished.connect(self._cleanup)
    self.docProject:dict[str,Any] = {}
    self.setWindowTitle('Upload project to repository')
    self.setMinimumSize(985, 340)

    # GUI elements
    self.mainL = QVBoxLayout(self)
    self.leTitle                       = QLineEdit()
    self.leDescription                 = QLineEdit()
    self.leKeywords                    = QLineEdit()
    self.leCategory                    = QLineEdit()
    self.leAdditional                  = QLineEdit()
    self.allDocTypes:list[list[str]]   = []
    self.allCheckboxes:list[QCheckBox] = []

    if not self.comm.projectID:
      showMessage(self, 'Repository upload error', 'Open a project before uploading.', 'Critical')
      return
    self.comm.uiRequestDoc.emit(self.comm.projectID)


  @Slot(dict)
  def onGetData(self, doc:dict[str,Any]) -> None:
    """
    Callback function to handle the received data

    Args:
      doc (dict): project document
    """
    if self.comm.projectID and doc['id']==self.comm.projectID:
      self.docProject = doc
      self.paint()


  def paint(self) -> None:
    """ Paint the dialog with the current data """
    if not self.docProject:
      return
    Label('Upload project to repository', 'h1', self.mainL)
    centerW = QWidget(self)
    center = QHBoxLayout(centerW)
    center.setSpacing(SPACE.L)
    center.setContentsMargins(0, SPACE.M, 0, SPACE.L)
    self.mainL.addWidget(centerW)
    repositories = self.comm.configuration.get('repositories', {})
    leftSideW = QWidget(self)
    leftSide = QGridLayout(leftSideW)
    leftSide.setSpacing(10)
    leftSide.setContentsMargins(0, 0, 20, 0)
    center.addWidget(leftSideW)
    leftSide.setAlignment(Qt.AlignTop)                                            # type: ignore[attr-defined]
    leftSide.addWidget(Label('Metadata','h2'), 0, 0)
    leftSide.addWidget(QLabel('Title'), 1, 0)
    self.leTitle = QLineEdit(self.docProject['name'])
    self.leTitle.setMinimumWidth(400)
    leftSide.addWidget(self.leTitle, 1, 1)
    leftSide.addWidget(QLabel('Description'), 2, 0)
    self.leDescription = QLineEdit(self.docProject['comment'])
    leftSide.addWidget(self.leDescription, 2, 1)
    leftSide.addWidget(QLabel('Keywords'), 3, 0)
    self.leKeywords = QLineEdit(', '.join(self.docProject['tags']))
    leftSide.addWidget(self.leKeywords, 3, 1)
    leftSide.addWidget(QLabel('Repository category or community'), 4, 0)
    self.leCategory = QLineEdit(repositories.get('category',''))
    leftSide.addWidget(self.leCategory, 4, 1)
    leftSide.addWidget(QLabel('Additional'), 5, 0)
    self.leAdditional = QLineEdit(json.dumps(repositories.get('additional',{})))
    leftSide.addWidget(self.leAdditional, 5, 1)
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.VLine)
    separator.setFrameShadow(QFrame.Shadow.Sunken)
    center.addWidget(separator)

    self.allDocTypes = [[k,v['title']] for k,v in self.comm.docTypesTitles.items()]
    projectString = ', '.join(i[1] for i in self.allDocTypes if i[0].startswith('x'))
    rightSideW = QWidget(self)
    rightSide = QVBoxLayout(rightSideW)
    rightSide.setSpacing(SPACE.M)
    rightSide.setContentsMargins(0, 0, SPACE.L, 0)
    center.addWidget(rightSideW)
    rightSide.setAlignment(Qt.AlignTop)                                           # type: ignore[attr-defined]
    Label('Include item types','h2', rightSide)
    self.allCheckboxes = [QCheckBox(projectString, self)]
    self.allCheckboxes[0].setChecked(True)
    self.allCheckboxes[0].setDisabled(True)
    rightSide.addWidget(self.allCheckboxes[0])
    for i in self.allDocTypes:
      if not i[0].startswith('x') and '/' not in i[0]:
        checkbox = QCheckBox(i[1], self)                                     # pylint: disable=qt-local-widget
        checkbox.setChecked(True)
        self.allCheckboxes.append(checkbox)
        rightSide.addWidget(checkbox)

    #final button box
    buttonLineW = QWidget(self)
    buttonLineL = QHBoxLayout(buttonLineW)
    buttonLineL.setSpacing(SPACE.M)
    buttonLineL.setContentsMargins(0, 0, 0, 0)
    self.mainL.addWidget(buttonLineW)
    buttonLineL.addStretch(1)
    if 'zenodo' in repositories and 'url' in repositories['zenodo']:
      Button('Upload to Zenodo', self, (Command.UPLOAD, True), buttonLineL,
             style=ButtonStyle.HIGHLIGHTED)
    if 'dataverse' in repositories and 'url' in repositories['dataverse']:
      Button('Upload to Dataverse', self, (Command.UPLOAD, False), buttonLineL,
             style=ButtonStyle.HIGHLIGHTED)
    Button('Cancel', self, (Command.CANCEL,), buttonLineL, tooltip='Discard changes')


  def execute(self, command:'tuple[Command, bool] | tuple[Command]') -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.CANCEL:
      self.reject()
    elif command[0] is Command.UPLOAD:
      assert len(command) == 2
      # collect docTypes and create ELN
      docTypes = [i.text() for i in self.allCheckboxes if i.isChecked() and ', ' not in i.text()]
      # collect metadata and save parts of it
      metadata = {'title': self.leTitle.text(),
                  'description': self.leDescription.text(),
                  'keywords': [i.strip() for i in self.leKeywords.text().split(',') if i.strip()],
                  'category': self.leCategory.text(),
                  'additional': json.loads(self.leAdditional.text()),
                  'author': self.comm.configuration['authors'][0]}
      repositories = self.comm.configuration.setdefault('repositories', {})
      repositories['category'] = self.leCategory.text()
      repositories['additional'] = json.loads(self.leAdditional.text())
      saveConfiguration(self.comm.configuration)
      self.comm.uiRequestTask.emit(Task.SEND_REPOSITORY, {'projID': self.comm.projectID, 'docTypes': docTypes,
                'uploadZenodo':command[1], 'repositories': repositories, 'metadata': metadata})
      self.accept()
    else:
      print('Got some button, without definition', command)
    return


  def _cleanup(self, _result: int) -> None:
    """Disconnect backend signals when the dialog closes"""
    self.comm.backendThread.worker.beSendDoc.disconnect(self.onGetData)


class Command(Enum):
  """ Commands used in this file """
  UPLOAD = 1
  CANCEL = 2
