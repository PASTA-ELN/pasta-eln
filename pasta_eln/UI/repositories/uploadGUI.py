""" Upload for Zenodo and Dataverse """
import json
from enum import Enum
from pathlib import Path
from typing import Any
import qtawesome as qta
from PySide6.QtCore import Qt, Slot                                        # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QCheckBox, QDialog, QLabel, QLineEdit, QVBoxLayout# pylint: disable=no-name-in-module
from ...backendWorker.worker import Task
from ...fixedStringsJson import CONF_FILE_NAME
from ..guiCommunicate import Communicate
from ..guiStyle import Label, TextButton, widgetAndLayout, widgetAndLayoutGrid
from ..messageDialog import showMessage


class UploadGUI(QDialog):
  """ Upload for Zenodo and Dataverse """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      backend (Backend): PASTA-ELN backend
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm    = comm
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)
    self.docProject:dict[str,Any] = {}
    self.setWindowTitle('Upload project to repository')

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
      showMessage(self, 'Error', 'You have to have an open project to upload', 'Critical')
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
    Label('Upload to a repository', 'h1', self.mainL)
    _, center = widgetAndLayout('H', self.mainL, spacing='l', bottom='l', top='m')
    repositories = self.comm.configuration['repositories']
    leftSideW, leftSide = widgetAndLayoutGrid(center, spacing='m', right='l')
    leftSideW.setStyleSheet('border-right: 2px solid black;')
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
    leftSide.addWidget(QLabel('Category/Community'), 4, 0)
    self.leCategory = QLineEdit(repositories.get('category',''))
    leftSide.addWidget(self.leCategory, 4, 1)
    leftSide.addWidget(QLabel('Additional'), 5, 0)
    self.leAdditional = QLineEdit(json.dumps(repositories.get('additional',{})))
    leftSide.addWidget(self.leAdditional, 5, 1)

    self.allDocTypes = [[k,v['title']] for k,v in self.comm.docTypesTitles.items()]
    projectString = ', '.join(i[1] for i in self.allDocTypes if i[0].startswith('x'))
    _, rightSide = widgetAndLayout('V', center, spacing='m', right='l')
    rightSide.setAlignment(Qt.AlignTop)                                           # type: ignore[attr-defined]
    Label('Include data types','h2', rightSide)
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
    _, buttonLineL = widgetAndLayout('H', self.mainL, 'm')
    buttonLineL.addStretch(1)
    if 'zenodo' in repositories and 'url' in repositories['zenodo']:
      TextButton('Upload to Zenodo',    self, [Command.UPLOAD, True],  buttonLineL)
    if 'dataverse' in repositories and 'url' in repositories['dataverse']:
      TextButton('Upload to Dataverse', self, [Command.UPLOAD, False], buttonLineL)
    TextButton('Cancel',              self, [Command.CANCEL], buttonLineL, 'Discard changes')


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.CANCEL:
      self.reject()
    elif command[0] is Command.UPLOAD:
      # collect docTypes and create .eln
      docTypes = [i.text() for i in self.allCheckboxes if i.isChecked() and ', ' not in i.text()]
      # collect metadata and save parts of it
      metadata = {'title': self.leTitle.text(),
                  'description': self.leDescription.text(),
                  'keywords': [i.strip() for i in self.leKeywords.text().split(',')],
                  'category': self.leCategory.text(),
                  'additional': json.loads(self.leAdditional.text()),
                  'author': self.comm.configuration['authors'][0]}
      repositories = self.comm.configuration['repositories']
      repositories['category'] = self.leCategory.text()
      repositories['additional'] = json.loads(self.leAdditional.text())
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.configuration,indent=2))
      self.comm.uiRequestTask.emit(Task.SEND_REPOSITORY, {'projID': self.comm.projectID, 'docTypes': docTypes,
                'uploadZenodo':command[1], 'repositories': repositories, 'metadata': metadata})
      self.accept()
    else:
      print('Got some button, without definition', command)
    return


  def changeButtonOnTest(self, success:bool, button:TextButton, message:str='') -> None:
    """ Helper function to change buttons upon success/failure

    Args:
      success (bool): change to successful state
      button (TextBotton): button to change
      message (str): optional message on failure
    """
    if success:
      button.setStyleSheet('background: #00FF00')
      button.setText('')
      button.setIcon(qta.icon('fa5s.check-square', scale_factor=1))
    else:
      if message:
        showMessage(self, 'Error', message)
      button.setStyleSheet('background: #FF0000')
      button.setText('')
      button.setIcon(qta.icon('fa5.times-circle', scale_factor=1))
    return


class Command(Enum):
  """ Commands used in this file """
  UPLOAD = 1
  CANCEL = 2
