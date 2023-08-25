""" Main class of config tab on GUI elements """
import json
from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import QWidget, QFormLayout, QLabel, QComboBox, QTextEdit  # pylint: disable=no-name-in-module
from PySide6.QtGui import QFontMetrics # pylint: disable=no-name-in-module
from ..miscTools import restart
from ..guiStyle import TextButton
from ..backend import Backend
from ..fixedStringsJson import configurationGUI

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
      for items  in configurationGUI.values():
        for k,v in items.items():
          setattr(self, k, self.addRowList(v[0], str(v[1]), [str(i) for i in v[2]]))
      self.tabAppearanceL.addRow('Save changes', TextButton('Save changes', self.saveData, None))


  def addRowList(self, label:str, default:str, itemList:list[str]) -> QComboBox:
    """
    Add a row with a combo-box to the form

    Args:
      label (str): label used in form
      default (str): default value
      itemList (list(str)): items to choose from

    Returns:
      QCombobox: filled combobox
    """
    widget = QComboBox()
    widget.addItems(itemList)
    widget.setCurrentText(default)
    self.tabAppearanceL.addRow(QLabel(label), widget)
    return widget


  def addRowText(self, item:str, label:str) -> QTextEdit:
    """
    Add a row with a combo-box to the form

    Args:
      item (str): property name in configuration file
      label (str): label used in form

    Returns:
      QTextEdit: text-edit widget with content
    """
    widget = QTextEdit()
    widget.setFixedHeight(QFontMetrics(widget.font()).lineSpacing()*5)
    widget.setText(' '.join(self.backend.configuration['GUI'][item]))
    widget.setAccessibleName(item)
    self.tabAppearanceL.addRow(QLabel(label), widget)
    return widget


  def saveData(self) -> None:
    """
    Save changes to hard-disk
    """
    for items in configurationGUI.values():
      for k in items.keys():
        try:
          self.backend.configuration['GUI'][k] = int(getattr(self, k).currentText())
        except Exception:
          self.backend.configuration['GUI'][k] = getattr(self, k).currentText()
    with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.backend.configuration,indent=2))
    restart()
    return
