""" Upload for Zenodo and Dataverse """
import json
import re
from enum import Enum
from pathlib import Path
from typing import Any, Callable
import qtawesome as qta
import webbrowser
from PySide6.QtWidgets import (QComboBox, QDialog, QLabel, QLineEdit,  QVBoxLayout, QCheckBox) # pylint: disable=no-name-in-module
from ...guiCommunicate import Communicate
from ...guiStyle import Label, TextButton, widgetAndLayout, widgetAndLayoutGrid, showMessage
from .zenodo import ZenodoClient
from .dataverse import DataverseClient
from ...fixedStringsJson import CONF_FILE_NAME

class UploadGUI(QDialog):
  """ Upload for Zenodo and Dataverse """
  def __init__(self, comm:Communicate, callbackFinished:Callable[[bool],None]):
    """
    Initialization

    Args:
      backend (Backend): PASTA-ELN backend
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm    = comm
    self.callbackFinished = callbackFinished
    self.configuration = self.comm.backend.configuration.get('repositories',{})

    # GUI elements
    mainL = QVBoxLayout(self)
    Label('Upload to a repository', 'h1', mainL)
    _, center = widgetAndLayout('H', mainL, spacing='l', bottom='l', top='m')


    leftSideW, leftSide = widgetAndLayoutGrid(center, spacing='m', right='l')
    leftSideW.setStyleSheet("border-right: 2px solid black;")
    Label('Metadata','h2', rightSide)
    # leftSide.addWidget(QLabel('URL'), 1, 0)
    # self.urlZenodo = QLineEdit('https://zenodo.org')
    # self.urlZenodo.setMinimumWidth(350)
    # leftSide.addWidget(self.urlZenodo, 1, 1)
    # leftSide.addWidget(QLabel('API key'), 2, 0)
    # self.apiZenodo = QLineEdit()
    # leftSide.addWidget(self.apiZenodo, 2, 1)
    # self.zenodoButton = TextButton('Check',   self, [Command.CHECK_ZENODO], tooltip='Check Zenodo login details')
    # leftSide.addWidget(self.zenodoButton, 3, 1)

    self.allDocTypes = self.comm.backend.db.dataHierarchy('', 'title')
    projectString = ', '.join(i[1] for i in self.allDocTypes if i[0].startswith('x'))
    _, rightSide = widgetAndLayout('V', center, spacing='m', right='l')
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
    TextButton('Upload to Zenodo',    self, [Command.UPLOAD, True],  buttonLineL)
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
      self.callbackFinished(False)
    elif command[0] is Command.UPLOAD:
      if 'repositories' not in self.configuration:
        self.configuration['repositories'] = {}
      if self.checkedZenodo:
        self.configuration['repositories']['zenodo'] = {'url':self.urlZenodo.text(),
                                                        'key':self.apiZenodo.text()}
      if self.checkedDataverse:
        self.configuration['repositories']['dataverse'] = {'url':self.urlDatavese.text(),
                                                          'key':self.apiDataverse.text(),
                                                          'dataverse':self.dvDataverse.currentData()}
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.configuration,indent=2))
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
