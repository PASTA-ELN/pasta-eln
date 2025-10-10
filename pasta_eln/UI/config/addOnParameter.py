""" Main class of config tab on parameters (e.g. API keys) for add-ons """
import importlib
import json
from enum import Enum
from pathlib import Path
from typing import Callable
from PySide6.QtWidgets import QApplication, QDialog, QGroupBox, QLineEdit, QVBoxLayout
from ...fixedStringsJson import CONF_FILE_NAME
from ..guiCommunicate import Communicate
from ..guiStyle import Label, TextButton, widgetAndLayout
from ..messageDialog import showMessage


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
    self.allLineEdits:list[tuple[str,str,str,QLineEdit]] = []
    self.allGroupBoxes = []
    if hasattr(comm, 'configuration'):
      addOns = comm.configuration['projectGroups'][comm.projectGroup]['addOns']
      for addOnType in addOns:                                                        # loop over add-on types
        if addOnType != 'extractors' and addOns[addOnType]:
          for name, _ in addOns[addOnType].items():                                        # loop over add-ons
            groupbox = QGroupBox(name.capitalize())
            mainL.addWidget(groupbox)
            groupLayout = QVBoxLayout(groupbox)
            self.allGroupBoxes.append((addOnType, name, groupbox, groupLayout))

    #final button box
    mainL.addStretch(1)
    _, buttonLineL = widgetAndLayout('H', mainL, 'm')
    tooltip = 'Scan files to find parameters. Takes time.'
    self.scanBtn = TextButton('Scan',                self, [Command.SCAN],   buttonLineL, tooltip)
    self.scanBtn.setStyleSheet('background: orange; color: black;')
    buttonLineL.addStretch(1)
    self.saveBtn = TextButton('Save', self, [Command.SAVE],   buttonLineL, 'Save changes')
    self.saveBtn.setShortcut('Ctrl+Return')
    self.cancelBtn = TextButton('Cancel',              self, [Command.CANCEL], buttonLineL, 'Discard changes')


  def execute(self, command:list[str]) -> None:
    """
    Execute a command

    Args:
      command (list[str]): command to execute
    """
    if command[0] is Command.CANCEL:
      self.reject()
      self.callbackFinished(False)
    elif command[0] is Command.SAVE:
      apiKeys = self.comm.configuration.get('addOnParameter',{})
      for _, name, param, lineEdit in self.allLineEdits:
        if name not in apiKeys:
          apiKeys[name] = {}
        apiKeys[name][param] = lineEdit.text()
      self.comm.configuration['addOnParameter'] = apiKeys
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.configuration,indent=2))
      self.accept()
      self.callbackFinished(False)
    elif command[0] is Command.SCAN:
      self.allLineEdits = []
      for addonType, name, groupbox, groupLayout in self.allGroupBoxes:
        QApplication.processEvents()                                                        # Force GUI update
        try:
          module      = importlib.import_module(name)           # ISSUE: slow since imports all dependencies,...
          requiredParam = module.reqParameter
          try:
            helpText = module.helpText
          except AttributeError:
            helpText = ''
          if not requiredParam:
            groupbox.hide()
          for param, tooltip in requiredParam.items():                                  # loop over parameters
            _, barL = widgetAndLayout('H', groupLayout, 'm', 's', 's', 's', 's')
            Label(f'{name}.py: {param}', 'h4', barL, tooltip=tooltip)
            lineEdit = QLineEdit()                                           # pylint: disable=qt-local-widget
            barL.addWidget(lineEdit)
            if helpText:
              TextButton('?', self, command=[helpText], layout=barL)
            self.allLineEdits.append((addonType,name,param,lineEdit))
        except Exception:
          Label(f'{name}.py: Error occurred; please check add-on.', 'h4', groupLayout)
    else:
      showMessage(self, 'Help', command[0], 'Information')
    return


class Command(Enum):
  """ Commands used in this file """
  SCAN        = 1
  SAVE        = 2
  CANCEL      = 3
