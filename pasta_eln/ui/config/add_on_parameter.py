""" Main class of config tab on parameters (e.g. API keys) for add-ons """
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtWidgets import QApplication, QDialog, QGroupBox, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget
from ...configuration_file import saveConfiguration
from ...misc_tools import loadNamedModule
from ..gui_communicate import Communicate
from ..gui_style import SPACE, Button, ButtonStyle, Label, shortcut
from ..message_dialog import showMessage


class ConfigurationAddOnParameter(QDialog):
  """ Main class of config tab on authors
  """
  def __init__(self, comm:Communicate, callbackFinished:Callable[[bool],None]):
    """
    Initialization

    Args:
      comm (Communicate): Shared communication object.
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm = comm
    self.callbackFinished = callbackFinished
    mainL = QVBoxLayout(self)
    mainL.setContentsMargins(SPACE.S, 0, 0, 0)
    Label('Define Add-On parameters','h2',mainL)
    mainL.addSpacing(SPACE.M)

    #GUI elements
    self.allLineEdits:list[tuple[str,str,str,QLineEdit]] = []
    self.allGroupBoxes = []
    if hasattr(comm, 'configuration'):
      addOns = comm.configuration['projectGroups'][comm.projectGroup]['addOns']
      for addOnType in sorted(addOns, key=str.casefold):                              # loop over add-on types
        if addOnType != 'extractors' and addOns[addOnType]:
          for name in sorted(addOns[addOnType], key=str.casefold):                         # loop over add-ons
            groupbox = QGroupBox(name.capitalize())
            mainL.addWidget(groupbox)
            groupLayout = QVBoxLayout(groupbox)
            self.allGroupBoxes.append((addOnType, name, groupbox, groupLayout))

    #final button box
    mainL.addStretch(1)
    footerW = QWidget()
    buttonLineL = QHBoxLayout(footerW)
    buttonLineL.setContentsMargins(0, SPACE.S, 0, 0)
    buttonLineL.setSpacing(SPACE.M)
    mainL.addWidget(footerW)
    tooltip = 'Scan files to find parameters. Takes time.'
    self.scanBtn = Button('Scan', self, [Command.SCAN], buttonLineL, tooltip=tooltip)
    buttonLineL.addStretch(1)
    self.cancelBtn = Button('Cancel', self, [Command.CANCEL], buttonLineL, tooltip='Discard changes')
    self.saveBtn   = Button('Save', self, [Command.SAVE], buttonLineL, tooltip='Save changes',
                          style=ButtonStyle.HIGHLIGHTED)
    self.saveShortcut = shortcut('Ctrl+Return', self, lambda: self.execute([Command.SAVE]))


  def execute(self, command:list[Any]) -> None:
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
      saveConfiguration(self.comm.configuration)
      self.accept()
      self.callbackFinished(False)
    elif command[0] is Command.SCAN:
      self.allLineEdits = []
      for addonType, name, groupbox, groupLayout in self.allGroupBoxes:
        QApplication.processEvents()                                                        # Force GUI update
        try:
          module        = loadNamedModule(Path(self.comm.addOnPath), name)
          requiredParam = module.reqParameter
          try:
            helpText = module.helpText
          except AttributeError:
            helpText = ''
          if not requiredParam:
            groupbox.hide()
          for param, tooltip in requiredParam.items():                                  # loop over parameters
            barW = QWidget()
            barL = QHBoxLayout(barW)
            barL.setContentsMargins(SPACE.S, SPACE.S, SPACE.S, SPACE.S)
            barL.setSpacing(SPACE.M)
            groupLayout.addWidget(barW)
            Label(f'{name}.py: {param}', 'h4', barL, tooltip=tooltip)
            lineEdit = QLineEdit()                                           # pylint: disable=qt-local-widget
            lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            barL.addWidget(lineEdit)
            if helpText:
              Button('?', self, command=[helpText], layout=barL)
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
