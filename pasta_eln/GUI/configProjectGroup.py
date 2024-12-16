""" Table Header dialog: change which columns are shown and in which order """
import json, shutil
from enum import Enum
from pathlib import Path
from typing import Any, Callable
import qrcode, requests
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap, QRegularExpressionValidator                 # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFileDialog, QLabel, \
                              QLineEdit, QMessageBox, QVBoxLayout, QTextEdit   # pylint: disable=no-name-in-module
from ..guiCommunicate import Communicate
from ..guiStyle import IconButton, Label, TextButton, showMessage, widgetAndLayoutGrid
from ..fixedStringsJson import CONF_FILE_NAME


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
    self.callbackFinished = callbackFinished
    self.configuration = self.comm.backend.configuration
    self.emptyConfig:dict[str,Any] = {'local':{},'remote':{}}

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
    self.groupTextField.setValidator(QRegularExpressionValidator("\\w{3,}"))
    self.comboboxActive = True

    newButton = IconButton('fa5s.plus',    self, [Command.NEW], tooltip='New project group')
    self.formL.addWidget(newButton, 0, 2)
    delButton = IconButton('fa5s.trash',   self, [Command.DEL], tooltip='Delete project group')
    self.formL.addWidget(delButton, 0, 3)

    self.directoryLabel = QLabel('label')
    self.formL.addWidget(self.directoryLabel, 1, 0)
    row1Button = IconButton('fa5.edit',   self, [Command.CHANGE_DIR], tooltip='Edit data path')
    self.formL.addWidget(row1Button, 1, 3)

    self.addOnLabel = QLabel('addon')
    self.formL.addWidget(self.addOnLabel, 2, 0)
    row2Button = IconButton('fa5.edit',   self, [Command.CHANGE_ADDON], tooltip='Edit add-on path')
    self.formL.addWidget(row2Button, 2, 3)

    self.serverLabel = QLineEdit('server')
    self.serverLabel.setPlaceholderText('Enter server address')
    self.formL.addWidget(self.serverLabel, 3, 0)
    self.row3Button = IconButton('fa5s.check-square',   self, [Command.TEST_SERVER], tooltip='Check server')
    self.formL.addWidget(self.row3Button, 3, 3)

    self.apiKeyLabel = QTextEdit()
    self.apiKeyLabel.setPlaceholderText('Enter API key')
    self.apiKeyLabel.setFixedHeight(48)
    # self.apiKeyLabel.setValidator(QRegularExpressionValidator(r"\d+-[0-9a-f]{85}"))
    self.formL.addWidget(self.apiKeyLabel, 4, 0)
    row4Button1 = IconButton('fa5s.question-circle', self,      [Command.TEST_API_HELP], tooltip='Help on obtaining API key')
    self.formL.addWidget(row4Button1, 4, 2)
    self.row4Button2 = IconButton('fa5s.check-square',   self, [Command.TEST_APIKEY], tooltip='Check API-key')
    self.formL.addWidget(self.row4Button2, 4, 3)

    # RIGHT SIDE: button and image
    qrButton = TextButton('Create QR code', self, [Command.CREATE_QRCODE])
    self.formL.addWidget(qrButton, 0, 6)
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
      key      = self.selectGroup.currentText()
      config   = self.configuration['projectGroups'][key]
      headers  = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization':config['remote'].get('key','')}
      url      = config['remote'].get('url','')
      if url and config['remote'].get('key',''):
        response = requests.get(f'{url}info', headers=headers, verify=True, timeout=60)
        if response.status_code!=200:
          showMessage(self, 'Error', 'Error: server address or api key are incorrect.')
          return
      if not config['local']['path']:
        showMessage(self, 'Error', 'Error: path to data directory is not set.')
        return
      if not config['addOnDir']:
        showMessage(self, 'Error', 'Error: add-on directory not set.')
        return
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as confFile:
        confFile.write(json.dumps(self.configuration, indent=2))
      self.callbackFinished(True)
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if not self.comboboxActive:  #first button press after entering a new group name
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
      answer = QFileDialog.getExistingDirectory(self, "Specify new data directory")
      if not answer:
        return
      if [i for i in Path(answer).iterdir() if i.name=='pastaELN.db']:
        button = QMessageBox.question(self, "Question", "Do you want to use existing PASTA ELN data?",
                                      QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if button == QMessageBox.StandardButton.No:
          return
      elif list(Path(answer).iterdir()):
        button = QMessageBox.question(self, "Question", "Do you want to use folder, which is not empty? This is not recommended.",
                                      QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if button == QMessageBox.StandardButton.No:
          return
      config['local']['path'] = answer
      self.directoryLabel.setText('Data directory: ' + answer)

    elif command[0] is Command.CHANGE_ADDON:
      answer = QFileDialog.getExistingDirectory(self, "Specify new add-on directory")
      if not answer:
        return
      button = QMessageBox.question(self, "Question", "Do you want to copy the add-ons from the old directory (recommended)?",
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.Yes:
        print(config['addOnDir'] ,answer)
        shutil.copytree(config['addOnDir'], answer, dirs_exist_ok=True)
      config['addOnDir'] = answer
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
      if not url.startswith('https'):
        url = 'https://' + url
      config['remote']['url'] = url
      self.serverLabel.setText(url)
      try:
        requests.get(f'{url}info', headers=headers, verify=True, timeout=15)
        self.row3Button.setStyleSheet('background: #00FF00')
      except Exception:
        showMessage(self, 'Error', 'Wrong server address')
        self.row3Button.setStyleSheet('background: #FF0000')

    elif command[0] is Command.TEST_API_HELP:
      link = f'OR go to {config["remote"]["url"][:-7]}ucp.php?tab=4\n\n' if config["remote"].get("url",'') else ''
      showMessage(self, 'Help', '### How to get an api key to access the server:\nOn the elabFTW server:\n1. go to the USER SYMBOL\n2. User-(Control) panel\n3. API KEYS\n\n'\
                  f'{link}'\
                  '1. Specify a name: e.g. "pasta_eln"\n2. change the permissions to "Read/Write"\n3. click "Generate new API key"\n\nCopy-paste that key into the text box on the right-hand-side')

    elif command[0] is Command.TEST_APIKEY:
      config['remote']['key'] = self.apiKeyLabel.toPlainText().strip()
      headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Authorization':config['remote']['key']}
      url = config['remote']['url']
      try:
        response = requests.get(f'{url}info', headers=headers, verify=True, timeout=15)
        if response.status_code==200:
          elabVersion = int(json.loads(response.content.decode('utf-8')).get('elabftw_version','0.0.0').split('.')[0])
          if elabVersion<5:
            showMessage(self, 'Error', 'Old elabFTW server installation')
          self.row4Button2.setStyleSheet('background: #00FF00')
        else:
          showMessage(self, 'Error', 'Wrong API key')
          self.row4Button2.setStyleSheet('background: #FF0000')
      except Exception:
        showMessage(self, 'Error', 'Wrong API key')
        self.row4Button2.setStyleSheet('background: #FF0000')
    elif command[0] is Command.CREATE_QRCODE:
      text   = json.dumps(config['remote'])
      img    = qrcode.make(text, error_correction=qrcode.constants.ERROR_CORRECT_M).get_image()
      pixmap = QPixmap.fromImage(ImageQt(img).scaledToWidth(350))
      self.image.setPixmap(pixmap)

    elif command[0] is Command.NEW:
      self.formL.removeWidget(self.selectGroup)
      self.formL.addWidget(self.groupTextField, 0, 0)
      self.directoryLabel.setText('Data directory: ')
      self.addOnLabel.setText('Add on directory: ')
      self.serverLabel.setText('')
      self.apiKeyLabel.setText('')
      self.image.setPixmap(QPixmap())
      self.comboboxActive = False

    elif command[0] is Command.DEL:
      del self.configuration['projectGroups'][key]
      self.selectGroup.removeItem(self.selectGroup.currentIndex())
      self.selectGroup.setCurrentIndex(0)

    else:
      print("Got some button, without definition", command)
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
    self.apiKeyLabel.setText(config['remote'].get('key', ''))
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
