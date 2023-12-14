""" Main class of config tab on authors """
import json, re
from pathlib import Path
from typing import Callable, Any
import requests
from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit  # pylint: disable=no-name-in-module
from ..miscTools import restart
from ..guiStyle import TextButton
from ..guiCommunicate import Communicate


class ConfigurationAuthors(QWidget):
  """ Main class of config tab on authors """
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
      self.configuration = self.comm.backend.configuration
      self.tabAppearanceL = QFormLayout(self)
      self.userOrcid = self.addRowText('orcid','ORCID')
      self.userTitle = self.addRowText('title','Title')
      self.userFirst = self.addRowText('first','First name')
      self.userLast  = self.addRowText('last', 'Surname')
      self.userEmail = self.addRowText('email','Email address')
      self.userRorid = self.addRowText('rorid','RORID')
      self.userOrg   = self.addRowText('organization','Organization')
      self.tabAppearanceL.addRow('Save changes', TextButton('Save changes', self, [], None))


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
      rightW.setText(self.configuration['authors'][0]['organizations'][0][item])
    else:
      rightW.setText(self.configuration['authors'][0][item])
    rightW.setAccessibleName(item)
    if item in {'rorid','orcid'}:
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
        reply = requests.get(
            f'https://api.ror.org/organizations/{self.userRorid.text().strip()}')
        self.userOrg.setText(reply.json()['name'])
    elif sender == 'orcid':
      if re.match(r'^\w{4}-\w{4}-\w{4}-\w{4}$', self.userOrcid.text().strip() ) is not None:
        reply = requests.get(
            f'https://pub.orcid.org/v3.0/{self.userOrcid.text().strip()}')
        text = reply.content.decode()
        first = text.split('<personal-details:given-names>')[1].split('</personal-details:given-names>')[0]
        last = text.split('<personal-details:family-name>')[1].split('</personal-details:family-name>')[0]
        self.userFirst.setText(first)
        self.userLast.setText(last)
    else:
      print('**ERROR: did not understand sender')
    return


  def execute(self, _:list[Any]) -> None:
    """
    Save changes to hard-disk
    """
    self.configuration['authors'][0]['first'] = self.userFirst.text().strip()
    self.configuration['authors'][0]['last']  = self.userLast.text().strip()
    self.configuration['authors'][0]['title'] = self.userTitle.text().strip()
    self.configuration['authors'][0]['email'] = self.userEmail.text().strip()
    self.configuration['authors'][0]['orcid'] = self.userOrcid.text().strip()
    self.configuration['authors'][0]['organizations'][0]['organization'] = self.userOrg.text().strip()
    self.configuration['authors'][0]['organizations'][0]['rorid']        = self.userRorid.text().strip()
    with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.configuration,indent=2))
    restart()
    return
