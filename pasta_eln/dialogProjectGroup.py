""" Table Header dialog: change which colums are shown and in which order """
import json
from pathlib import Path
import qrcode
from PIL.ImageQt import ImageQt
#pylint: disable=no-name-in-module
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, \
                              QLineEdit, QDialogButtonBox, QFormLayout, QLabel, QGroupBox, QComboBox, QTextEdit
from PySide6.QtGui import QPixmap, QImage
#pylint: enable=no-name-in-module
from .style import Label, TextButton
from .miscTools import upOut


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
    self.setWindowTitle('Select table headers')
    self.setMinimumWidth(1000)
    mainL = QVBoxLayout(self)
    Label('Project group', 'h1', mainL)
    topbarW = QWidget()
    topbarL = QHBoxLayout(topbarW)
    self.selectGroup = QComboBox()
    self.selectGroup.addItems([i for i in self.backend.configuration['projectGroups']])
    self.selectGroup.currentTextChanged.connect(self.changeProjectGroup)
    self.selectGroup.setCurrentText(self.backend.configuration['defaultProjectGroup'])
    topbarL.addWidget(self.selectGroup)
    TextButton('New', self.btnEvent, topbarL, 'new')
    TextButton('Fill remote', self.btnEvent, topbarL, 'fill')
    TextButton('Create QR', self.btnEvent, topbarL, 'createQR')
    TextButton('Check All', self.btnEvent, topbarL, 'check')
    mainL.addWidget(topbarW)
    self.messageW = QTextEdit()
    self.messageW.hide()
    mainL.addWidget(self.messageW)
    bodyW = QWidget()
    bodyL = QHBoxLayout(bodyW)
    #local
    localW = QGroupBox('Local credentials')
    localL = QFormLayout(localW)
    self.userNameL = QLineEdit('')
    localL.addRow('User name', self.userNameL)
    self.passwordL = QLineEdit('')
    self.passwordL.setEchoMode(QLineEdit.PasswordEchoOnEdit)
    localL.addRow('Password', self.passwordL)
    self.databaseL = QLineEdit('')
    localL.addRow('Database', self.databaseL)
    self.pathL = QLineEdit('')
    localL.addRow('Path', self.pathL)
    bodyL.addWidget(localW)
    #remote
    remoteW = QGroupBox('Remote credentials')
    remoteL = QFormLayout(remoteW)
    self.userNameR = QLineEdit('')
    remoteL.addRow('User name', self.userNameR)
    self.passwordR = QLineEdit('')
    self.passwordR.setEchoMode(QLineEdit.PasswordEchoOnEdit)
    remoteL.addRow('Password', self.passwordR)
    self.databaseR = QLineEdit('')
    remoteL.addRow('Database', self.databaseR)
    self.serverR = QLineEdit('')
    remoteL.addRow('Server', self.serverR)
    bodyL.addWidget(remoteW)
    #image
    self.image = QLabel()
    bodyL.addWidget(self.image)
    mainL.addWidget(bodyW)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.save)
    mainL.addWidget(buttonBox)
    self.selectGroup.currentTextChanged.emit(self.backend.configuration['defaultProjectGroup']) #emit to fill initially


  def save(self, btn):
    """ save selectedList to configuration and exit """
    if btn.text()=='Cancel':
      self.reject()
    elif btn.text()=='Save':
      #TODO
      self.accept()  #close
    return

  def btnEvent(self):
    """ events that occur when top-bar buttons are pressed """
    btnName = self.sender().accessibleName()
    if btnName=='new':
      pass
    elif btnName=='fill':
      pass
    elif btnName=='createQR':
      img = qrcode.make('hans', error_correction=qrcode.constants.ERROR_CORRECT_M)
      pixmap = QPixmap.fromImage(ImageQt(img))
      self.image.setPixmap(pixmap)
    elif btnName=='check':
      pass
    return


  def changeProjectGroup(self, item):
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
