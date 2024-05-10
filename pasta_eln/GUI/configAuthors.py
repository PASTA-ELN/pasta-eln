""" Main class of config tab on authors """
import json, re
from enum import Enum
from pathlib import Path
from typing import Callable, Any
import requests
from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QComboBox  # pylint: disable=no-name-in-module
from ..miscTools import restart
from ..guiStyle import TextButton, IconButton, widgetAndLayout
from ..guiCommunicate import Communicate


class ConfigurationAuthors(QWidget):
  """ Main class of config tab on authors

  FOR NOW: only one author (one self) can be added to align with GDPR
  """
  def __init__(self, comm:Communicate, callbackFinished:Callable[[],None]):
    """
    Initialization

    Args:
      comm (Communicate): communication
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm = comm

    #GUI elements
    if hasattr(self.comm.backend, 'configuration'):
      self.author = self.comm.backend.configuration['authors'][0]
      self.tabAuthorL = QFormLayout(self)
      self.userOrcid = self.addRowText('orcid','ORCID')
      self.userTitle = self.addRowText('title','Title')
      self.userFirst = self.addRowText('first','First name')
      self.userLast  = self.addRowText('last', 'Surname')
      self.userEmail = self.addRowText('email','Email address')
      orgaW, orgaL = widgetAndLayout('H', None, spacing='s', top='l')
      self.orgaCB = QComboBox()
      self.orgaCB.addItems([i['organization'] for i in self.author['organizations']])
      orgaL.addStretch(1)
      orgaL.addWidget(self.orgaCB)
      IconButton('fa5s.plus-circle', self, [Command.ADD], orgaL, 'Add organization')
      IconButton('fa5s.minus-circle', self, [Command.DELETE], orgaL, 'Delete organization')
      self.tabAuthorL.addRow(orgaW)
      self.userRorid = self.addRowText('rorid','RORID')
      self.userOrg   = self.addRowText('organization','Organization')
      buttonBarW, buttonBarL = widgetAndLayout('H', None, top='l')
      buttonBarL.addStretch(1)
      TextButton('Save changes', self, [Command.SAVE], buttonBarL)
      self.tabAuthorL.addRow(buttonBarW)
      self.orgaCB_lastIndex = 0
      self.orgaCB.currentIndexChanged.connect(lambda: self.execute([Command.CHANGE])) #connect to slot only after all painting is done


  def addRowText(self, item:str, label:str) -> QLineEdit:
    """
    Add a row with a combo-box to the form

    Args:
      item (str): property name in configuration file
      label (str): label used in form

    Returns:
      QTextEdit: text-edit widget with content
    """
    rightW = QLineEdit()
    if item in {'organization','rorid'}:
      rightW.setText(self.author['organizations'][0][item])
    else:
      rightW.setText(self.author[item])
    rightW.setAccessibleName(item)
    if item in {'rorid','orcid'}:
      rightW.editingFinished.connect(self.changedID)
    self.tabAuthorL.addRow(QLabel(label), rightW)
    return rightW


  def changedID(self) -> None:
    """
    Autofill based on orcid and rorid
    """
    sender = self.sender().accessibleName()
    if sender == 'rorid':
      if re.match(r'^\w{9}$', self.userRorid.text().strip() ) is not None:
        reply = requests.get(f'https://api.ror.org/organizations/{self.userRorid.text().strip()}', timeout=10)
        self.userOrg.setText(reply.json()['name'])
    elif sender == 'orcid':
      if re.match(r'^\w{4}-\w{4}-\w{4}-\w{4}$', self.userOrcid.text().strip() ) is not None:
        reply = requests.get(f'https://pub.orcid.org/v3.0/{self.userOrcid.text().strip()}', timeout=10)
        text = reply.content.decode()
        first = text.split('<personal-details:given-names>')[1].split('</personal-details:given-names>')[0]
        last = text.split('<personal-details:family-name>')[1].split('</personal-details:family-name>')[0]
        self.userFirst.setText(first)
        self.userLast.setText(last)
    else:
      print('**ERROR: did not understand sender')
    return


  def execute(self, command:list[Any]) -> None:
    """
    Save changes to hard-disk
    """
    if command[0] is Command.SAVE:
      self.author['first'] = self.userFirst.text().strip()
      self.author['last']  = self.userLast.text().strip()
      self.author['title'] = self.userTitle.text().strip()
      self.author['email'] = self.userEmail.text().strip()
      self.author['orcid'] = self.userOrcid.text().strip()
      j = self.orgaCB_lastIndex
      self.author['organizations'][j]['organization'] = self.userOrg.text().strip()
      self.author['organizations'][j]['rorid']        = self.userRorid.text().strip()
      with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.configuration,indent=2))
      restart()
    elif command[0] is Command.ADD:
      self.author['organizations'].append({'rorid':'', 'organization':''})
      self.orgaCB.addItem('- new -')
      self.orgaCB.setCurrentText('- new -')
    elif command[0] is Command.DELETE:
      k = self.orgaCB.currentIndex()
      j = 0 if k>0 else -1
      self.orgaCB.setCurrentIndex(j)
      self.author['organizations'].pop(k)
      self.orgaCB.removeItem(k)
    elif command[0] is Command.CHANGE:
      j = self.orgaCB_lastIndex
      self.author['organizations'][j]['organization'] = self.userOrg.text().strip()
      self.author['organizations'][j]['rorid']        = self.userRorid.text().strip()
      k = self.orgaCB.currentIndex()
      self.userRorid.setText(self.author['organizations'][k]['rorid'])
      self.userOrg.setText(self.author['organizations'][k]['organization'])
      self.orgaCB_lastIndex = k
    return


class Command(Enum):
  """ Commands used in this file """
  SAVE   = 1
  ADD    = 2
  DELETE = 3
  CHANGE = 4
