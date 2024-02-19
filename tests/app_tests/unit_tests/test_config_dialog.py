#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: test_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore

from pasta_eln.GUI.dataverse.config_dialog import ConfigDialog
from pasta_eln.dataverse.config_model import ConfigModel


@pytest.fixture
def mock_message_box():
  with patch('PySide6.QtWidgets.QMessageBox') as mock:
    yield mock.return_value


@pytest.fixture
def mock_webbrowser():
  with patch('webbrowser.open') as mock:
    yield mock


@pytest.fixture
def mock_dataverse_client(mocker):
  with patch('pasta_eln.dataverse.client.DataverseClient') as mock:
    mock_instance = mock.return_value
    mock_instance.get_dataverse_list.side_effect = mocker.AsyncMock(
      return_value=[{'title': 'Dataverse1', 'id': 'dv1'}, {'title': 'Dataverse2', 'id': 'dv2'}])
    yield mock_instance


@pytest.fixture
def mock_database_api():
  with patch('pasta_eln.dataverse.database_api.DatabaseAPI') as mock:
    mock_instance = mock.return_value
    mock_instance.get_model.return_value = ConfigModel(_id="test_id", _rev="test_rev",
                                                       dataverse_login_info={"server_url": "http://valid.url",
                                                                             "api_token": "test_token",
                                                                             "dataverse_id": "test_dataverse_id"},
                                                       parallel_uploads_count=1, project_upload_items={}, metadata={})
    yield mock_instance


@pytest.fixture
def config_dialog(qapp, qtbot, mocker, mock_message_box, mock_webbrowser, mock_dataverse_client, mock_database_api):
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DataverseClient', return_value=mock_dataverse_client)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DatabaseAPI', return_value=mock_database_api)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QMessageBox', new=mock_message_box)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.logging')
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.get_encrypt_key', return_value=(True, b"test_encrypt_key"))
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.decrypt_data', return_value='decrypted_api_token')
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.encrypt_data', return_value='encrypted_api_token')
  dialog = ConfigDialog()
  mocker.resetall()
  qtbot.addWidget(dialog.instance)
  return dialog


