""" Table Header dialog: change which columns are shown and in which order """
import json
from enum import Enum
from pathlib import Path
from typing import Any
import qrcode
from PIL.ImageQt import ImageQt
from PySide6.QtGui import QPixmap, QRegularExpressionValidator                 # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFileDialog, QLabel, \
                              QLineEdit, QMessageBox, QVBoxLayout, QTextEdit   # pylint: disable=no-name-in-module
from ..guiCommunicate import Communicate
from ..guiStyle import IconButton, Label, TextButton, showMessage, widgetAndLayoutGrid
from ..miscTools import restart


class ProjectGroup(QDialog):
  """ Table Header dialog: change which columns are shown and in which order """
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
    Label('Project group editor', 'h1', mainL)

    # LEFT SIDE: form
    formW, formL = widgetAndLayoutGrid(mainL, spacing='m')  #TODO TALK ABOUT WIDGET
    self.selectGroup = QComboBox()
    self.selectGroup.addItems(self.configuration['projectGroups'].keys())
    self.selectGroup.currentTextChanged.connect(self.changeProjectGroup)
    formL.addWidget(self.selectGroup, 0, 0)
    newButton = TextButton('New',      self, [Command.NEW])
    formL.addWidget(newButton, 0, 1)
    delButton = TextButton('Delete',   self, [Command.DEL])
    formL.addWidget(delButton, 0, 2)

    self.directoryLabel = QLabel('label')
    formL.addWidget(self.directoryLabel, 1, 0)
    row1Button = TextButton('Change',   self, [Command.CHANGE_DIR])
    formL.addWidget(row1Button, 1, 2)

    self.addOnLabel = QLabel('addon')
    formL.addWidget(self.addOnLabel, 2, 0)
    row2Button = TextButton('Change',   self, [Command.CHANGE_ADDON])
    formL.addWidget(row2Button, 2, 2)

    self.serverLabel = QLineEdit('server')
    formL.addWidget(self.serverLabel, 3, 0)
    row3Button = TextButton('Test',   self, [Command.TEST_SERVER])
    formL.addWidget(row3Button, 3, 2)

    self.apiKeyLabel = QTextEdit()
    self.apiKeyLabel.setFixedHeight(48)
    formL.addWidget(self.apiKeyLabel, 4, 0)
    row4Button1 = TextButton('Help',   self, [Command.TEST_API_HELP])
    formL.addWidget(row4Button1, 4, 1)
    row4Button2 = TextButton('Test',   self, [Command.TEST_APIKEY])
    formL.addWidget(row4Button2, 4, 2)

    # RIGHT SIDE: button and image
    qrButton = TextButton('Create QR code', self, [Command.CREATE_QRCODE])
    formL.addWidget(qrButton, 0, 5)
    self.image = QLabel()
    formL.addWidget(self.image, 1, 5, 4, 1)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    self.selectGroup.currentTextChanged.emit(self.configuration['defaultProjectGroup']) #emit to fill fields initially


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif 'Save' in btn.text():
      # TEST SERVER and API KEY -> save config
      restart()
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.CHANGE_DIR:
      answer = QFileDialog.getExistingDirectory(self, "Specify new data directory")
      if [i for i in Path(answer).iterdir() if i.name=='pastaELN.db']:
        button = QMessageBox.question(self, "Question", "Do you want to use existing PASTA ELN data?")
        if button == QMessageBox.StandardButton.No:
          return
      elif len([i for i in Path(answer).iterdir()]) > 0:
        button = QMessageBox.question(self, "Question", "Do you want to use folder, which is not empty? This is not recommended.")
        if button == QMessageBox.StandardButton.No:
          return
      key = self.selectGroup.currentText()
      config = self.configuration['projectGroups'][key]
      config['local']['path'] = answer
      self.directoryLabel.setText('Data directory: ' + answer)
    if command[0] is Command.CHANGE_ADDON:
      # ask for new directory: as above
      # don't worry if empty
      # ask if old add-ons should be copied into it
      pass
    if command[0] is Command.TEST_SERVER:
      # test connection
      pass
    if command[0] is Command.TEST_APIKEY:
      # test connection
      pass
    if command[0] is Command.CREATE_QRCODE:
      text = ''
      img = qrcode.make(text, error_correction=qrcode.constants.ERROR_CORRECT_M)
      pixmap = QPixmap.fromImage(ImageQt(img).scaledToWidth(200))
      self.image.setPixmap(pixmap)
    if command[0] is Command.NEW:
      # new project group name and empty all other fields
      pass
    if command[0] is Command.DEL:
      # delete from config
      # take first from list
      pass
    print(json.dumps(self.configuration['projectGroups'], indent=2))
    return


  def changeProjectGroup(self, item:str) -> None:
    """
    change the project group to this; do not save to file

    Args:
      item (str): name of project group
    """
    config = self.configuration['projectGroups'][item]
    self.directoryLabel.setText('Data directory: ' + config['local']['path'])
    self.addOnLabel.setText('Add on directory: ' + config['addOnDir'])
    self.serverLabel.setText(config['remote']['url'])
    self.apiKeyLabel.setText(config['remote']['key'])
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
