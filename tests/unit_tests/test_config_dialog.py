#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore, QtWidgets

from pasta_eln.GUI.dataverse.config_dialog import ConfigDialog
from pasta_eln.dataverse.config_error import ConfigError
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
    mock_instance.get_config_model.return_value = ConfigModel(_id="test_id", _rev="test_rev",
                                                              dataverse_login_info={"server_url": "http://valid.url",
                                                                                    "api_token": "test_token",
                                                                                    "dataverse_id": "test_dataverse_id"},
                                                              parallel_uploads_count=1, project_upload_items={},
                                                              metadata={})
    yield mock_instance


@pytest.fixture
def mock_config_dialog(qtbot, mocker, mock_message_box, mock_webbrowser, mock_dataverse_client, mock_database_api):
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DataverseClient', return_value=mock_dataverse_client)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DatabaseAPI', return_value=mock_database_api)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QMessageBox', new=mock_message_box)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.logging')
  dialog = ConfigDialog()
  mocker.resetall()
  qtbot.addWidget(dialog.instance)
  return dialog


class TestConfigDialog:

  # Happy path test
  @pytest.mark.parametrize("server_url,api_token,dataverse_id", [
    ('http://valid.url', "test_token", "test_dataverse_id"),
  ])
  def test_config_dialog_init_success_path(self, mocker, mock_database_api, mock_dataverse_client, mock_message_box,
                                           server_url, api_token,
                                           dataverse_id):
    # Arrange
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DataverseClient', return_value=mock_dataverse_client)
    mock_db_ctor = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DatabaseAPI', return_value=mock_database_api)
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QMessageBox', new=mock_message_box)
    mock_logger = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.logging')
    mock_qdialog = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QDialog')
    mock_validator = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QRegularExpressionValidator')
    mock_regex = mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QRegularExpression')
    mock_setup_ui = mocker.patch('pasta_eln.GUI.dataverse.config_dialog_base.Ui_ConfigDialogBase.setupUi')
    mocker.patch.object(ConfigDialog, 'dataverseServerLineEdit', create=True)
    mocker.patch.object(ConfigDialog, 'apiTokenLineEdit', create=True)
    mocker.patch.object(ConfigDialog, 'dataverseListComboBox', create=True)
    mocker.patch.object(ConfigDialog, 'dataverseLineEdit', create=True)
    mocker.patch.object(ConfigDialog, 'buttonBox', create=True)
    mocker.patch.object(ConfigDialog, 'apiTokenVerifyPushButton', create=True)
    mocker.patch.object(ConfigDialog, 'dataverseLoadPushButton', create=True)
    mocker.patch.object(ConfigDialog, 'apiTokenHelpPushButton', create=True)

    # Act
    config_dialog = ConfigDialog()

    # Assert
    mock_logger.getLogger.assert_called_once_with('pasta_eln.GUI.dataverse.config_dialog.ConfigDialog')
    mock_qdialog.assert_called_once()
    mock_setup_ui.assert_called_once_with(mock_qdialog.return_value)
    mock_db_ctor.assert_called_once()
    mock_database_api.get_config_model.assert_called_once()
    mock_regex.assert_called_once_with("\\S*")
    mock_validator.assert_called_once_with(mock_regex.return_value)
    config_dialog.dataverseServerLineEdit.setValidator.assert_called_once_with(mock_validator.return_value)

    config_dialog.dataverseListComboBox.setCurrentText.assert_called_once_with(dataverse_id)
    config_dialog.dataverseServerLineEdit.setText.assert_called_once_with(server_url)
    config_dialog.apiTokenLineEdit.setText.assert_called_once_with(api_token)
    config_dialog.dataverseLineEdit.setText.assert_called_once_with(dataverse_id)

    config_dialog.dataverseServerLineEdit.textChanged[str].connect.assert_called_once_with(
      config_dialog.update_dataverse_server)
    config_dialog.apiTokenLineEdit.textChanged[str].connect.assert_called_once_with(
      config_dialog.update_api_token)
    config_dialog.dataverseLineEdit.textChanged[str].connect.assert_called_once_with(
      config_dialog.update_dataverse_id)
    config_dialog.dataverseListComboBox.currentTextChanged.connect.assert_called_once_with(
      config_dialog.update_dataverse_line_edit)
    config_dialog.buttonBox.button.assert_called_once_with(QtWidgets.QDialogButtonBox.Save)
    config_dialog.buttonBox.button.return_value.clicked.connect.assert_called_once_with(
      config_dialog.save_config)
    config_dialog.apiTokenVerifyPushButton.clicked.connect.assert_called_once_with(
      config_dialog.verify_server_url_and_api_token)
    config_dialog.dataverseLoadPushButton.clicked.connect.assert_called_once_with(
      config_dialog.load_dataverse_list)
    config_dialog.apiTokenHelpPushButton.clicked.connect.assert_called_once()

    config_dialog.dataverseServerLineEdit.text.assert_called_once()
    config_dialog.apiTokenLineEdit.text.assert_called_once()
    config_dialog.dataverseLoadPushButton.click.assert_called_once()

  # Error case: Config not found
  def test_config_dialog_init_error_no_config(self, mocker, mock_database_api, mock_dataverse_client, mock_message_box):
    # Arrange
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DatabaseAPI', return_value=mock_database_api)
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.logging')
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QDialog')
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog_base.Ui_ConfigDialogBase.setupUi')
    mock_config = ConfigModel()
    mock_database_api.get_config_model.return_value = mock_config  # Simulate no config found

    # Act & Assert
    with pytest.raises(ConfigError) as exc_info:
      ConfigDialog()  # Attempt to initialize the dialog
    assert "Config not found, Corrupt installation!" in str(exc_info.value)

  # Edge case: Empty dataverse login info
  @pytest.mark.parametrize("server_url,api_token,dataverse_id", [
    pytest.param("", "", "", id="empty_login_info"),
  ])
  def test_config_dialog_init_edge_empty_login_info(self, mocker, mock_database_api, mock_dataverse_client,
                                                    mock_message_box, server_url,
                                                    api_token, dataverse_id):
    # Arrange
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DataverseClient', return_value=mock_dataverse_client)
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DatabaseAPI', return_value=mock_database_api)
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QMessageBox', new=mock_message_box)
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.logging')
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QDialog')
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QRegularExpressionValidator')
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QRegularExpression')
    mocker.patch('pasta_eln.GUI.dataverse.config_dialog_base.Ui_ConfigDialogBase.setupUi')
    mocker.patch.object(ConfigDialog, 'dataverseServerLineEdit', create=True)
    mocker.patch.object(ConfigDialog, 'apiTokenLineEdit', create=True)
    mocker.patch.object(ConfigDialog, 'dataverseListComboBox', create=True)
    mocker.patch.object(ConfigDialog, 'dataverseLineEdit', create=True)
    mocker.patch.object(ConfigDialog, 'buttonBox', create=True)
    mocker.patch.object(ConfigDialog, 'apiTokenVerifyPushButton', create=True)
    mocker.patch.object(ConfigDialog, 'dataverseLoadPushButton', create=True)
    mocker.patch.object(ConfigDialog, 'apiTokenHelpPushButton', create=True)
    mock_database_api.get_config_model.return_value.dataverse_login_info = {}  # Empty login info

    # Act - Initialization is done in the fixture
    config_dialog = ConfigDialog()

    # Assert
    config_dialog.dataverseServerLineEdit.setText.assert_called_once_with(server_url)
    config_dialog.apiTokenLineEdit.setText.assert_called_once_with(api_token)
    config_dialog.dataverseLineEdit.setText.assert_called_once_with(dataverse_id)

  # Parametrized test for update_dataverse_server method
  @pytest.mark.parametrize("test_id, server_url",
                           [("success_path_valid_url", "http://valid.url"), ("edge_case_empty_string", ""),
                            ("error_case_invalid_url", "not_a_url")])
  def test_update_dataverse_server(self, mock_config_dialog, test_id, server_url):
    # Act
    mock_config_dialog.update_dataverse_server(server_url)

    # Assert
    assert mock_config_dialog.config_model.dataverse_login_info["server_url"] == server_url

  # Parametrized test for update_api_token method
  @pytest.mark.parametrize("test_id, api_token",
                           [("success_path_valid_token", "valid_token"), ("edge_case_empty_string", ""),
                            ("error_case_special_chars", "!@#$%^&*()")])
  def test_update_api_token(self, mock_config_dialog, test_id, api_token):

    # Act
    mock_config_dialog.update_api_token(api_token)

    # Assert
    assert mock_config_dialog.config_model.dataverse_login_info["api_token"] == api_token

  @pytest.mark.parametrize("test_id, input_data, expected_output",
                           [("success_path_1", "12345", "12345"), ("success_path_2", "67890", "67890"),
                            ("edge_case_empty", "", ""), ("edge_case_none", None, ""),  # Add more test cases as needed
                            ])
  def test_update_dataverse_line_edit(self, mocker, mock_config_dialog, test_id, input_data, expected_output):
    # Arrange
    mock_config_dialog.dataverseListComboBox = mocker.MagicMock()
    mock_config_dialog.dataverseListComboBox.currentData.return_value = input_data

    # Act
    mock_config_dialog.update_dataverse_line_edit()

    # Assert
    mock_config_dialog.dataverseListComboBox.currentData.assert_called_once_with(QtCore.Qt.ItemDataRole.UserRole)
    assert mock_config_dialog.dataverseLineEdit.text() == expected_output, f"Test failed for {test_id}"

  @pytest.mark.parametrize("new_value, test_id",
                           [("12345", "success_path_numeric"), ("new_dataverse", "success_path_alpha"),
                            ("dv_2023_01", "success_path_alphanumeric"), ("", "edge_case_empty_string")])
  def test_update_dataverse_id(self, mock_config_dialog, new_value, test_id):
    # Arrange
    original_value = mock_config_dialog.config_model.dataverse_login_info.get("dataverse_id", "")

    # Act
    mock_config_dialog.update_dataverse_id(new_value)

    # Assert
    assert mock_config_dialog.config_model.dataverse_login_info["dataverse_id"] == new_value

  # Parametrized test for save_config method
  @pytest.mark.parametrize("test_id", [("success_path_save_config")])
  def test_save_config(self, mock_config_dialog, test_id, mock_message_box):
    # Arrange
    mock_config_dialog.db_api.update_model_document = MagicMock()

    # Act
    mock_config_dialog.save_config()

    # Assert
    mock_config_dialog.logger.info.assert_called_once_with("Saving config..")
    mock_config_dialog.db_api.save_config_model.assert_called_once_with(mock_config_dialog.config_model)

  # Parametrized test for verify_server_url_and_api_token method
  @pytest.mark.parametrize("test_id, server_url, api_token, success, message", [
    ("success_path_valid_credentials", "http://valid.url", "valid_token", True, "Credentials are valid."),
    ("error_case_invalid_credentials", "http://invalid.url", "invalid_token", False, "Invalid credentials."),
    ("error_case_empty_fields", "", "", False, "Please enter both server URL and API token")])
  def test_verify_server_url_and_api_token(self, mock_config_dialog, test_id, server_url, api_token, success, message,
                                           mock_message_box):
    # Arrange
    mock_config_dialog.dataverseServerLineEdit.setText(server_url)
    mock_config_dialog.apiTokenLineEdit.setText(api_token)
    with patch('pasta_eln.GUI.dataverse.config_dialog.check_login_credentials',
               return_value=(success, message)) as mock_check:

      # Act
      mock_config_dialog.verify_server_url_and_api_token()

      # Assert
      mock_config_dialog.logger.info.assert_called_once_with("Verifying server URL and API token..")
      if not server_url or not api_token:
        mock_message_box.warning.assert_called_once_with(mock_config_dialog.instance, "Error",
                                                         "Please enter both server URL and API token")
      elif success:
        mock_message_box.information.assert_called_once_with(mock_config_dialog.instance, "Credentials Valid", message)
      else:
        mock_message_box.warning.assert_called_once_with(mock_config_dialog.instance, "Credentials Invalid", message)

  # Parametrized test for load_dataverse_list method
  @pytest.mark.parametrize("test_id, server_url, api_token, dataverse_list, expected_items", [(
      "success_path_valid_data", "http://valid.url", "valid_token",
      [{'title': 'Dataverse1', 'id': 'dv1'}, {'title': 'Dataverse2', 'id': 'dv2'}], 2),
    ("success_path_valid_data", "http://valid.url", "valid_token", [{'title': 'Dataverse1', 'id': 'dv1'}], 1), (
        "success_path_valid_data_saved_id_exists", "http://valid.url", "valid_token",
        [{'title': 'Dataverse1', 'id': 'dv1'}, ], 1),
    ("edge_case_empty_fields", "http://valid.url", "valid_token", [], 0),
    ("edge_case_not_list", "http://valid.url", "valid_token", {"title": "Dataverse"}, 0),
    ("edge_case_list_with_non_dict", "http://valid.url", "valid_token", [1, 2, 3], 0),
    ("edge_case_list_with_no_properties", "http://valid.url", "valid_token", [{'title': 'Dataverse'}], 0),
    ("error_case_empty_fields", "", "", [], 0),
    ("error_case_list_retrieval_failed", "http://valid.url", "valid_token", "404 error not found", 0)])
  def test_load_dataverse_list(self, mocker, mock_config_dialog, test_id, server_url, api_token, expected_items,
                               dataverse_list, mock_dataverse_client, mock_message_box):
    # Arrange
    mock_dataverse_client.get_dataverse_list.side_effect = mocker.AsyncMock(return_value=dataverse_list)
    mock_config_dialog.dataverseServerLineEdit.setText(server_url)
    mock_config_dialog.apiTokenLineEdit.setText(api_token)

    # Act
    mock_config_dialog.load_dataverse_list()

    # Assert
    mock_config_dialog.logger.info.assert_called_once_with("Loading dataverse list..")
    if not server_url or not api_token:
      mock_message_box.warning.assert_called_once_with(mock_config_dialog.instance, "Error",
                                                       "Please enter both server URL and API token")
    else:
      assert mock_config_dialog.dataverseListComboBox.count() == expected_items
      mock_dataverse_client.get_dataverse_list.assert_called_once_with()
    if test_id == "success_path_valid_data_saved_id_exists":
      assert mock_config_dialog.dataverseListComboBox.currentData(QtCore.Qt.ItemDataRole.UserRole) == "dv1"
      assert mock_config_dialog.dataverseListComboBox.currentText() == "Dataverse1"
    if test_id in ["edge_case_not_list", "error_case_list_retrieval_failed"]:
      mock_config_dialog.logger.error.assert_called_once_with("Failed to load dataverse list, error: %s",
                                                              dataverse_list)
      mock_message_box.warning.assert_called_once_with(mock_config_dialog.instance, "Error",
                                                       "Failed to load dataverse list")

  @pytest.mark.parametrize("test_id, show_exception", [  # Success tests with various realistic test values
    ("success_case", None),

    # Error cases could include scenarios where instance.show() raises an exception.
    ("error_case", Exception("Error during show")), ])
  def test_show(self, test_id, mock_config_dialog, show_exception):
    # Arrange
    mock_config_dialog.instance = MagicMock()
    if show_exception:
      mock_config_dialog.instance.show.side_effect = show_exception

    # Act
    if test_id == "error_case":
      with pytest.raises(Exception) as exc_info:
        mock_config_dialog.show()
      # Assert
      assert str(exc_info.value) == "Error during show"
    else:
      mock_config_dialog.show()
      # Assert
      mock_config_dialog.instance.show.assert_called_once()
