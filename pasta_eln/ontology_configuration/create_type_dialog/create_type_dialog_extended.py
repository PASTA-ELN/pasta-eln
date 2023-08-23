#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: create_type_dialog_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from collections.abc import Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog

from pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog import Ui_CreateTypeDialog


class CreateTypeDialog(Ui_CreateTypeDialog):

  def __init__(self,
               accepted_callback: Callable,
               rejected_callback: Callable):
    """
    Instantiates the create type dialog
    Args:
      accepted_callback (Callable): Accepted button parent callback.
      rejected_callback (Callable): Rejected button parent callback.
    """
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
    self.next_struct_level = None
    self.instance = QDialog()
    ui = super()
    ui.setupUi(self.instance)
    self.buttonBox.accepted.connect(accepted_callback)
    self.buttonBox.rejected.connect(rejected_callback)
    self.structuralLevelCheckBox.stateChanged.connect(self.structural_level_checkbox_callback)

  def structural_level_checkbox_callback(self):
    """
    Callback invoked when the state changes for structuralLevelCheckBox

    Returns:
        None
    """
    if self.structuralLevelCheckBox.isChecked():
      self.titleLineEdit.setText(self.next_struct_level)
      self.titleLineEdit.setDisabled(True)
    else:
      self.titleLineEdit.clear()
      self.titleLineEdit.setDisabled(False)

  def show(self):
    """
    Displays the dialog

    Returns: None

    """
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.instance.show()

  def clear_ui(self):
    """
    Clear the Dialog UI

    Returns:
      None

    """
    self.labelLineEdit.clear()
    self.titleLineEdit.clear()
    self.structuralLevelCheckBox.setChecked(False)

  def set_structural_level_title(self,
                                 structural_level: str):
    """
    Set the next possible structural type level title

    Args:
      structural_level (str): Passed in structural level of the format (x0, x1, x2 ...)

    Returns:
      None

    """
    self.logger.info(f"Next structural level set: {structural_level}...")
    self.next_struct_level = structural_level
