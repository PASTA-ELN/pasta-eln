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
from asyncio import get_event_loop
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QMessageBox

from pasta_eln.GUI.dataverse.config_dialog_base import Ui_ConfigDialogBase
from pasta_eln.dataverse.client import DataverseClient
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

    self.dataverseServerLineEdit.setText(self.config_model.dataverse_login_info.get("server_url", ""))
    self.apiTokenLineEdit.setText(self.config_model.dataverse_login_info.get("api_token", ""))
    self.dataverseListComboBox.setCurrentText(self.config_model.dataverse_login_info.get("dataverse_id", ""))
    self.dataverseLineEdit.setText(self.config_model.dataverse_login_info.get("dataverse_id", ""))

    # Setup slots
    self.dataverseServerLineEdit.textChanged[str].connect(self.update_dataverse_server)
    self.apiTokenLineEdit.textChanged[str].connect(self.update_api_token)
    self.dataverseLineEdit.textChanged[str].connect(self.update_dataverse_via_line_edit)
    self.dataverseListComboBox.currentTextChanged.connect(self.update_dataverse)

    self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_config)

    self.apiTokenVerifyPushButton.clicked.connect(self.verify_api_token)
    self.dataverseLoadPushButton.clicked.connect(self.load_dataverse_list)

    self.dataverseLoadPushButton.click()

  def update_dataverse_server(self, new_value: str) -> None:
    self.config_model.dataverse_login_info["server_url"] = new_value

  def update_api_token(self, new_value: str) -> None:
    self.config_model.dataverse_login_info["api_token"] = new_value

  def update_dataverse(self, new_value: str) -> None:
    dataverse_id = self.dataverseListComboBox.currentData(QtCore.Qt.ItemDataRole.UserRole)
    self.config_model.dataverse_login_info["dataverse_id"] = dataverse_id or new_value
    self.dataverseLineEdit.setText(dataverse_id)

  def update_dataverse_via_line_edit(self, new_value: str) -> None:
    self.config_model.dataverse_login_info["dataverse_id"] = new_value

  def save_config(self) -> None:
    self.db_api.update_model_document(self.config_model)

  def verify_api_token(self) -> None:
    server_url = self.dataverseServerLineEdit.text()
    api_token = self.apiTokenLineEdit.text()
    if not (server_url and api_token):
      QMessageBox.information(self.instance, "Error", "Please enter both server URL and API token")
      return
    dataverse_client = DataverseClient(server_url, api_token)
    event_loop = get_event_loop()
    if result := event_loop.run_until_complete(dataverse_client.check_if_dataverse_server_reachable()):
      if result[0]:
        QMessageBox.information(self.instance, "Success", result[1])
      else:
        QMessageBox.warning(self.instance, "Failed", f"Server is not reachable. Error: {result[1][0]}")

  def load_dataverse_list(self) -> None:
    server_url = self.dataverseServerLineEdit.text()
    api_token = self.apiTokenLineEdit.text()
    if not (server_url and api_token):
      QMessageBox.information(self.instance, "Error", "Please enter both server URL and API token")
      return
    dataverse_client = DataverseClient(server_url, api_token)
    self.dataverseListComboBox.clear()
    event_loop = get_event_loop()
    if dataverses := event_loop.run_until_complete(dataverse_client.get_dataverse_list()):
      if isinstance(dataverses, list):
        current_text = ""
        saved_id = self.config_model.dataverse_login_info.get("dataverse_id", "")
        for dataverse in dataverses:
          self.dataverseListComboBox.addItem(dataverse['title'], userData=dataverse['id'])
          if saved_id == dataverse['id']:
            current_text = dataverse['title']
        self.dataverseListComboBox.setCurrentText(current_text)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = ConfigDialog()
  ui.instance.show()
  sys.exit(app.exec())
