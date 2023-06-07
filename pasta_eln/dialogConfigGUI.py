""" Main class of config tab on GUI elements """
import json
from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QComboBox, QTextEdit  # pylint: disable=no-name-in-module
from PySide6.QtGui import QFontMetrics # pylint: disable=no-name-in-module
from .miscTools import restart
from .style import TextButton
from .backend import Backend

class ConfigurationGUI(QWidget):
  """ Main class of config tab on GUI elements """
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
      self.theme = self.addRowList('theme','Theme',
        ['dark_amber','dark_blue','dark_cyan','dark_lightgreen','dark_pink','dark_purple', 'dark_red',\
        'dark_teal','dark_yellow','light_amber','light_blue','light_cyan','light_cyan_500','light_lightgreen',\
        'light_pink','light_purple','light_red','light_teal','light_yellow','none'])
      self.wD = self.addRowList('imageSizeDetails','Image size in details view and form', ['300','400','500','600'])
      self.wP = self.addRowList('imageWidthProject','Image width in project view', ['200','250','300','350','400'])
      self.wS = self.addRowList('sidebarWidth','Sidebar width', ['220','280','340'])
      self.log = self.addRowList('loggingLevel','Logging level (more->less)', ['DEBUG','INFO','WARNING','ERROR'])
      self.tabAppearanceL.addRow('Save changes', TextButton('Save changes', self.saveData, None))


  def addRowList(self, item:str, label:str, itemList:list[str]) -> QComboBox:
    """
    Add a row with a combo-box to the form

    Args:
      item (str): property name in configuration file
      label (str): label used in form
      itemList (list(str)): items to choose from

    Returns:
      QCombobox: filled combobox
    """
    rightW = QComboBox()
    rightW.addItems(itemList)
    rightW.setCurrentText(str(self.backend.configuration['GUI'][item]))
    self.tabAppearanceL.addRow(QLabel(label), rightW)
    return rightW


  def addRowText(self, item:str, label:str) -> QTextEdit:
    """
    Add a row with a combo-box to the form

    Args:
      item (str): property name in configuration file
      label (str): label used in form

    Returns:
      QTextEdit: text-edit widget with content
    """
    rightW = QTextEdit()
    rightW.setFixedHeight(QFontMetrics(rightW.font()).lineSpacing()*5)
    rightW.setText(' '.join(self.backend.configuration['GUI'][item]))
    rightW.setAccessibleName(item)
    self.tabAppearanceL.addRow(QLabel(label), rightW)
    return rightW


  def saveData(self) -> None:
    """
    Save changes to hard-disk
    """
    self.backend.configuration['GUI']['theme'] = self.theme.currentText()
    self.backend.configuration['GUI']['imageSizeDetails'] = int(self.wD.currentText())
    self.backend.configuration['GUI']['imageWidthProject'] = int(self.wP.currentText())
    self.backend.configuration['GUI']['sidebarWidth'] =  int(self.wS.currentText())
    self.backend.configuration['GUI']['loggingLevel'] = self.log.currentText()
    with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.backend.configuration,indent=2))
    restart()
    return
