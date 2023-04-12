""" Table Header dialog: change which colums are shown and in which order """
import json
from pathlib import Path
import qrcode
from PIL.ImageQt import ImageQt
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, \
                              QLineEdit, QDialogButtonBox, QFormLayout, QLabel, QGroupBox, QComboBox, \
                              QTextEdit, QFileDialog  # pylint: disable=no-name-in-module
from PySide6.QtGui import QRegularExpressionValidator # pylint: disable=no-name-in-module
from .style import Label, TextButton, showMessage
from .miscTools import upOut, restart, upIn
from .serverActions import testLocal, testRemote, passwordDecrypt


class ProjectGroup(QDialog):
  """ Table Header dialog: change which colums are shown and in which order """
  def __init__(self, backend):
    """
    Initialization

    Args:
      backend (Backend): PASTA-ELN backend
    """
    super().__init__()
    self.backend = backend

    # GUI elements
    self.setWindowTitle('Define and use project groups')
    self.setMinimumWidth(1000)
    mainL = QVBoxLayout(self)
    Label('Project group', 'h1', mainL)
    topbarW = QWidget()
    topbarL = QHBoxLayout(topbarW)
    self.selectGroup = QComboBox()
    self.selectGroup.addItems(self.backend.configuration['projectGroups'].keys())
    self.selectGroup.currentTextChanged.connect(self.changeProjectGroup)
    topbarL.addWidget(self.selectGroup)
    TextButton('New', self.btnEvent, topbarL, 'new')
    TextButton('Fill remote', self.btnEvent, topbarL, 'fill')
    TextButton('Create QR', self.btnEvent, topbarL, 'createQR')
    TextButton('Check All', self.btnEvent, topbarL, 'check')
    mainL.addWidget(topbarW)
    self.projectGroupName = QLineEdit('')
    self.projectGroupName.hide()
    mainL.addWidget(self.projectGroupName)
    bodyW = QWidget()
    bodyL = QHBoxLayout(bodyW)
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
    self.pathL = QLineEdit('')
    self.pathL.setValidator(QRegularExpressionValidator("[\\w\\\\\\/:]{5,}"))
    localL.addRow('Path', self.pathL)
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
    mainL.addWidget(bodyW)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.addButton('Save encrypted', QDialogButtonBox.AcceptRole)
    buttonBox.clicked.connect(self.close)
    mainL.addWidget(buttonBox)
    self.selectGroup.currentTextChanged.emit(self.backend.configuration['defaultProjectGroup']) #emit to fill initially


  def close(self, btn):
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    print('project group press',btn.text() )
    if btn.text().endswith('Cancel'):
      self.reject()
    elif 'Save' in btn.text() and self.checkEntries():
      name = self.projectGroupName.text() if self.selectGroup.isHidden() else self.selectGroup.currentText()
      if btn.text().endswith('Save'):
        local = {'user':self.userNameL.text(), 'password':self.passwordL.text(), \
                'database':self.databaseL.text(), 'path':self.pathL.text()}
        remote = {'user':self.userNameR.text(), 'password':self.passwordR.text(), \
                'database':self.databaseR.text(), 'url':self.serverR.text()}
      elif btn.text().endswith('Save encrypted'):
        credL = upIn(self.userNameL.text()+':'+self.passwordL.text())
        credR = upIn(self.userNameR.text()+':'+self.passwordR.text())
        local = {'cred':credL, 'database':self.databaseL.text(), 'path':self.pathL.text()}
        remote = {'cred':credR, 'database':self.databaseR.text(), 'url':self.serverR.text()}
      newGroup = {'local':local, 'remote':remote}
      self.backend.configuration['projectGroups'][name] = newGroup
      self.backend.configuration['defaultProjectGroup'] = name
      with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.backend.configuration,indent=2))
      restart()
    else:
      print('dialogProjectGroup: did not get a fitting btn ',btn.text())
    return


  def btnEvent(self):
    """ events that occur when top-bar buttons are pressed """
    btnName = self.sender().accessibleName()
    if btnName=='new':
      self.selectGroup.hide()
      self.projectGroupName.show()
      self.projectGroupName.setText('my_project_group_name')
      self.userNameL.setText('')
      self.userNameR.setText('')
      self.passwordL.setText('')
      self.passwordR.setText('')
      self.databaseL.setText('')
      self.databaseR.setText('')
      self.pathL.setText('')
      self.serverR.setText('')
    elif btnName=='fill':
      content = QFileDialog.getOpenFileName(self, "Load remote credentials", str(Path.home()), '*.key')[0]
      with open(content, encoding='utf-8') as fIn:
        content = json.loads( passwordDecrypt(fIn.read()) )
        self.userNameR.setText(content['user-name'])
        self.passwordR.setText(content['password'])
        self.databaseR.setText(content['database'])
        self.serverR.setText(content['Server'])
    elif btnName=='createQR':
      if self.projectGroupName.isHidden():
        configname = self.selectGroup.currentText()
      else:
        configname = self.projectGroupName.text()
      qrCode = {"configname": configname, "credentials":{"server":self.serverR.text(), \
        "username":self.userNameR.text(), "password":self.passwordR.text(), "database":self.databaseR.text()}}
      img = qrcode.make(json.dumps(qrCode), error_correction=qrcode.constants.ERROR_CORRECT_M)
      pixmap = QPixmap.fromImage(ImageQt(img).scaledToWidth(200))
      self.image.setPixmap(pixmap)
    elif btnName=='check':
      self.checkEntries()
    return


  def checkEntries(self):
    """
    Check if entries are ok

    Returns:
      bool: success
    """
    # local
    localTest = testLocal(self.userNameL.text(), self.passwordL.text(), self.databaseL.text())
    if Path(self.pathL.text() ).exists():
      localTest += 'success: Local path exists\n'
    else:
      localTest += 'ERROR: Local path does not exist\n'
    # remote
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


  def changeProjectGroup(self, item):
    """
    change the project group to this; do not save to file

    Args:
      item (str): name of project group
    """
    config = self.backend.configuration['projectGroups'][item]
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
