""" Main class of config tab on GUI elements """
import json
from pathlib import Path
from typing import Any
from PySide6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QGroupBox, QDialogButtonBox  # pylint: disable=no-name-in-module
from ..miscTools import restart
from ..guiStyle import TextButton, addRowList
from ..guiCommunicate import Communicate
from ..fixedStringsJson import configurationGUI

class ConfigurationGUI(QWidget):
  """ Main class of config tab on GUI elements """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication
    """
    super().__init__()
    self.comm = comm
    #GUI elements
    if hasattr(self.comm.backend, 'configuration'):
      onDisk = self.comm.backend.configuration['GUI']
      mainL  = QVBoxLayout(self)
      for label, items  in configurationGUI.items():
        groupbox = QGroupBox(label.capitalize())
        mainL.addWidget(groupbox)
        sectionL = QFormLayout(groupbox)
        for k,v in items.items():
          setattr(self, k,
                  addRowList(sectionL, label=v[0], default=str(onDisk[k]), itemList=[str(i) for i in v[2]]))
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)


  def closeDialog(self, btn:TextButton) -> None:
    """
    Save changes to hard-disk
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    else:
      for items in configurationGUI.values():
        for k in items.keys():
          try:
            self.comm.backend.configuration['GUI'][k] = int(getattr(self, k).currentText())
          except Exception:
            self.comm.backend.configuration['GUI'][k] = getattr(self, k).currentText()
      with open(Path.home()/'.pastaELN_v3.json', 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.backend.configuration,indent=2))
      restart()
    return
