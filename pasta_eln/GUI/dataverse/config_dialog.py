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
import webbrowser
from asyncio import get_event_loop
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QMessageBox

from pasta_eln.GUI.dataverse.config_dialog_base import Ui_ConfigDialogBase
from pasta_eln.dataverse.client import DataverseClient
from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.utils import check_login_credentials, log_and_create_error


class ConfigDialog(Ui_ConfigDialogBase):
  """
  Creates a new instance of the ConfigDialog class.

  Explanation:
  This class represents a configuration dialog.
  It initializes the dialog, sets up the logger,
  and handles various UI elements and actions related to the configuration.

  __new__(cls, *_: Any, **__: Any) -> Any

  Creates a new instance of the ConfigDialog class.

  Args:
      *_: Variable length argument list.
      **__: Arbitrary keyword arguments.

  Returns:
      Any: The new instance of the ConfigDialog class.

  __init__(self) -> None

  Initializes the ConfigDialog.

  Explanation:
  This method initializes the ConfigDialog class.
  It sets up the logger, creates an instance of QDialog,
  and performs various initialization tasks related to the configuration.

  Usage:
    config_dialog = ConfigDialog()
    config_dialog.show()
  """

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
    self.config_model = self.db_api.get_config_model() or ConfigModel()
    if self.config_model.id is None:
      raise log_and_create_error(self.logger, ConfigError, "Config not found, Corrupt installation!")
    self.config_model.dataverse_login_info = self.config_model.dataverse_login_info or {}
    self.dataverseServerLineEdit.setValidator(QRegularExpressionValidator(QRegularExpression("\\S*")))

    # Initialize UI elements
    self.dataverseServerLineEdit.setText(self.config_model.dataverse_login_info.get("server_url", ""))
    self.apiTokenLineEdit.setText(self.config_model.dataverse_login_info.get("api_token", ""))
    self.dataverseListComboBox.setCurrentText(self.config_model.dataverse_login_info.get("dataverse_id", ""))
    self.dataverseLineEdit.setText(self.config_model.dataverse_login_info.get("dataverse_id", ""))

    # Setup slots
    self.dataverseServerLineEdit.textChanged[str].connect(self.update_dataverse_server)
    self.apiTokenLineEdit.textChanged[str].connect(self.update_api_token)
    self.dataverseLineEdit.textChanged[str].connect(self.update_dataverse_id)
    self.dataverseListComboBox.currentTextChanged.connect(self.update_dataverse_line_edit)
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_config)
    self.dataverseVerifyLoadPushButton.clicked.connect(self.verify_and_load_dataverse_list)
    self.apiTokenHelpPushButton.clicked.connect(
      lambda: webbrowser.open("https://data.fz-juelich.de/guide/api/auth.html"))

  def update_dataverse_server(self, new_value: str) -> None:
    """
    Updates the server URL in the dataverse login info.

    Explanation:
        This method updates the server URL in the dataverse login info with the provided new value.

    Args:
        new_value (str): The new server URL.
    """
    self.config_model.dataverse_login_info["server_url"] = new_value  # type: ignore[index]

  def update_api_token(self, new_value: str) -> None:
    """
    Updates the API token in the dataverse login info.

    Explanation:
        This method updates the API token in the dataverse login info with the provided new value.

    Args:
        new_value (str): The new API token.
    """
    self.config_model.dataverse_login_info["api_token"] = new_value  # type: ignore[index]

  def update_dataverse_line_edit(self) -> None:
    """
    Updates the dataverse line edit with the provided dataverse ID.

    Args:
        self: The instance of the class.
    """
    dataverse_id = self.dataverseListComboBox.currentData(QtCore.Qt.ItemDataRole.UserRole)
    self.dataverseLineEdit.setText(dataverse_id)

  def update_dataverse_id(self, new_value: str) -> None:
    """
    Updates the dataverse ID in the dataverse login info.

    Explanation:
        This method updates the dataverse ID in the dataverse login info with the provided new value.

    Args:
        new_value (str): The new dataverse ID.
    """
    self.config_model.dataverse_login_info["dataverse_id"] = new_value  # type: ignore[index]

  def save_config(self) -> None:
    """
    Saves the configuration in database.

    Explanation:
        This method saves the configuration by encrypting the API token.
    """
    self.logger.info("Saving config..")
    self.db_api.save_config_model(self.config_model)

  def verify_server_url_and_api_token(self) -> bool:
    """
    Verifies the server URL and API token.

    Explanation:
        This method verifies the server URL and API token by checking if they are both provided.
        If they are not provided, it shows a warning message.

    Returns:
        bool: True if the server URL and API token are valid, False otherwise.
    """
    self.logger.info("Verifying server URL and API token..")
    server_url = self.dataverseServerLineEdit.text()
    api_token = self.apiTokenLineEdit.text()
    if not (server_url and api_token):
      QMessageBox.warning(self.instance, "Error", "Please enter both server URL and API token")
      return False
    success, message = check_login_credentials(self.logger, api_token, server_url)
    if success:
      QMessageBox.information(self.instance, "Credentials Valid", message)
      return True
    else:
      QMessageBox.warning(self.instance, "Credentials Invalid", message)
      return False

  def verify_and_load_dataverse_list(self) -> None:
    """
    Loads the dataverse list.

    Explanation:
        This method loads the dataverse list by making a request to the server and populating the dataverse list combo box with the retrieved dataverses.
    """
    self.logger.info("Loading dataverse list..")
    saved_id = self.config_model.dataverse_login_info.get("dataverse_id", "")  # type: ignore[union-attr]
    self.dataverseListComboBox.clear()
    server_url = self.dataverseServerLineEdit.text()
    api_token = self.apiTokenLineEdit.text()
    if not self.verify_server_url_and_api_token():
      return
    if not (server_url and api_token):
      QMessageBox.warning(self.instance, "Error", "Please enter both server URL and API token")
      return
    dataverse_client = DataverseClient(server_url, api_token)
    event_loop = get_event_loop()
    if dataverses := event_loop.run_until_complete(dataverse_client.get_dataverse_list()):
      if isinstance(dataverses, list) and isinstance(dataverses[0], dict):
        current_text = ""
        for dataverse in dataverses:
          dv_title = dataverse.get('title', None)
          dv_id = dataverse.get('id', None)
          if dv_title and dv_id:
            self.dataverseListComboBox.addItem(dv_title, userData=dataverse['id'])
            if saved_id == dv_id:
              current_text = dv_title
        self.dataverseListComboBox.setCurrentText(current_text)
      else:
        self.logger.error("Failed to load dataverse list, error: %s", dataverses)
        QMessageBox.warning(self.instance, "Error", "Failed to load dataverse list")

  def show(self) -> None:
    """
    Shows the instance.

    Explanation:
        This method shows the instance by calling its show method.
    """
    self.instance.show()
    # Load dataverse list
    if self.dataverseServerLineEdit.text() and self.apiTokenLineEdit.text():
      self.dataverseVerifyLoadPushButton.click()


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = ConfigDialog()
  ui.show()
  sys.exit(app.exec())
