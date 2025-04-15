""" Upload for Zenodo and Dataverse """
import json
import tempfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
import qtawesome as qta
from PySide6.QtCore import Qt  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QCheckBox, QDialog, QLabel, QLineEdit, QVBoxLayout  # pylint: disable=no-name-in-module
from ...fixedStringsJson import CONF_FILE_NAME
from ...guiCommunicate import Communicate
from ...guiStyle import Label, TextButton, showMessage, widgetAndLayout, widgetAndLayoutGrid
from ...inputOutput import exportELN
from .dataverse import DataverseClient
from .zenodo import ZenodoClient


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

    # GUI elements
    mainL = QVBoxLayout(self)
    Label('Upload to a repository', 'h1', mainL)
    _, center = widgetAndLayout('H', mainL, spacing='l', bottom='l', top='m')

    if not self.comm.projectID:
      return
    docProject = self.comm.backend.db.getDoc(self.comm.projectID)
    repositories = self.comm.backend.configuration['repositories']
    leftSideW, leftSide = widgetAndLayoutGrid(center, spacing='m', right='l')
    leftSideW.setStyleSheet('border-right: 2px solid black;')
    leftSide.setAlignment(Qt.AlignTop)                                            # type: ignore[attr-defined]
    leftSide.addWidget(Label('Metadata','h2'), 0, 0)
    leftSide.addWidget(QLabel('Title'), 1, 0)
    self.leTitle = QLineEdit(docProject['name'])
    self.leTitle.setMinimumWidth(400)
    leftSide.addWidget(self.leTitle, 1, 1)
    leftSide.addWidget(QLabel('Description'), 2, 0)
    self.leDescription = QLineEdit(docProject['comment'])
    leftSide.addWidget(self.leDescription, 2, 1)
    leftSide.addWidget(QLabel('Keywords'), 3, 0)
    self.leKeywords = QLineEdit(', '.join(docProject['tags']))
    leftSide.addWidget(self.leKeywords, 3, 1)
    leftSide.addWidget(QLabel('Category/Community'), 4, 0)
    self.leCategory = QLineEdit(repositories.get('category',''))
    leftSide.addWidget(self.leCategory, 4, 1)
    leftSide.addWidget(QLabel('Additional'), 5, 0)
    self.leAdditional = QLineEdit(json.dumps(repositories.get('additional',{})))
    leftSide.addWidget(self.leAdditional, 5, 1)

    self.allDocTypes = self.comm.backend.db.dataHierarchy('', 'title')
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
        checkbox = QCheckBox(i[1], self)
        checkbox.setChecked(True)
        self.allCheckboxes.append(checkbox)
        rightSide.addWidget(checkbox)

    #final button box
    _, buttonLineL = widgetAndLayout('H', mainL, 'm')
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
      tempELN = str(Path(tempfile.gettempdir())/'export.eln')
      res0 = exportELN(self.comm.backend, [self.comm.projectID], tempELN, docTypes)
      print('Export eln',res0)

      # collect metadata and save parts of it
      metadata = {'title': self.leTitle.text(),
                  'description': self.leDescription.text(),
                  'keywords': [i.strip() for i in self.leKeywords.text().split(',')],
                  'category': self.leCategory.text(),
                  'additional': json.loads(self.leAdditional.text()),
                  'author': self.comm.backend.configuration['authors'][0]}
      repositories = self.comm.backend.configuration['repositories']
      repositories['category'] = self.leCategory.text()
      repositories['additional'] = json.loads(self.leAdditional.text())
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.backend.configuration,indent=2))
      # convert to repository specific and upload to repository
      if command[1]: #Zenodo
        clientZ = ZenodoClient(repositories['zenodo']['url'], repositories['zenodo']['key'])
        metadataZ = clientZ.prepareMetadata(metadata)
        res = clientZ.uploadRepository(metadataZ, tempELN)
      else:          #Dataverse
        clientD = DataverseClient(repositories['dataverse']['url'], repositories['dataverse']['key'],
                                  repositories['dataverse']['dataverse'])
        metadataD = clientD.prepareMetadata(metadata)
        res = clientD.uploadRepository(metadataD, tempELN)
      showMessage(self, 'Success' if res[0] else 'Error', res[1])
      # update project with upload details
      if res[0]:
        docProject = self.comm.backend.db.getDoc(self.comm.projectID)
        docProject['.repository_upload'] = f'{datetime.now().strftime("%Y-%m-%d")} {res[1]}'
        docProject['branch'] = docProject['branch'][0] | {'op':'u'}
        self.comm.backend.db.updateDoc(docProject, self.comm.projectID)
      else:
        showMessage(self, 'Error', res[1])
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
