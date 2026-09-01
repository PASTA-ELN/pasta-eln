""" config tab on GUI / Appearance / Interface elements """
from collections.abc import Callable
from PySide6.QtWidgets import (QAbstractButton, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QLabel,
                               QLineEdit, QVBoxLayout)
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
    self.sectionGroups:dict[str, QGroupBox] = {}
    #GUI elements
    if hasattr(self.comm, 'configuration'):
      onDisk = self.comm.configuration['GUI']
      mainL  = QVBoxLayout(self)
      for label, items  in configurationGUI.items():                                                 # section
        groupbox = QGroupBox(label.capitalize())
        self.sectionGroups[label] = groupbox
        mainL.addWidget(groupbox)
        sectionL = QFormLayout(groupbox)
        for k,v in items.items():
          if k == 'scanExcludePatterns':
            widget = QLineEdit(', '.join(str(item) for item in self.comm.configuration['scanExcludePatterns']))
            sectionL.addRow(QLabel(v[0]), widget)
          else:
            widget = self.addRowList(sectionL, label=v[0], default=str(onDisk[k]), itemList=[str(i) for i in v[2]])
          setattr(self, k, widget)
        if label == 'appearance':
          self.detailsLevel.currentTextChanged.connect(self.updateAdvancedVisibility)# type: ignore[attr-defined]
      self.updateAdvancedVisibility(self.detailsLevel.currentText())# type: ignore[attr-defined]
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
            widget = getattr(self, k)
            if k == 'scanExcludePatterns':
              newList = [item.strip() for item in widget.text().split(',') if item.strip()]
              self.comm.configuration['scanExcludePatterns'] = newList
            else:
              self.comm.configuration['GUI'][k] = int(widget.currentText())
          except Exception:
            self.comm.configuration['GUI'][k] = getattr(self, k).currentText()
          if k == 'theme':
            self.comm.palette.setTheme(getattr(self, k).currentText())
      saveConfiguration(self.comm.configuration)
      self.accept()
      self.callbackFinished(True)
    return


  def updateAdvancedVisibility(self, detailsLevel:str) -> None:
    """Update visibility of the Advanced configuration group.

    Args:
      detailsLevel (str): Selected interface detail level.
    """
    self.sectionGroups['advanced'].setVisible(detailsLevel == 'Advanced')


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
