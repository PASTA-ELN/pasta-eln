""" Table Header dialog: change which colums are shown and in which order """
import json, platform
from enum import Enum
from pathlib import Path
from typing import Any
import qrcode
from PIL.ImageQt import ImageQt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGroupBox, QLineEdit, QDialogButtonBox, QFormLayout, QComboBox, QFileDialog, QMessageBox  # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QRegularExpressionValidator # pylint: disable=no-name-in-module
from cloudant.client import CouchDB
from ..guiStyle import Label, TextButton, IconButton, showMessage, widgetAndLayout
from ..miscTools import upOut, restart, upIn
from ..serverActions import testLocal, testRemote, passwordDecrypt
from ..guiCommunicate import Communicate

class ProjectGroup(QDialog):
  """ Table Header dialog: change which colums are shown and in which order """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      backend (Backend): PASTA-ELN backend
    """
    super().__init__()
    self.comm    = comm
    self.configuration = self.comm.backend.configuration

    # GUI elements
    self.setWindowTitle('Define and use project groups')
    self.setMinimumWidth(1000)
    mainL = QVBoxLayout(self)
    Label('Project group', 'h1', mainL)
    _, topbarL = widgetAndLayout('H', mainL, spacing='m')
    self.selectGroup = QComboBox()
    self.selectGroup.addItems(self.configuration['projectGroups'].keys())
    self.selectGroup.currentTextChanged.connect(self.changeProjectGroup)
    topbarL.addWidget(self.selectGroup)
    TextButton('New',         self, [Command.NEW],       topbarL)
    TextButton('Fill remote', self, [Command.FILL],      topbarL)
    TextButton('Create QR',   self, [Command.CREATE_QR], topbarL)
    TextButton('Check All',   self, [Command.CHECK],     topbarL)
    self.projectGroupName = QLineEdit('')
    self.projectGroupName.hide()
    mainL.addWidget(self.projectGroupName)
    _, bodyL = widgetAndLayout('H', mainL)
    #local
    localW = QGroupBox('Local credentials')
    localL = QFormLayout(localW)
    self.userNameL = QLineEdit('')
    self.userNameL.setValidator(QRegularExpressionValidator("[\\w.]{5,}"))
    localL.addRow('User name', self.userNameL)
    self.passwordL = QLineEdit('')
    self.passwordL.setValidator(QRegularExpressionValidator("\\S{5,}"))
    self.passwordL.setEchoMode(QLineEdit.PasswordEchoOnEdit)
    localL.addRow('Password', self.passwordL)
    self.databaseL = QLineEdit('')
    self.databaseL.setValidator(QRegularExpressionValidator("\\w{5,}"))
    localL.addRow('Database', self.databaseL)
    pathW, pathL = widgetAndLayout('H', spacing='s')
    self.pathL = QLineEdit('')
    pathL.addWidget(self.pathL, stretch=5) # type: ignore[call-arg]
    if platform.system()=='Windows':
      self.pathL.setValidator(QRegularExpressionValidator(r"[\\/~][\\w\\\\\\/:\.~]{5,}"))
    else:
      self.pathL.setValidator(QRegularExpressionValidator(r"[\\/~][\\w\\/]{5,}"))
    IconButton('fa5.folder-open', self, [Command.OPEN_DIR], pathL, 'Folder to save data in')
    localL.addRow('Path', pathW)
    bodyL.addWidget(localW)
    #remote
    remoteW = QGroupBox('Remote credentials')
    remoteL = QFormLayout(remoteW)
    self.userNameR = QLineEdit('')
    self.userNameR.setValidator(QRegularExpressionValidator("[\\w.]{5,}"))
    remoteL.addRow('User name', self.userNameR)
    self.passwordR = QLineEdit('')
    self.passwordR.setValidator(QRegularExpressionValidator("\\S{5,}"))
    self.passwordR.setEchoMode(QLineEdit.PasswordEchoOnEdit)
    remoteL.addRow('Password', self.passwordR)
    self.databaseR = QLineEdit('')
    self.databaseR.setValidator(QRegularExpressionValidator("\\w{5,}"))
    remoteL.addRow('Database', self.databaseR)
    self.serverR = QLineEdit('')
    self.serverR.setValidator(QRegularExpressionValidator("http:\\/\\/(?:[0-9]{1,3}\\.){3}[0-9]{1,3}:5984"))
    remoteL.addRow('Server', self.serverR)
    bodyL.addWidget(remoteW)
    #image
    self.image = QLabel()
    bodyL.addWidget(self.image)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.addButton('Save encrypted', QDialogButtonBox.AcceptRole)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    self.selectGroup.currentTextChanged.emit(self.configuration['defaultProjectGroup']) #emit to fill initially


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif 'Save' in btn.text() and self.checkEntries():
      name = self.projectGroupName.text() if self.selectGroup.isHidden() else self.selectGroup.currentText()
      if btn.text().endswith('Save'):
        localPath = self.pathL.text()
        if localPath.startswith('~'):
          localPath = (Path.home()/localPath[1:]).as_posix()
        local = {'user':self.userNameL.text(), 'password':self.passwordL.text(), \
                  'database':self.databaseL.text(), 'path':localPath}
        remote = {'user':self.userNameR.text(), 'password':self.passwordR.text(), \
                  'database':self.databaseR.text(), 'url':self.serverR.text()}
      elif btn.text().endswith('Save encrypted'):
        credL = upIn(f'{self.userNameL.text()}:{self.passwordL.text()}')
        credR = upIn(f'{self.userNameR.text()}:{self.passwordR.text()}')
        local = {'cred':credL, 'database':self.databaseL.text(), 'path':self.pathL.text()}
        remote = {'cred':credR, 'database':self.databaseR.text(), 'url':self.serverR.text()}
      newGroup = {'local':local, 'remote':remote}
      self.configuration['projectGroups'][name] = newGroup
      self.configuration['defaultProjectGroup'] = name
      with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.configuration,indent=2))
      restart()
    else:
      print('dialogProjectGroup: did not get a fitting btn ',btn.text())
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.NEW:
      self.selectGroup.hide()
      self.projectGroupName.show()
      self.projectGroupName.setText('my_project_group_name')
      defaultProjectGroup = self.configuration['defaultProjectGroup']
      config = self.configuration['projectGroups'][defaultProjectGroup]
      if 'cred' in config['local']:
        u,p = upOut(config['local']['cred'])[0].split(':')
      else:
        u,p = config['local']['user'], config['local']['password']
      self.userNameL.setText(u)
      self.userNameR.setText('')
      self.passwordL.setText(p)
      self.passwordR.setText('')
      self.databaseL.setText('')
      self.databaseR.setText('')
      self.pathL.setText('')
      self.serverR.setText('')
    elif command[0] is Command.FILL:
      content = QFileDialog.getOpenFileName(self, "Load remote credentials", str(Path.home()), '*.key')[0]
      with open(content, encoding='utf-8') as fIn:
        content = json.loads( passwordDecrypt(bytes(fIn.read(), 'UTF-8')) )
        self.userNameR.setText(content['user-name'])
        self.passwordR.setText(content['password'])
        self.databaseR.setText(content['database'])
        self.serverR.setText(content['Server'])
    elif command[0] is Command.CREATE_QR:
      if self.projectGroupName.isHidden():
        configname = self.selectGroup.currentText()
      else:
        configname = self.projectGroupName.text()
      qrCode = {"configname": configname, "credentials":{"server":self.serverR.text(), \
          "username":self.userNameR.text(), "password":self.passwordR.text(), "database":self.databaseR.text()}}
      img = qrcode.make(json.dumps(qrCode), error_correction=qrcode.constants.ERROR_CORRECT_M)
      pixmap = QPixmap.fromImage(ImageQt(img).scaledToWidth(200))
      self.image.setPixmap(pixmap)
    elif command[0] is Command.CHECK:
      self.checkEntries()
    elif command[0] is Command.OPEN_DIR:
      if dirName := QFileDialog.getExistingDirectory(self, 'Choose directory to save data', str(Path.home())):
        self.pathL.setText(dirName)
    else:
      print("**ERROR projectGroup unknown:",command)
    return


  def checkEntries(self) -> bool:
    """
    Check if entries are ok

    Returns:
      bool: success
    """
    # local
    localTest = testLocal(self.userNameL.text(), self.passwordL.text(), self.databaseL.text())
    if 'Error: Local database does not exist' in localTest and \
       'success: Local username and password ok' in localTest and self.databaseL.text():
      button = QMessageBox.question(self, "Question", "Local database does not exist. Should I create it?")
      if button == QMessageBox.Yes:
        localTest += '  Local data was created\n'
        client = CouchDB(self.userNameL.text(), self.passwordL.text(), url='http://127.0.0.1:5984', connect=True)
        client.create_database(self.databaseL.text())
      else:
        localTest += '  Local data was NOT created\n'
    if not self.pathL.text():
      localTest += 'ERROR: Local path not given\n'
    else:
      fullLocalPath = self.comm.backend.basePath/self.pathL.text()
      if fullLocalPath.exists():
        localTest += 'success: Local path exists\n'
      else:
        button = QMessageBox.question(self, "Question", "Local folder does not exist. Should I create it?")
        if button == QMessageBox.Yes:
          fullLocalPath.mkdir()
        else:
          localTest += 'ERROR: Local path does not exist\n'
    # remote
    remoteTest = ''
    if self.userNameR.text()!='' and self.passwordR.text()!='' and self.databaseR.text()!='' and \
        self.serverR.text()!='':
      remoteTest = testRemote(self.serverR.text(), self.userNameR.text(), self.passwordR.text(), \
        self.databaseR.text())
    # give output
    if 'ERROR' in localTest or 'ERROR' in remoteTest:
      showMessage(self, 'ERROR occurred', localTest+remoteTest, 'Critical')
      return False
    #success
    showMessage(self, 'Successful test', localTest+remoteTest, 'Information')
    return True


  def changeProjectGroup(self, item:str) -> None:
    """
    change the project group to this; do not save to file

    Args:
      item (str): name of project group
    """
    config = self.configuration['projectGroups'][item]
    if 'cred' in config['local']:
      u,p = upOut(config['local']['cred'])[0].split(':')
    else:
      u,p = config['local']['user'], config['local']['password']
    self.userNameL.setText(u)
    self.passwordL.setText(p)
    self.databaseL.setText(config['local']['database'])
    self.pathL.setText(config['local']['path'])
    if 'url' in config['remote']:
      if 'cred' in config['remote']:
        u,p = upOut(config['remote']['cred'])[0].split(':')
      else:
        u,p = config['remote']['user'], config['remote']['password']
      self.userNameR.setText(u)
      self.passwordR.setText(p)
      self.databaseR.setText(config['remote']['database'])
      self.serverR.setText(config['remote']['url'])
    return


class Command(Enum):
  """ Commands used in this file """
  NEW       = 1
  FILL      = 2
  CREATE_QR = 3
  CHECK     = 4
  OPEN_DIR  = 5
