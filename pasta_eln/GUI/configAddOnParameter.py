""" Main class of config tab on parameters (e.g. API keys) for add-ons """
import importlib
import json
from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit)  # pylint: disable=no-name-in-module
from ..fixedStringsJson import CONF_FILE_NAME
from ..guiCommunicate import Communicate
from ..guiStyle import TextButton, Label, widgetAndLayout, showMessage


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
    mainL = QVBoxLayout(self)
    Label('Define Add-On parameters','h2',mainL)

    #GUI elements
    self.allLineEdits = []
    if hasattr(comm.backend, 'configuration'):
      addOns = comm.backend.configuration['projectGroups'][comm.backend.configurationProjectGroup]['addOns']
      for addOnType in addOns:                               # loop over add-on types
        if addOnType != 'extractors' and addOns[addOnType]:
          for name, _ in addOns[addOnType].items():          # loop over add-ons
            module      = importlib.import_module(name)
            requiredParam = module.reqParameter
            try:
              helpText = module.helpText
            except AttributeError:
              helpText = ''
            for param, tooltip in requiredParam.items():    # loop over parameters
              _, barL = widgetAndLayout('H', mainL, 'm', 's', 's', 's', 's')
              Label(f'{addOnType}/{name}.py: {param}', 'h4', barL, tooltip=tooltip)
              lineEdit = QLineEdit()
              barL.addWidget(lineEdit)
              if helpText:
                TextButton('?', self, command=[helpText], layout=barL)
              self.allLineEdits.append((addOnType,name,param,lineEdit))

    #final button box
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)


  def execute(self, command:list[str]) -> None:
    """
    Execute a command

    Args:
      command (list[str]): command to execute
    """
    showMessage(self, 'Help', command[0], 'Information')
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
