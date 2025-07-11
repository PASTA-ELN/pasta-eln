""" Table Header dialog: change which columns are shown and in which order """
import json
import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable
import qrcode
import qtawesome as qta
import requests
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap, QRegularExpressionValidator, Qt         # pylint: disable=no-name-in-module
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog,# pylint: disable=no-name-in-module
                               QLabel, QLineEdit, QMessageBox, QTextEdit, QVBoxLayout)
from ..elabFTWapi import ElabFTWApi
from ..fixedStringsJson import CONF_FILE_NAME
from ..guiCommunicate import Communicate
from ..miscTools import restart
from .guiStyle import IconButton, Label, TextButton, widgetAndLayoutGrid
from .messageDialog import showMessage


class ProjectGroup(QDialog):
  """ Table Header dialog: change which columns are shown and in which order """
  def __init__(self, comm:Communicate, callbackFinished:Callable[[bool],None]):
    """
    Initialization

    Args:
      backend (Backend): PASTA-ELN backend
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm    = comm
    self.projectGroupTested = False
    self.callbackFinished = callbackFinished
    self.configuration = self.comm.backend.configuration
    self.emptyConfig:dict[str,Any] = {'local':{'path':''}, 'remote':{}, 'addOnDir':''}
    self.elabApi: ElabFTWApi|None = None
    self.serverPG: set[tuple[str,Any,Any,Any]] = set()
    self.requireHardRestart = False

    # GUI elements
    mainL = QVBoxLayout(self)
    Label('Project group editor', 'h1', mainL)

    # LEFT SIDE: form
    _, self.formL = widgetAndLayoutGrid(mainL, spacing='m')
    self.selectGroup = QComboBox()
    self.selectGroup.addItems(self.configuration['projectGroups'].keys())
    self.selectGroup.currentTextChanged.connect(self.changeProjectGroup)
    self.formL.addWidget(self.selectGroup, 0, 0)
    self.groupTextField = QLineEdit()
    self.groupTextField.setValidator(QRegularExpressionValidator('\\w{3,}'))
    self.comboboxActive = True

    self.newButton = IconButton('fa5s.plus',    self, [Command.NEW], tooltip='New project group')
    self.formL.addWidget(self.newButton, 0, 2)
    self.delButton = IconButton('fa5s.trash',   self, [Command.DEL], tooltip='Delete project group')
    self.formL.addWidget(self.delButton, 0, 3)

    self.directoryLabel = QLabel('label')
    self.directoryLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard)
    self.formL.addWidget(self.directoryLabel, 1, 0, 1, 2)
    self.row1Button = IconButton('fa5.edit',   self, [Command.CHANGE_DIR], tooltip='Edit data path')
    self.formL.addWidget(self.row1Button, 1, 3)

    self.addOnLabel = QLabel('addon')
    self.addOnLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard)
    self.formL.addWidget(self.addOnLabel, 2, 0, 1, 2)
    self.row2Button = IconButton('fa5.edit',   self, [Command.CHANGE_ADDON], tooltip='Edit add-on path')
    self.formL.addWidget(self.row2Button, 2, 3)

    self.formL.addWidget(QLabel('Server address:'), 3, 0)
    self.serverLabel = QLineEdit('server')
    self.serverLabel.setPlaceholderText('Enter server address')
    self.formL.addWidget(self.serverLabel, 3, 1)
    self.row3Button = TextButton('Verify',   self, [Command.TEST_SERVER], tooltip='Check server')
    self.formL.addWidget(self.row3Button, 3, 3)

    self.formL.addWidget(QLabel('API-key:'), 4, 0)
    self.apiKeyLabel = QTextEdit()
    self.apiKeyLabel.setPlaceholderText('Enter API key')
    self.apiKeyLabel.setFixedHeight(48)
    # self.apiKeyLabel.setValidator(QRegularExpressionValidator(r"\d+-[0-9a-f]{85}"))
    self.formL.addWidget(self.apiKeyLabel, 4, 1)
    self.row4Button1 = IconButton('fa5s.question-circle', self,      [Command.TEST_API_HELP], tooltip='Help on obtaining API key')
    self.formL.addWidget(self.row4Button1, 4, 2)
    self.row4Button2 = TextButton('Verify',   self, [Command.TEST_APIKEY], tooltip='Check API-key')
    self.formL.addWidget(self.row4Button2, 4, 3)

    self.formL.addWidget(QLabel('Storage block:'), 5, 0)
    self.serverProjectGroupLabel = QComboBox()
    self.formL.addWidget(self.serverProjectGroupLabel, 5, 1)
    self.row5Button2 = TextButton('Verify',   self, [Command.TEST_SERVERPG], tooltip='Check access to storage block')
    self.formL.addWidget(self.row5Button2, 5, 3)

    # RIGHT SIDE: button and image
    self.qrButton = TextButton('Create QR code', self, [Command.CREATE_QRCODE])
    self.formL.addWidget(self.qrButton, 0, 6)
    self.image = QLabel()
    self.formL.addWidget(self.image, 1, 6, 4, 1)

    #final button box
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)

    #initialize
    if hasattr(self.comm.backend, 'configurationProjectGroup'):
      self.selectGroup.setCurrentText(self.comm.backend.configurationProjectGroup)
      self.selectGroup.currentTextChanged.emit(self.comm.backend.configurationProjectGroup)
    self.setStyleSheet(f"QLineEdit, QComboBox {{ {self.comm.palette.get('secondaryText', 'color')} }}")


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
      self.callbackFinished(False)
    elif 'Save' in btn.text() and not self.selectGroup.isHidden():
      if not self.comboboxActive:
        showMessage(self, 'Error', 'Fill out data and add-on location, first.')
        return
      # all information (excl. storage block) is already in self.configuration saved
      key      = self.selectGroup.currentText()
      config   = self.configuration['projectGroups'][key]
      if config['remote'].get('url','') and config['remote'].get('key','') and not self.projectGroupTested:
        showMessage(self, 'Error', 'Error: You have to select and test the storage block once successfully.')
        return
      if not config['local']['path']:
        showMessage(self, 'Error', 'Error: path to data directory is not set.')
        return
      if not config['addOnDir']:
        showMessage(self, 'Error', 'Error: add-on directory not set.')
        return
      # success
      choices = [i for i in self.serverPG if i[0]==self.serverProjectGroupLabel.currentText()]
      if choices and len(choices[0])==4:
        config['remote']['config'] = {'title':choices[0][0],
                                      'id':choices[0][1],
                                      'canRead':choices[0][2],
                                      'canWrite':choices[0][3]}
      defaultProjectGroup = self.configuration['defaultProjectGroup']
      if defaultProjectGroup not in self.configuration['projectGroups']:
        self.configuration['defaultProjectGroup'] = list(self.configuration['projectGroups'].keys())[0]

      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as confFile:
        confFile.write(json.dumps(self.configuration, indent=2))
      if self.requireHardRestart:
        restart()
      else:
        self.callbackFinished(True)
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if not self.comboboxActive:                            #first button press after entering a new group name
      newKey = self.groupTextField.text()
      self.selectGroup.addItem(newKey)
      self.selectGroup.setCurrentText(newKey)
      self.configuration['projectGroups'][newKey] = self.emptyConfig
      self.formL.removeWidget(self.groupTextField)
      self.formL.addWidget(self.selectGroup, 0,0)
      self.groupTextField.hide()
      self.comboboxActive = True
    key = self.selectGroup.currentText()
    if not key:
      return
    config = self.configuration['projectGroups'][key]

    #cases
    if command[0] is Command.CHANGE_DIR:
      answer = QFileDialog.getExistingDirectory(self, 'Specify new data directory')
      if not answer:
        return
      if [i for i in Path(answer).iterdir() if i.name=='pastaELN.db']:
        button = QMessageBox.question(self, 'Question', 'Do you want to use existing PASTA ELN data?',
                                      QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if button == QMessageBox.StandardButton.No:
          return
      elif list(Path(answer).iterdir()):
        button = QMessageBox.question(self, 'Question', 'Do you want to use folder, which is not empty? This is not recommended.',
                                      QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if button == QMessageBox.StandardButton.No:
          return
      config['local']['path'] = answer
      self.directoryLabel.setText(f'Data directory: {answer}')

    elif command[0] is Command.CHANGE_ADDON:
      answer = QFileDialog.getExistingDirectory(self, 'Specify new add-on directory')
      if not answer:
        return
      button = QMessageBox.question(self, 'Question', 'Do you want to copy the add-ons from the old directory (recommended)?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.Yes:
        source =Path(__file__).parent.parent/'AddOns'
        shutil.copytree(source, answer, dirs_exist_ok=True)
        self.requireHardRestart = True                                      #because python-path has to change
      config['addOnDir'] = answer
      config['addOns'] = {}
      self.addOnLabel.setText('Add on directory: ' + config['addOnDir'])

    elif command[0] is Command.TEST_SERVER:
      headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
      url     = self.serverLabel.text().strip()
      if not url:
        return
      if not url.endswith('/'):
        url += '/'
      if not url.endswith('api/v2/'):
        url += 'api/v2/'
      if not url.startswith('http'):
        url = f'https://{url}'
      config['remote']['url'] = url
      self.serverLabel.setText(url)
      try:
        requests.get(f'{url}info', headers=headers, verify=True, timeout=15)
        self.changeButtonOnTest(True, self.row3Button)
      except Exception:
        self.changeButtonOnTest(False, self.row3Button, 'Wrong server address')

    elif command[0] is Command.TEST_API_HELP:
      link = f'Go to: {config["remote"]["url"][:-7]}ucp.php?tab=4\n\n' if config['remote'].get('url','') else ''
      showMessage(self, 'Help', f'### How to get an api key to access the server:\n\n{link}'
                  'On the elabFTW server:\n\nClick on the User Symbol in the top right\n\nGo to "Settings"\n\n'
                  'Open the tab "API keys"\n\nCreate a new API key:\n\n  a) Specify a name, like "pasta_eln"\n\n  b) '
                  'Change the permissions to "Read/Write"\n\n  c) Click on "Generate new API key"\n\nCopy+Paste that '
                  'key into the text box on the right-hand side')
    elif command[0] is Command.TEST_APIKEY:
      if self.apiKeyLabel.toPlainText()!='--- API key hidden ---':
        config['remote']['key'] = self.apiKeyLabel.toPlainText().strip()
      headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization':config['remote']['key']}
      url = config['remote']['url']
      try:
        res = requests.get(f'{url}info', headers=headers, verify=True, timeout=15)
        if res.status_code==200:
          elabVersion = int(json.loads(res.content.decode('utf-8')).get('elabftw_version','0.0.0').split('.')[0])
          if elabVersion<5:
            showMessage(self, 'Error', 'Old elabFTW server installation')
          # success
          self.changeButtonOnTest(True, self.row4Button2)
          self.elabApi   = ElabFTWApi(url, config['remote']['key'])
          response = self.elabApi.readEntry('items?q=category%3AProjectGroup&archived=on')
          if not response:
            showMessage(self, 'Error', 'Please ask your database admin to add your project-group(s).')
          self.serverPG = {(i['title'],i['id'],i['canread'],i['canwrite']) for i in response}
          self.serverProjectGroupLabel.clear()
          self.serverProjectGroupLabel.addItems([i[0] for i in self.serverPG])
        else:
          self.changeButtonOnTest(False, self.row4Button2, 'Wrong API key')
      except Exception:
        self.changeButtonOnTest(False, self.row4Button2, 'Wrong API key')

    elif command[0] is Command.TEST_SERVERPG and self.elabApi is not None:
      idxList = [i[1] for i in self.serverPG if i[0]==self.serverProjectGroupLabel.currentText()]
      if not idxList:
        return
      idx = idxList[0]
      currentBody = self.elabApi.readEntry('items',idx)[0]['body']
      currentBody+= f'<br>Tested access by {self.configuration["userID"]} on {datetime.now().isoformat()} <br>'
      if self.elabApi.updateEntry('items',idx, {'body':currentBody}):
        self.projectGroupTested = True
        self.changeButtonOnTest(True, self.row5Button2)
      else:
        self.changeButtonOnTest(False, self.row5Button2, 'You do not have access to this project group')

    elif command[0] is Command.CREATE_QRCODE:
      text   = json.dumps(config['remote'])
      img    = qrcode.make(text, error_correction=qrcode.constants.ERROR_CORRECT_M).get_image()
      pixmap = QPixmap.fromImage(ImageQt(img).scaledToWidth(350))
      self.image.setPixmap(pixmap)

    elif command[0] is Command.NEW:
      #TODO: the self.selectGroup does not disappear
      # TODO: widget want you to create an addon folder, but it is not needed
      # when new project group: api-key is highlighted
      # new pg name has to be small letters, no spaces, no special characters
      #
      self.formL.removeWidget(self.selectGroup)
      self.formL.addWidget(self.groupTextField, 0, 0)
      self.directoryLabel.setText('Data directory: ')
      self.addOnLabel.setText('Add on directory: ')
      self.serverLabel.setText('')
      self.apiKeyLabel.setText('')
      self.image.setPixmap(QPixmap())
      self.comboboxActive = False

    elif command[0] is Command.DEL:
      button = QMessageBox.question(self, 'Question', 'Do you really want to delete this project group from the configuration (Data will remain)?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.Yes:
        del self.configuration['projectGroups'][key]
        self.selectGroup.removeItem(self.selectGroup.currentIndex())
        self.selectGroup.setCurrentIndex(0)
        self.execute([Command.TEST_APIKEY])
        self.execute([Command.TEST_SERVERPG])
    else:
      print('Got some button, without definition', command)
    return


  def changeProjectGroup(self, item:str) -> None:
    """
    change the project group to this; do not save to file

    Args:
      item (str): name of project group
    """
    config = self.configuration['projectGroups'].get(item, self.emptyConfig)
    self.directoryLabel.setText('Data directory: ' + config['local'].get('path',''))
    self.addOnLabel.setText('Add on directory: ' + config.get('addOnDir',''))
    self.serverLabel.setText(config['remote'].get('url', ''))
    if config['remote'].get('key', ''):
      self.apiKeyLabel.setText('--- API key hidden ---')
    else:
      self.apiKeyLabel.setText('')
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
  NEW          = 1
  DEL          = 2
  CHANGE_DIR   = 3
  CHANGE_ADDON = 4
  TEST_SERVER  = 5
  TEST_APIKEY  = 6
  TEST_API_HELP= 7
  CREATE_QRCODE= 8
  TEST_SERVERPG= 9
