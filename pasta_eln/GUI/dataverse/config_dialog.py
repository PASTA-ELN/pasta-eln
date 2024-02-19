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
from PySide6.QtWidgets import QDialog, QMessageBox

from pasta_eln.GUI.dataverse.config_dialog_base import Ui_ConfigDialogBase
from pasta_eln.dataverse.client import DataverseClient
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.utils import check_login_credentials, decrypt_data, encrypt_data, get_encrypt_key


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
    self.encrypt_key: bytes | None = None
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance: QDialog = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.config_model = self.db_api.get_model(self.db_api.config_doc_id, ConfigModel)
    self.config_model.dataverse_login_info = self.config_model.dataverse_login_info or {}
    self.decrypt_api_token()

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
    self.apiTokenVerifyPushButton.clicked.connect(self.verify_server_url_and_api_token)
    self.dataverseLoadPushButton.clicked.connect(self.load_dataverse_list)
    self.apiTokenHelpPushButton.clicked.connect(
      lambda: webbrowser.open("https://guides.dataverse.org/en/latest/api/auth.html"))

    # Load dataverse list
    if self.dataverseServerLineEdit.text() and self.apiTokenLineEdit.text():
      self.dataverseLoadPushButton.click()

  def decrypt_api_token(self):
    """
    Decrypts the API token using the encryption key.

    Explanation:
        This method decrypts the API token using the encryption key.
        If the encryption key is not found, it removes the API token and dataverse ID from the configuration.

    Args:
        self: The instance of the class.

    Returns:
        None
    """
    key_exists, self.encrypt_key = get_encrypt_key(self.logger)
    if not key_exists:
      self.logger.warning(
        "No encryption key found. Hence if any API key exists, it will be removed and the user needs to re-enter it.")
      self.config_model.dataverse_login_info["api_token"] = None
      self.config_model.dataverse_login_info["dataverse_id"] = None
      self.save_config()
    else:
      self.config_model.dataverse_login_info["api_token"] = decrypt_data(self.logger, self.encrypt_key,
                                                                         self.config_model.dataverse_login_info[
                                                                           "api_token"])

  def update_dataverse_server(self, new_value: str) -> None:
    self.config_model.dataverse_login_info["server_url"] = new_value

  def update_api_token(self, new_value: str) -> None:
    self.config_model.dataverse_login_info["api_token"] = new_value

  def update_dataverse_line_edit(self) -> None:
    dataverse_id = self.dataverseListComboBox.currentData(QtCore.Qt.ItemDataRole.UserRole)
    self.dataverseLineEdit.setText(dataverse_id)

  def update_dataverse_id(self, new_value: str) -> None:
    self.config_model.dataverse_login_info["dataverse_id"] = new_value

  def save_config(self) -> None:
    self.logger.info("Saving config..")
    self.config_model.dataverse_login_info["api_token"] = encrypt_data(self.logger, self.encrypt_key,
                                                                       self.config_model.dataverse_login_info[
                                                                         "api_token"])
    self.db_api.update_model_document(self.config_model)

  def verify_server_url_and_api_token(self) -> None:
    self.logger.info("Verifying server URL and API token..")
    server_url = self.dataverseServerLineEdit.text()
    api_token = self.apiTokenLineEdit.text()
    if not (server_url and api_token):
      QMessageBox.information(self.instance, "Error", "Please enter both server URL and API token")
      return
    success, message = check_login_credentials(self.logger, api_token, server_url)
    if success:
      QMessageBox.information(self.instance, "Credentials Valid", message)
    else:
      QMessageBox.warning(self.instance, "Credentials Invalid", message)

  def load_dataverse_list(self) -> None:
    self.logger.info("Loading dataverse list..")
    server_url = self.dataverseServerLineEdit.text()
    api_token = self.apiTokenLineEdit.text()
    if not (server_url and api_token):
      QMessageBox.information(self.instance, "Error", "Please enter both server URL and API token")
      return
    self.dataverseListComboBox.clear()
    dataverse_client = DataverseClient(server_url, api_token)
    event_loop = get_event_loop()
    if dataverses := event_loop.run_until_complete(dataverse_client.get_dataverse_list()):
      if isinstance(dataverses, list) and isinstance(dataverses[0], dict):
        current_text = ""
        saved_id = self.config_model.dataverse_login_info.get("dataverse_id", "")
        for dataverse in dataverses:
          dv_title = dataverse.get('title', None)
          dv_id = dataverse.get('id', None)
          if dv_title and dv_id:
            self.dataverseListComboBox.addItem(dv_title, userData=dataverse['id'])
            if saved_id == dv_id:
              current_text = dv_title
        self.dataverseListComboBox.setCurrentText(current_text)
      else:
        self.logger.error("Failed to load dataverse list")


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = ConfigDialog()
  ui.instance.show()
  sys.exit(app.exec())
