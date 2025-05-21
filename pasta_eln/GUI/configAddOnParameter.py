""" Main class of config tab on parameters (e.g. API keys) for add-ons """
import importlib
import json
from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QLabel,  # pylint: disable=no-name-in-module
                               QLineEdit)
from ..fixedStringsJson import CONF_FILE_NAME
from ..guiCommunicate import Communicate
from ..guiStyle import TextButton


class ConfigurationAddOnParameter(QDialog):
  """ Main class of config tab on authors
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
    mainL = QFormLayout(self)
    mainL.addRow(QLabel('Define parameters of add-ons, e.g. API keys'), QLabel(''))

    #GUI elements
    self.allLineEdits = []
    if hasattr(comm.backend, 'configuration'):
      addOns = comm.backend.configuration['projectGroups'][comm.backend.configurationProjectGroup]['addOns']
      for addOnType in addOns:
        if addOnType != 'extractors' and addOns[addOnType]:
          for name, _ in addOns[addOnType].items():
            module      = importlib.import_module(name)
            reqiredParam = module.reqParameter
            for param, tooltip in reqiredParam.items():
              label    = QLabel(f'{addOnType}/{name}.py: {param}')
              label.setToolTip(tooltip)
              lineEdit = QLineEdit()
              lineEdit.setToolTip(tooltip)
              mainL.addRow(label, lineEdit)
              self.allLineEdits.append((addOnType,name,param,lineEdit))

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    else:
      apiKeys = self.comm.backend.configuration.get('addOnParameter',{})
      for _, name, param, lineEdit in self.allLineEdits:
        if name not in apiKeys:
          apiKeys[name] = {}
        apiKeys[name][param] = lineEdit.text()
      self.comm.backend.configuration['addOnParameter'] = apiKeys
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.backend.configuration,indent=2))
      self.accept()
    self.callbackFinished(False)
    return
