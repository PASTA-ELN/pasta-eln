""" Creates a new instance of the ConfigDialog class. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog

from pasta_eln.GUI.dataverse.config_dialog_base import Ui_ConfigDialogBase
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI


class ConfigDialog(Ui_ConfigDialogBase):
  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the ConfigDialog class.

    Explanation:
        This method creates a new instance of the ConfigDialog class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the ConfigDialog class.
    """
    return super(ConfigDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the ConfigDialog.

    Explanation:
        This method initializes the ConfigDialog class.

        It sets up the logger and creates an instance of QDialog.

    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance: QDialog = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.config_model = self.db_api.get_model(self.db_api.config_doc_id, ConfigModel)
    self.config_model.dataverse_login_info = self.config_model.dataverse_login_info or {}


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = ConfigDialog()
  ui.instance.show()
  sys.exit(app.exec())