class TestConfigDialog:

  # Parametrized test for update_dataverse_server method
  @pytest.mark.parametrize("test_id, server_url",
                           [("success_path_valid_url", "http://valid.url"), ("edge_case_empty_string", ""),
                            ("error_case_invalid_url", "not_a_url")])
  def test_update_dataverse_server(self, qtbot, config_dialog, test_id, server_url):
    # Act
    config_dialog.update_dataverse_server(server_url)

    # Assert
    assert config_dialog.config_model.dataverse_login_info["server_url"] == server_url

  # Parametrized test for update_api_token method
  @pytest.mark.parametrize("test_id, api_token",
                           [("success_path_valid_token", "valid_token"), ("edge_case_empty_string", ""),
                            ("error_case_special_chars", "!@#$%^&*()")])
  def test_update_api_token(self, qtbot, config_dialog, test_id, api_token):

    # Act
    config_dialog.update_api_token(api_token)

    # Assert
    assert config_dialog.config_model.dataverse_login_info["api_token"] == api_token

  @pytest.mark.parametrize("test_id, input_data, expected_output",
                           [("success_path_1", "12345", "12345"), ("success_path_2", "67890", "67890"),
                            ("edge_case_empty", "", ""), ("edge_case_none", None, ""),  # Add more test cases as needed
                            ])
  def test_update_dataverse_line_edit(self, mocker, config_dialog, test_id, input_data, expected_output):
    # Arrange
    config_dialog.dataverseListComboBox = mocker.MagicMock()
    config_dialog.dataverseListComboBox.currentData.return_value = input_data

    # Act
    config_dialog.update_dataverse_line_edit()

    # Assert
    config_dialog.dataverseListComboBox.currentData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole)
    assert config_dialog.dataverseLineEdit.text() == expected_output, f"Test failed for {test_id}"

  @pytest.mark.parametrize("new_value, test_id",
                           [("12345", "success_path_numeric"), ("new_dataverse", "success_path_alpha"),
                            ("dv_2023_01", "success_path_alphanumeric"), ("", "edge_case_empty_string")])
  def test_update_dataverse_id(self, config_dialog, new_value, test_id):
    # Arrange
    original_value = config_dialog.config_model.dataverse_login_info.get("dataverse_id", "")

    # Act
    config_dialog.update_dataverse_id(new_value)

    # Assert
    assert config_dialog.config_model.dataverse_login_info["dataverse_id"] == new_value

  # Parametrized test for save_config method
  @pytest.mark.parametrize("test_id", [("success_path_save_config")])
  def test_save_config(self, qtbot, mocker, config_dialog, test_id, mock_message_box):
    # Arrange
    config_dialog.db_api.update_model_document = MagicMock()
    mock_encrypt_data = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.encrypt_data',
                                     return_value='encrypted_api_token')
    unencrypted_api_token = config_dialog.config_model.dataverse_login_info["api_token"]

    # Act
    config_dialog.save_config()

    # Assert
    config_dialog.logger.info.assert_called_once_with("Saving config..")
    mock_encrypt_data.assert_called_once_with(config_dialog.logger, config_dialog.encrypt_key, unencrypted_api_token)
    config_dialog.db_api.update_model_document.assert_called_once_with(config_dialog.config_model)
    config_dialog.config_model.dataverse_login_info["api_token"] = "decrypted_api_token"

  # Parametrized test for verify_server_url_and_api_token method
  @pytest.mark.parametrize("test_id, server_url, api_token, success, message", [
    ("success_path_valid_credentials", "http://valid.url", "valid_token", True, "Credentials are valid."),
    ("error_case_invalid_credentials", "http://invalid.url", "invalid_token", False, "Invalid credentials."),
    ("error_case_empty_fields", "", "", False, "Please enter both server URL and API token")])
  def test_verify_server_url_and_api_token(self, config_dialog, test_id, server_url, api_token, success, message,
                                           mock_message_box):
    # Arrange
    config_dialog.dataverseServerLineEdit.setText(server_url)
    config_dialog.apiTokenLineEdit.setText(api_token)
    with patch('pasta_eln.GUI.dataverse.config_dialog.check_login_credentials',
               return_value=(success, message)) as mock_check:

      # Act
      config_dialog.verify_server_url_and_api_token()

      # Assert
      config_dialog.logger.info.assert_called_once_with("Verifying server URL and API token..")
      if not server_url or not api_token:
        mock_message_box.information.assert_called_once_with(config_dialog.instance, "Error",
                                                             "Please enter both server URL and API token")
      elif success:
        mock_message_box.information.assert_called_once_with(config_dialog.instance, "Credentials Valid", message)
      else:
        mock_message_box.warning.assert_called_once_with(config_dialog.instance, "Credentials Invalid", message)

  # Parametrized test for load_dataverse_list method
  @pytest.mark.parametrize("test_id, server_url, api_token, dataverse_list, expected_items", [(
      "success_path_valid_data", "http://valid.url", "valid_token",
      [{'title': 'Dataverse1', 'id': 'dv1'}, {'title': 'Dataverse2', 'id': 'dv2'}], 2),
    ("success_path_valid_data", "http://valid.url", "valid_token", [{'title': 'Dataverse1', 'id': 'dv1'}], 1), (
        "success_path_valid_data_saved_id_exists", "http://valid.url", "valid_token",
        [{'title': 'Dataverse1', 'id': 'test_dataverse_id'}, ], 1),
    ("edge_case_empty_fields", "http://valid.url", "valid_token", [], 0),
    ("edge_case_not_list", "http://valid.url", "valid_token", {"title": "Dataverse"}, 0),
    ("edge_case_list_with_non_dict", "http://valid.url", "valid_token", [1, 2, 3], 0),
    ("edge_case_list_with_no_properties", "http://valid.url", "valid_token", [{'title': 'Dataverse'}], 0),
    ("error_case_empty_fields", "", "", [], 0)])
  def test_load_dataverse_list(self, mocker, config_dialog, test_id, server_url, api_token, expected_items,
                               dataverse_list, mock_dataverse_client, mock_message_box):
    # Arrange
    mock_dataverse_client.get_dataverse_list.side_effect = mocker.AsyncMock(return_value=dataverse_list)
    config_dialog.dataverseServerLineEdit.setText(server_url)
    config_dialog.apiTokenLineEdit.setText(api_token)

    # Act
    config_dialog.load_dataverse_list()

    # Assert
    config_dialog.logger.info.assert_called_once_with("Loading dataverse list..")
    if not server_url or not api_token:
      mock_message_box.information.assert_called_once_with(config_dialog.instance, "Error",
                                                           "Please enter both server URL and API token")
    else:
      assert config_dialog.dataverseListComboBox.count() == expected_items
      mock_dataverse_client.get_dataverse_list.assert_called_once_with()
    if test_id == "success_path_valid_data_saved_id_exists":
      assert config_dialog.dataverseListComboBox.currentData(QtCore.Qt.ItemDataRole.UserRole) == "test_dataverse_id"
      assert config_dialog.dataverseListComboBox.currentText() == "Dataverse1"
    if test_id == "edge_case_not_list":
      config_dialog.logger.error.assert_called_once_with("Failed to load dataverse list")

  @pytest.mark.parametrize("key_exists, encrypt_key, expected_api_token, expected_dataverse_id, test_id",
                           [  # Success path tests
                             (True, 'mock_key', 'decrypted_api_token', 'some_dataverse_id', 'success_path_valid_key'),
                             (True, '', 'decrypted_api_token', 'some_dataverse_id', 'success_path_empty_key'),

                             # Edge cases
                             (True, None, 'decrypted_api_token', 'some_dataverse_id', 'edge_case_none_key'),

                             # Error cases
                             (False, None, None, None, 'error_no_key'), ])
  def test_decrypt_api_token(self, mocker, config_dialog, key_exists, encrypt_key, expected_api_token,
                             expected_dataverse_id, test_id):
    # Arrange
    config_dialog.encrypt_key = None
    mock_save_config = mocker.MagicMock()
    config_dialog.config_model.dataverse_login_info = {'api_token': 'encrypted_api_token',
                                                       'dataverse_id': 'some_dataverse_id'}
    config_dialog.save_config = mock_save_config

    mock_get_key = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.get_encrypt_key',
                                return_value=(key_exists, encrypt_key))
    mock_decrypt_data = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.decrypt_data',
                                     return_value='decrypted_api_token')

    # Act
    config_dialog.decrypt_api_token()

    # Assert
    if key_exists:
      mock_get_key.assert_called_once_with(config_dialog.logger)
      mock_decrypt_data.assert_called_once_with(config_dialog.logger, encrypt_key, 'encrypted_api_token')
    else:
      config_dialog.logger.warning.assert_called_once_with(
        'No encryption key found. Hence if any API key exists, it will be removed and the user needs to re-enter it.')
      mock_save_config.assert_called_once()

    assert config_dialog.config_model.dataverse_login_info["dataverse_id"] == expected_dataverse_id
    assert config_dialog.config_model.dataverse_login_info["api_token"] == expected_api_token
