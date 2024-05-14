""" Creates a new instance of the EditMetadataSummaryDialog class. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: edit_metadata_summary_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any, Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QDialog

from pasta_eln.GUI.dataverse.edit_metadata_summary_dialog_base import Ui_EditMetadataSummaryDialog


class EditMetadataSummaryDialog(Ui_EditMetadataSummaryDialog):
  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the EditMetadataSummaryDialog class.

    Explanation:
        This method creates a new instance of the EditMetadataSummaryDialog class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the EditMetadataDialog class.

    """
    return super(EditMetadataSummaryDialog, cls).__new__(cls)

  def __init__(self, save_config_callback: Callable[[], None]) -> None:
    """
    Initializes the EditMetadataSummaryDialog instance.

    Args:
        save_config_callback (Callable[[], None]): A callable function to be connected to the 'accepted' signal of the buttonBox.

    Raises:
        TypeError: If save_config_callback is not callable.
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    if not callable(save_config_callback):
      raise TypeError("save_config_callback must be callable.")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.summaryTextEdit.setReadOnly(True)
    self.buttonBox.accepted.connect(save_config_callback)

  def show(self) -> None:
    """
    Displays the EditMetadataSummaryDialog instance.
    """
    self.instance.show()
