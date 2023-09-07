""" CreateTypeDialog used for the create type dialog """
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
from typing import Any

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog

from pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog import Ui_CreateTypeDialog


class CreateTypeDialog(Ui_CreateTypeDialog):
  """
  Abstracted dialog for the create type
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the create type dialog
    """
    return super(CreateTypeDialog, cls).__new__(cls)

  def __init__(self,
               accepted_callback: Callable[[], None],
               rejected_callback: Callable[[], None]) -> None:
    """
    Initializes the create type dialog
    Args:
      accepted_callback (Callable): Accepted button parent callback.
      rejected_callback (Callable): Rejected button parent callback.
    """
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
    self.next_struct_level: str | None = ""
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.setup_slots(accepted_callback, rejected_callback)

  def setup_slots(self,
                  accepted_callback: Callable[[], None],
                  rejected_callback: Callable[[], None]) -> None:
    """
    Sets up the slots for the dialog
    Args:
      accepted_callback (Callable): Accepted button parent callback.
      rejected_callback (Callable): Rejected button parent callback.

    Returns: None

    """
    self.buttonBox.accepted.connect(accepted_callback)
    self.buttonBox.rejected.connect(rejected_callback)
    self.structuralLevelCheckBox.stateChanged.connect(self.structural_level_checkbox_callback)

  def structural_level_checkbox_callback(self) -> None:
    """
    Callback invoked when the state changes for structuralLevelCheckBox

    Returns: Nothing
    """
    if self.structuralLevelCheckBox.isChecked():
      self.titleLineEdit.setText(self.next_struct_level)
      self.titleLineEdit.setDisabled(True)
    else:
      self.titleLineEdit.clear()
      self.titleLineEdit.setDisabled(False)

  def show(self) -> None:
    """
    Displays the dialog

    Returns: None

    """
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.instance.show()

  def clear_ui(self) -> None:
    """
    Clear the Dialog UI

    Returns: Nothing

    """
    self.labelLineEdit.clear()
    self.titleLineEdit.clear()
    self.structuralLevelCheckBox.setChecked(False)

  def set_structural_level_title(self,
                                 structural_level: str | None) -> None:
    """
    Set the next possible structural type level title

    Args:
      structural_level (str): Passed in structural level of the format (x0, x1, x2 ...)

    Returns: Nothing

    """
    self.logger.info("Next structural level set: {%s}...", structural_level)
    self.next_struct_level = structural_level
