""" Main class of config tab on GUI elements """
import json
from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QLabel, QVBoxLayout
from ...fixedStringsJson import CONF_FILE_NAME, configurationGUI
from ..guiCommunicate import Communicate
from ..guiStyle import TextButton


class ConfigurationGUI(QDialog):
  """ Main class of config tab on GUI elements """
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
    #GUI elements
    if hasattr(self.comm, 'configuration'):
      onDisk = self.comm.configuration['GUI']
      mainL  = QVBoxLayout(self)
      for label, items  in configurationGUI.items():                                                 # section
        groupbox = QGroupBox(label.capitalize())
        mainL.addWidget(groupbox)
        sectionL = QFormLayout(groupbox)
        for k,v in items.items():
          setattr(self, k, self.addRowList(sectionL, label=v[0], default=str(onDisk[k]), itemList=[str(i) for i in v[2]]))
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    self.setStyleSheet(f"QLineEdit, QComboBox {{ {self.comm.palette.get('secondaryText', 'color')} }}")


  def closeDialog(self, btn:TextButton) -> None:
    """
    Save changes to hard-disk
    """
    if btn.text().endswith('Cancel'):
      self.reject()
      self.callbackFinished(False)
    else:
      for items in configurationGUI.values():
        for k in items.keys():
          try:
            self.comm.configuration['GUI'][k] = int(getattr(self, k).currentText())
          except Exception:
            self.comm.configuration['GUI'][k] = getattr(self, k).currentText()
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.configuration,indent=2))
    return


  def addRowList(self, layout:QFormLayout, label:str, default:str, itemList:list[str]) -> QComboBox:
    """
    Add a row with a combo-box to the form

    Args:
      layout (QLayout): layout to add row to
      label (str): label used in form
      default (str): default value
      itemList (list(str)): items to choose from

    Returns:
      QCombobox: filled combobox
    """
    widget = QComboBox()                                                     # pylint: disable=qt-local-widget
    if label == 'Color style':
      widget.setToolTip('Restart of PASTA-ELN required.')
      label += ' *'
    widget.addItems(itemList)
    widget.setCurrentText(default)
    layout.addRow(QLabel(label), widget)
    return widget
