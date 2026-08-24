""" config tab on GUI / Appearance / Interface elements """
from collections.abc import Callable
from PySide6.QtWidgets import (QAbstractButton, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QLabel,
                               QVBoxLayout)
from ...configuration_file import saveConfiguration
from ...fixed_strings_json import configurationGUI
from ..gui_communicate import Communicate


class ConfigurationGUI(QDialog):
  """ config tab on GUI / Appearance / Interface elements """
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
    #TODO allow users to switch of info after extractor success


  def closeDialog(self, btn: QAbstractButton) -> None:
    """
    Save changes to hard-disk
    """
    if btn.text().endswith('Cancel'):
      self.comm.palette.setTheme()
      self.reject()
      self.callbackFinished(False)
    else:
      for items in configurationGUI.values():
        for k in items.keys():
          try:
            self.comm.configuration['GUI'][k] = int(getattr(self, k).currentText())
          except Exception:
            self.comm.configuration['GUI'][k] = getattr(self, k).currentText()
          if k == 'theme':
            self.comm.palette.setTheme(getattr(self, k).currentText())
      saveConfiguration(self.comm.configuration)
      self.accept()
      self.callbackFinished(True)
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
    labelWidget = QLabel(label)
    if label == 'Color style':
      widget.currentTextChanged.connect(lambda: self.comm.palette.setTheme(widget.currentText(), False))
    widget.addItems(itemList)
    widget.setCurrentText(default)
    layout.addRow(labelWidget, widget)
    return widget
