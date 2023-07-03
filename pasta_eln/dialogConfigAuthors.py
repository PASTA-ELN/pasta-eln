""" Main class of config tab on authors """
import json, requests, re
from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit  # pylint: disable=no-name-in-module
from PySide6.QtGui import QFontMetrics # pylint: disable=no-name-in-module
from .miscTools import restart
from .style import TextButton
from .backend import Backend

#TODO_P5 allow to add more users and each user can have multiple organizations

class ConfigurationAuthors(QWidget):
  """ Main class of config tab on authors """
  def __init__(self, backend:Backend, callbackFinished:Callable[[],None]):
    """
    Initialization

    Args:
      backend (Pasta): backend, not communication
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.backend = backend

    #GUI elements
    if hasattr(self.backend, 'configuration'):
      self.tabAppearanceL = QFormLayout(self)

      self.userOrcid = self.addRowText('orcid','ORCID')
      self.userTitle = self.addRowText('title','title')
      self.userFirst = self.addRowText('first','first name')
      self.userLast = self.addRowText('last','surname')
      self.userEmail = self.addRowText('email','email address')
      self.userRorid = self.addRowText('rorid','RORID')
      self.userOrganization = self.addRowText('organization','organization')
      self.tabAppearanceL.addRow('Save changes', TextButton('Save changes', self.saveData, None))


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
    if item in ['organization','rorid']:
      rightW.setText(self.backend.configuration['authors'][0]['organizations'][0][item])
    else:
      rightW.setText(self.backend.configuration['authors'][0][item])
    rightW.setAccessibleName(item)
    if item in ['rorid','orcid']:
      rightW.editingFinished.connect(self.changedID)
    self.tabAppearanceL.addRow(QLabel(label), rightW)
    return rightW


  def changedID(self) -> None:
    """
    Autofill based on orcid and rorid
    """
    sender = self.sender().accessibleName()
    if sender == 'rorid':
      if re.match(r'^\w{9}$', self.userRorid.text().strip() ) is not None:
        reply = requests.get('https://api.ror.org/organizations/'+self.userRorid.text().strip())
        self.userOrganization.setText(reply.json()['name'])
    elif sender == 'orcid':
      if re.match(r'^\w{4}-\w{4}-\w{4}-\w{4}$', self.userOrcid.text().strip() ) is not None:
        reply = requests.get('https://pub.orcid.org/v3.0/'+self.userOrcid.text().strip())
        text = reply.content.decode()
        first = text.split('<personal-details:given-names>')[1].split('</personal-details:given-names>')[0]
        last = text.split('<personal-details:family-name>')[1].split('</personal-details:family-name>')[0]
        self.userFirst.setText(first)
        self.userLast.setText(last)
    else:
      print('**ERROR: did not understand sender')
    return


  def saveData(self) -> None:
    """
    Save changes to hard-disk
    """
    self.backend.configuration['authors'][0]['first'] = self.userFirst.text().strip()
    self.backend.configuration['authors'][0]['last']  = self.userLast.text().strip()
    self.backend.configuration['authors'][0]['title'] = self.userTitle.text().strip()
    self.backend.configuration['authors'][0]['email'] = self.userEmail.text().strip()
    self.backend.configuration['authors'][0]['orcid'] = self.userOrcid.text().strip()
    self.backend.configuration['authors'][0]['organizations'][0]['organization'] = self.userOrganization.text().strip()
    self.backend.configuration['authors'][0]['organizations'][0]['rorid']        = self.userRorid.text().strip()
    with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.backend.configuration,indent=2))
    restart()
    return
