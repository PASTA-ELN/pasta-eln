""" Main class of config tab on authors """
import json
import re, logging
from enum import Enum
from pathlib import Path
from typing import Any, Callable
import requests
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QLineEdit, QVBoxLayout# pylint: disable=no-name-in-module
from ..fixedStringsJson import CONF_FILE_NAME
from ..guiCommunicate import Communicate
from .guiStyle import IconButton, TextButton, widgetAndLayout, widgetAndLayoutForm


class ConfigurationAuthors(QDialog):
  """ Main class of config tab on authors

  FOR NOW: only one author (one self) can be added to align with GDPR
  """
  def __init__(self, comm:Communicate, callbackFinished:Callable[[bool],None]):
    """
    Initialization

    Args:
      comm (Communicate): communication
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm = comm
    self.callbackFinished = callbackFinished
    mainL = QVBoxLayout(self)
    self.textFields:dict[str, QLineEdit] = {}

    #GUI elements
    if hasattr(self.comm.backend, 'configuration'):
      self.author = self.comm.backend.configuration['authors'][0]
      _, self.tabAuthorL = widgetAndLayoutForm(mainL, 's')
      self.userOrcid = self.addRowText('orcid','ORCID')
      self.userTitle = self.addRowText('title','Title')
      self.userFirst = self.addRowText('first','First name')
      self.userLast  = self.addRowText('last', 'Surname')
      self.userEmail = self.addRowText('email','Email address')
      #headline of organizations
      orgaW, orgaL = widgetAndLayout('H', None, spacing='s', top='l')
      self.orgaCB = QComboBox()
      self.orgaCB.addItems([i['organization'] for i in self.author['organizations']])
      orgaL.addStretch(1)
      orgaL.addWidget(self.orgaCB, stretch=2)
      IconButton('fa5s.plus',  self, [Command.ADD],    orgaL, 'Add organization')
      IconButton('fa5s.trash', self, [Command.DELETE], orgaL, 'Delete organization')
      self.tabAuthorL.addRow(orgaW)

      self.userRorid = self.addRowText('rorid','RORID')
      self.userOrg   = self.addRowText('organization','Organization')

    #final button box
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)

    #initialize
    self.orgaCB_previousIndex = 0
    self.lockSelfAuthor = False
    self.orgaCB.currentIndexChanged.connect(lambda: self.execute([Command.CHANGE]))#connect to slot only after all painting is done
    self.setStyleSheet(f"QLineEdit, QComboBox {{ {self.comm.palette.get('secondaryText', 'color')} }}")


  def addRowText(self, item:str, label:str) -> QLineEdit:
    """
    Add a row with a combo-box to the form

    Args:
      item (str): property name in configuration file
      label (str): label used in form

    Returns:
      QTextEdit: text-edit widget with content
    """
    self.textFields[item]  = QLineEdit()
    if item in {'organization','rorid'}:
      self.textFields[item].setText(self.author['organizations'][0][item] if self.author['organizations'] else '')
    else:
      self.textFields[item].setText(self.author[item])
    self.textFields[item].setAccessibleName(item)
    if item in {'organization', 'rorid','orcid'}:
      self.textFields[item] .editingFinished.connect(self.changedID)
    self.tabAuthorL.addRow(QLabel(label), self.textFields[item] )
    return self.textFields[item]


  def changedID(self) -> None:
    """
    Autofill based on orcid and rorid
    """
    sender = self.sender().accessibleName()                                       # type: ignore[attr-defined]
    if sender == 'rorid':
      if re.match(r'^\w{9}$', self.userRorid.text().strip() ) is not None:
        reply = requests.get(f'https://api.ror.org/organizations/{self.userRorid.text().strip()}', timeout=10)
        self.userOrg.setText(reply.json()['name'])
        self.orgaCB.setItemText(self.orgaCB.currentIndex(), reply.json()['name'])
    elif sender == 'orcid':
      if re.match(r'^\w{4}-\w{4}-\w{4}-\w{4}$', self.userOrcid.text().strip() ) is not None:
        reply = requests.get(f'https://pub.orcid.org/v3.0/{self.userOrcid.text().strip()}', timeout=10)
        text = reply.content.decode()
        first = text.split('<personal-details:given-names>')[1].split('</personal-details:given-names>')[0]
        last = text.split('<personal-details:family-name>')[1].split('</personal-details:family-name>')[0]
        self.userFirst.setText(first)
        self.userLast.setText(last)
    elif sender == 'organization':
      self.orgaCB.setItemText(self.orgaCB.currentIndex(), self.userOrg.text())
    else:
      logging.error('Did not understand sender: %s',sender)
    return


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    else:
      self.author['first'] = self.userFirst.text().strip()
      self.author['last']  = self.userLast.text().strip()
      self.author['title'] = self.userTitle.text().strip()
      self.author['email'] = self.userEmail.text().strip()
      self.author['orcid'] = self.userOrcid.text().strip()
      j = self.orgaCB.currentIndex()
      if j>-1:
        self.author['organizations'][j]['organization'] = self.userOrg.text().strip()
        self.author['organizations'][j]['rorid']        = self.userRorid.text().strip()
      self.comm.backend.configuration['authors'][0] = self.author
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.backend.configuration,indent=2))
    self.callbackFinished(False)
    return


  def execute(self, command:list[Any]) -> None:
    """
    Save changes to hard-disk
    """
    if command[0] is Command.ADD:
      self.orgaCB.addItem('- new -')
      if len(self.author['organizations'])<self.orgaCB.count():
        self.author['organizations'].append({'rorid':'', 'organization':''})
      self.orgaCB.setCurrentText('- new -')
      self.userRorid.setEnabled(True)
      self.userRorid.setText('')
      self.userOrg.setEnabled(True)
      self.userOrg.setText('')
    elif command[0] is Command.DELETE:
      k = self.orgaCB.currentIndex()
      if k>-1:
        self.author['organizations'].pop(k)
        self.lockSelfAuthor = True
        self.orgaCB.removeItem(k)
      if self.orgaCB.currentIndex()==-1:
        self.userRorid.setEnabled(False)
        self.userOrg.setEnabled(False)
      self.lockSelfAuthor = False
    elif command[0] is Command.CHANGE and self.author['organizations']:
      j = self.orgaCB_previousIndex
      if j<len(self.author['organizations']) and not self.lockSelfAuthor:
        self.author['organizations'][j]['organization'] = self.userOrg.text().strip()
        self.author['organizations'][j]['rorid']        = self.userRorid.text().strip()
      k = self.orgaCB.currentIndex()
      self.userRorid.setText(self.author['organizations'][k]['rorid'])
      self.userOrg.setText(self.author['organizations'][k]['organization'])
    self.orgaCB_previousIndex = self.orgaCB.currentIndex()
    return


class Command(Enum):
  """ Commands used in this file """
  ADD    = 1
  DELETE = 2
  CHANGE = 3
