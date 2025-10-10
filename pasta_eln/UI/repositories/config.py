""" Config for Zenodo and Dataverse """
import json
import re
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any, Callable
import qtawesome as qta
from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QLineEdit, QToolButton, QVBoxLayout
from ...backendWorker.dataverse import DataverseClient
from ...backendWorker.zenodo import ZenodoClient
from ...fixedStringsJson import CONF_FILE_NAME
from ..guiCommunicate import Communicate
from ..guiStyle import Label, TextButton, widgetAndLayout, widgetAndLayoutGrid
from ..messageDialog import showMessage


class ConfigurationRepositories(QDialog):
  """ Config for Zenodo and Dataverse """
  def __init__(self, comm:Communicate, callbackFinished:Callable[[bool],None]):
    """
    Initialization

    Args:
      backend (Backend): PASTA-ELN backend
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm    = comm
    conf = {'zenodo':{'url':'https://zenodo.org', 'key':''},'dataverse':{'url':'','key':'','dataverse':''},
            'category':'', 'additional': {}}
    conf |= self.comm.configuration.get('repositories', {})

    self.callbackFinished = callbackFinished
    self.checkedZenodo = False
    self.checkedDataverse = True
    self.setStyleSheet(f"QLineEdit {{ {self.comm.palette.get('secondaryText', 'color')} }}")

    # GUI elements
    mainL = QVBoxLayout(self)
    Label('Configure the repositories', 'h1', mainL)
    _, center = widgetAndLayout('H', mainL, spacing='l', bottom='l', top='m')

    leftSideW, leftSide = widgetAndLayoutGrid(center, spacing='m', right='l')
    leftSideW.setStyleSheet('border-right: 2px solid black;')
    leftSide.addWidget(QLabel('Zenodo'), 0, 0)
    leftSide.addWidget(QLabel('URL'), 1, 0)
    self.urlZenodo = QLineEdit(conf['zenodo']['url'])                                    # type: ignore[index]
    self.urlZenodo.setMinimumWidth(350)
    leftSide.addWidget(self.urlZenodo, 1, 1)
    leftSide.addWidget(QLabel('API key'), 2, 0)
    self.apiZenodo = QLineEdit(conf['zenodo']['key'])                                    # type: ignore[index]
    leftSide.addWidget(self.apiZenodo, 2, 1)
    self.apiZenodo.setEchoMode(QLineEdit.EchoMode.Password)
    self.zenodoToggle = QToolButton()
    self.zenodoToggle.setCheckable(True)
    self.zenodoToggle.setIcon(qta.icon('fa5s.eye-slash'))                                  # hidden by default
    def _toggle_zenodo(checked: bool) -> None:
      self.apiZenodo.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
      self.zenodoToggle.setIcon(qta.icon('fa5s.eye' if checked else 'fa5s.eye-slash'))
    self.zenodoToggle.toggled.connect(_toggle_zenodo)
    leftSide.addWidget(self.zenodoToggle, 2, 2)
    self.zenodoButton = TextButton('Check',   self, [Command.CHECK_ZENODO], tooltip='Check Zenodo login details')
    leftSide.addWidget(self.zenodoButton, 3, 1)

    _, rightSide = widgetAndLayoutGrid(center, spacing='m', right='l')
    rightSide.addWidget(QLabel('Dataverse'), 0, 0)
    rightSide.addWidget(QLabel('URL'), 1, 0)
    self.urlDatavese = QLineEdit(conf['dataverse']['url'])                               # type: ignore[index]
    self.urlDatavese.setMinimumWidth(350)
    rightSide.addWidget(self.urlDatavese, 1, 1)
    self.dataverseButton1 = TextButton('Check',   self, [Command.CHECK_DV1], tooltip='Check Dataverse server details')
    self.dataverseButton1.setMinimumWidth(100)
    rightSide.addWidget(self.dataverseButton1, 1, 3)
    rightSide.addWidget(QLabel('API key'), 2, 0)
    self.apiDataverse = QLineEdit(conf['dataverse']['key'])                              # type: ignore[index]
    self.apiDataverse.setEchoMode(QLineEdit.EchoMode.Password)
    self.dataverseToggle = QToolButton()
    self.dataverseToggle.setCheckable(True)
    self.dataverseToggle.setIcon(qta.icon('fa5s.eye-slash'))
    def _toggle_dataverse(checked: bool) -> None:
      self.apiDataverse.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
      self.dataverseToggle.setIcon(qta.icon('fa5s.eye' if checked else 'fa5s.eye-slash'))
    self.dataverseToggle.toggled.connect(_toggle_dataverse)
    rightSide.addWidget(self.dataverseToggle, 2, 2)
    rightSide.addWidget(self.apiDataverse, 2, 1)
    self.dataverseButton2 = TextButton('Check',   self, [Command.CHECK_DV2], tooltip='Check Dataverse API-key')
    rightSide.addWidget(self.dataverseButton2, 2, 3)
    rightSide.addWidget(QLabel('Sub dataverse'), 3, 0)
    self.dvDataverse = QComboBox()
    self.dvDataverse.addItem(conf['dataverse']['dataverse'])                             # type: ignore[index]
    self.dvDataverse.setStyleSheet(self.comm.palette.get('secondaryText', 'color'))
    rightSide.addWidget(self.dvDataverse, 3, 1)

    #final button box
    _, buttonLineL = widgetAndLayout('H', mainL, 'm')
    TextButton('Help',                self, [Command.HELP],   buttonLineL, 'Help for this dialog')
    buttonLineL.addStretch(1)
    self.saveBtn = TextButton('Save', self, [Command.SAVE],   buttonLineL, 'Save changes')
    self.saveBtn.setShortcut('Ctrl+Return')
    TextButton('Cancel',              self, [Command.CANCEL], buttonLineL, 'Discard changes')


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.CHECK_ZENODO:
      url = self.urlZenodo.text().strip()
      if re.match(r'(http:|https:)+\/\/[\w\.]+', url) is None:
        showMessage(self, 'Error', 'URL is not valid')
        return
      api = self.apiZenodo.text().strip()
      if re.match(r'\w{60}', api) is None:
        showMessage(self, 'Error', 'API key is not valid')
        return
      clientZ = ZenodoClient(url, api)
      success, message = clientZ.checkServer()
      if success:
        self.changeButtonOnTest(True, self.zenodoButton)
        self.checkedZenodo = True
      else:
        self.changeButtonOnTest(False, self.zenodoButton)
        showMessage(self, 'Error', message)

    elif command[0] is Command.CHECK_DV1:
      url = self.urlDatavese.text().strip()
      if re.match(r'(http:|https:)+\/\/[\w\.]+', url) is None:
        showMessage(self, 'Error', 'URL is not valid')
        return
      clientD = DataverseClient(url, '', '')
      success, message = clientD.checkServer()
      if success:
        self.changeButtonOnTest(True, self.dataverseButton1)
      else:
        self.changeButtonOnTest(False, self.dataverseButton1)
        showMessage(self, 'Error', message)

    elif command[0] is Command.CHECK_DV2:
      url = self.urlDatavese.text().strip()
      if re.match(r'(http:|https:)+\/\/[\w\.]+', url) is None:
        showMessage(self, 'Error', 'URL is not valid')
        return
      api = self.apiDataverse.text().strip()
      if re.match(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', api) is None:
        showMessage(self, 'Error', 'API key is not valid')
        return
      clientD = DataverseClient(url, api, '')
      if success := clientD.checkAPIKey():
        self.changeButtonOnTest(True, self.dataverseButton2)
        self.checkedDataverse = True
        self.dvDataverse.clear()
        for data in clientD.getDataverseList():
          self.dvDataverse.addItem(f"{data.get('title')} - {data.get('id')}", data.get('id'))
      else:
        self.changeButtonOnTest(False, self.dataverseButton2)
        showMessage(self, 'Error', 'API key invalid')

    elif command[0] is Command.CANCEL:
      self.reject()
      self.callbackFinished(False)

    elif command[0] is Command.SAVE:
      if 'repositories' not in self.comm.configuration:
        self.comm.configuration['repositories'] = {}
      if self.checkedZenodo:
        self.comm.configuration['repositories']['zenodo'] = {'url':self.urlZenodo.text(),
                                                             'key':self.apiZenodo.text()}
      if self.checkedDataverse:
        self.comm.configuration['repositories']['dataverse'] = {'url':self.urlDatavese.text(),
                                                          'key':self.apiDataverse.text(),
                                                          'dataverse':self.dvDataverse.currentData()}
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.configuration,indent=2))
      self.accept()
    elif command[0] is Command.HELP:
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/repositories.html')
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
  CHECK_ZENODO= 1
  CHECK_DV1   = 2
  CHECK_DV2   = 3
  HELP        = 4
  SAVE        = 5
  CANCEL      = 6
