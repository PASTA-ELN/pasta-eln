""" Main class of config tab on GUI elements """
import json
from pathlib import Path
from typing import Callable, Any
from PySide6.QtWidgets import QWidget, QFormLayout  # pylint: disable=no-name-in-module
from ..miscTools import restart
from ..guiStyle import TextButton, addRowList
from ..guiCommunicate import Communicate
from ..fixedStringsJson import configurationGUI

class ConfigurationGUI(QWidget):
  """ Main class of config tab on GUI elements """
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
      onDisk = self.comm.backend.configuration['GUI']
      self.mainL = QFormLayout(self)
      for items  in configurationGUI.values():
        for k,v in items.items():
          setattr(self, k,
                  addRowList(self.mainL, label=v[0], default=str(onDisk[k]), itemList=[str(i) for i in v[2]]))
      self.mainL.addRow('Save changes', TextButton('Save changes', self, [], None))


  def execute(self, _:list[Any]) -> None:
    """
    Save changes to hard-disk
    """
    for items in configurationGUI.values():
      for k in items.keys():
        try:
          self.comm.backend.configuration['GUI'][k] = int(getattr(self, k).currentText())
        except Exception:
          self.comm.backend.configuration['GUI'][k] = getattr(self, k).currentText()
    with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.comm.backend.configuration,indent=2))
    restart()
    return
