#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox

from pasta_eln.GUI.dataverse.config_dialog import ConfigDialog
from pasta_eln.database.models.config_model import ConfigModel
from testsAdvanced.common.test_utils import read_json


@pytest.fixture()
def dataverse_list_mock() -> dict | None:
  return read_json('dataverse_list.json')


@pytest.fixture
def mock_message_box(mocker):
  mock = mocker.patch('PySide6.QtWidgets.QMessageBox')
  return mock.return_value


@pytest.fixture
def mock_webbrowser(mocker):
  return mocker.patch('webbrowser.open')


@pytest.fixture
def mock_dataverse_client(mocker, dataverse_list_mock: dataverse_list_mock):
  mock = mocker.patch('pasta_eln.dataverse.client.DataverseClient')
  mock_instance = mock.return_value
  mock_instance.get_dataverse_list.side_effect = mocker.AsyncMock(return_value=dataverse_list_mock)
  return mock_instance


@pytest.fixture
def mock_database_api(mocker):
  mock = mocker.patch('pasta_eln.dataverse.database_api.DatabaseAPI')
  mock_instance = mock.return_value
  mock_instance.get_config_model.return_value = ConfigModel(_id=12345678,
                                                            dataverse_login_info={"server_url": "http://valid.url",
                                                                                  "api_token": "decrypted_api_token",
                                                                                  "dataverse_id": "test_dataverse_id"},
                                                            parallel_uploads_count=1, project_upload_items={},
                                                            metadata={})
  return mock_instance


def mock_check_login_credentials(_, api_token, server_url) -> tuple[bool, str]:
  if api_token == 'decrypted_api_token' and server_url == 'http://valid.url':
    return True, "Data server is reachable and token is valid"
  elif api_token == 'invalid_api_token' and server_url == 'http://valid.url':
    return False, "Data server is reachable but token is invalid"
  else:
    return False, "Data server is not reachable"


@pytest.fixture
def config_dialog(qtbot, mocker, mock_message_box, mock_webbrowser, mock_dataverse_client, mock_database_api):
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DataverseClient', return_value=mock_dataverse_client)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.DatabaseAPI', return_value=mock_database_api)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.QMessageBox', new=mock_message_box)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.logging')
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.webbrowser', mock_webbrowser)
  mocker.patch('pasta_eln.GUI.dataverse.config_dialog.check_login_credentials',
               side_effect=mock_check_login_credentials)
  dialog = ConfigDialog()
  mocker.resetall()
  qtbot.addWidget(dialog.instance)
  return dialog


class TestDataverseConfigDialog:

  def test_component_launch_should_display_all_ui_elements(self, qtbot, config_dialog):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      assert config_dialog.buttonBox.isVisible() is True, "Dataverse config dialog button box not shown!"
      assert config_dialog.dataverseVerifyLoadPushButton.isVisible(), "Dataverse load verify push button not found"
      assert config_dialog.dataverseServerLineEdit.isVisible() is not None, "Dataverse server line edit not found"
      assert config_dialog.apiTokenLineEdit.isVisible() is not None, "API token line edit not found"
      assert config_dialog.dataverseListComboBox.isVisible() is not None, "Dataverse list combo box not found"
      assert config_dialog.dataverseLineEdit.isVisible() is not None, "Dataverse line edit not found"
      assert config_dialog.apiTokenHelpPushButton.isVisible() is not None, "API token help button not found"
      assert config_dialog.dataverseServerLabel.isVisible() is not None, "Dataverse server label not found"
      assert config_dialog.apiTokenLabel.isVisible() is not None, "API token label not found"
      assert config_dialog.dataverseListLabel.isVisible() is not None, "Dataverse list label not found"

      assert config_dialog.dataverseServerLabel.text() == "Dataverse URL", "Dataverse server label text not found"
      assert config_dialog.apiTokenLabel.text() == "API token", "API token label text not found"
      assert config_dialog.dataverseListLabel.text() == "Dataverse list", "Dataverse list label text not found"

      assert config_dialog.apiTokenHelpPushButton.text() == "Help", "API token help button text not found"
      assert config_dialog.dataverseVerifyLoadPushButton.text() == "Verify && Load", "Dataverse load verify push button text not found"
    qtbot.mouseClick(config_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)

  def test_component_launch_all_ui_elements_should_display_data(self, qtbot, config_dialog):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      assert config_dialog.buttonBox.isVisible() is True, "Dataverse config dialog button box not shown!"
      assert config_dialog.dataverseServerLineEdit.text() == "http://valid.url", "Dataverse server line edit should be set with mock data"
      assert config_dialog.apiTokenLineEdit.text() == "decrypted_api_token", "API token line edit should be set with mock data"
      assert config_dialog.dataverseListComboBox.currentText() == (
        "\"Open Science in the South - Management and research data: "
        "panorama and perspectives\n                in Africa,\" Dataverse\n            "), "Dataverse list combo box should be set with mock data"
      assert config_dialog.dataverseLineEdit.text() == "opensciencesouth", "Dataverse line edit should be set with mock data"
      assert config_dialog.dataverseListComboBox.count() == 115, "Dataverse list combo box should have 115 items"
    qtbot.mouseClick(config_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)

  @pytest.mark.parametrize("test_id, server_url, api_token, expected_msg_box_heading, expected_msg_box_output",
                           [  # Success tests with various realistic test values
                             ("success_case_with_valid_url_api_token", "http://valid.url", "decrypted_api_token",
                              "Credentials Valid", "Data server is reachable and token is valid"),

                             # Edge cases with various realistic test values
                             ("edge_case_api_token_none", "http://valid.url", None, "Error",
                              "Please enter both server URL and API token"), (
                               "edge_case_api_token_empty", "http://valid.url", "", "Error",
                               "Please enter both server URL and API token"), (
                               "edge_case_URL_none", None, "decrypted_api_token", "Error",
                               "Please enter both server URL and API token"), (
                               "edge_case_URL_empty", "", "decrypted_api_token", "Error",
                               "Please enter both server URL and API token"), (
                               "edge_case_both_URL_api_token_none", None, None, "Error",
                               "Please enter both server URL and API token"), (
                               "edge_case_both_URL_api_token_empty", "", "", "Error",
                               "Please enter both server URL and API token"),

                             # Error cases
                             ("error_case_invalid_api_token", "http://valid.url", "invalid_api_token",
                              "Credentials Invalid", "Data server is reachable but token is invalid"), (
                               "error_case_invalid_URL", "http://invalid.url", "decrypted_api_token",
                               "Credentials Invalid", "Data server is not reachable")])
  def test_verify_with_different_url_api_token_combinations_should_give_expected_result(self, qtbot, config_dialog,
                                                                                        mock_message_box, test_id,
                                                                                        server_url, api_token,
                                                                                        expected_msg_box_heading,
                                                                                        expected_msg_box_output):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      config_dialog.dataverseServerLineEdit.setText(server_url)
      config_dialog.apiTokenLineEdit.setText(api_token)
      qtbot.mouseClick(config_dialog.dataverseVerifyLoadPushButton, Qt.LeftButton)
      if expected_msg_box_heading == "Credentials Valid":
        mock_message_box.information.assert_any_call(config_dialog.instance, expected_msg_box_heading,
                                                     expected_msg_box_output)
      else:
        mock_message_box.warning.assert_any_call(config_dialog.instance, expected_msg_box_heading,
                                                 expected_msg_box_output)
    qtbot.mouseClick(config_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)

  def test_help_button_click_should_open_help_url(self, qtbot, config_dialog, mock_webbrowser):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      qtbot.mouseClick(config_dialog.apiTokenHelpPushButton, Qt.LeftButton)
      mock_webbrowser.open.assert_called_once_with("https://data.fz-juelich.de/guide/api/auth.html")

  def test_cancel_button_click_should_close_dialog(self, qtbot, config_dialog):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
    qtbot.mouseClick(config_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert config_dialog.instance.isVisible() is False, "Dataverse config dialog should be closed!"

  @pytest.mark.parametrize("test_id, dataverse_title, expected_dataverse_id",
                           [  # Success tests with various realistic test values
                             ("success_case_1", "Harvard Datavers-DASH Integration Demo Site", "HDV_DASH"),
                             ("success_case_2", "ABC University Data Repository", "ABCDD"),
                             ("success_case_3", "Faculty Dataverse", "iitropar_faculty"),
                             ("success_case_4", "INLS 756 Dataverse", "inls756"),
                             ("success_case_4", "NTU Dataverse Training, November 11, 2019", "NTUtraining"), (
                               "success_case_4", "New York Cooperative Fish and Wildlife Research Unit Dataverse",
                               "NY_coop"), ("success_case_4", "Open Repositories, 2023 Workshop", "OpenRepo2023"), ])
  def test_dataverse_list_combo_box_changed_should_update_dataverse_line_edit(self, qtbot, config_dialog, test_id,
                                                                              dataverse_title, expected_dataverse_id):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      qtbot.keyClicks(config_dialog.dataverseListComboBox, dataverse_title, delay=1)
      assert config_dialog.dataverseLineEdit.text() == expected_dataverse_id

  def test_dataverse_load_button_click_should_reload_dataverse_list_and_update_dataverse_line_edit(self, qtbot,
                                                                                                   config_dialog):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      qtbot.keyClicks(config_dialog.dataverseListComboBox, "Harvard Datavers-DASH Integration Demo Site", delay=1)
      assert config_dialog.dataverseLineEdit.text() == "HDV_DASH"
      qtbot.mouseClick(config_dialog.dataverseVerifyLoadPushButton, Qt.LeftButton, delay=1)
      assert config_dialog.dataverseLineEdit.text() == "HDV_DASH"
      assert config_dialog.dataverseListComboBox.currentText() == "Harvard Datavers-DASH Integration Demo Site", "Dataverse list combo box should be reset with mock data"
      assert config_dialog.dataverseListComboBox.count() == 115, "Dataverse list combo box should have 115 items"

  def test_dataverse_load_button_click_should_reload_dataverse_list_and_update_dataverse_line_edit_to_the_saved_dataverse_id(
      self, qtbot, config_dialog):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      config_dialog.config_model.dataverse_login_info["dataverse_id"] = "datafest2021"
      qtbot.mouseClick(config_dialog.dataverseVerifyLoadPushButton, Qt.LeftButton, delay=1)
      assert config_dialog.dataverseLineEdit.text() == "datafest2021"
      assert config_dialog.dataverseListComboBox.currentText() == "Datafest 2021, Demo Dataverse", "Dataverse list combo box should be reset with mock data"
      assert config_dialog.dataverseListComboBox.count() == 115, "Dataverse list combo box should have 115 items"

  def test_dataverse_load_button_click_when_server_URL_or_token_invalid_should_return_error(self, mocker, qtbot,
                                                                                            config_dialog,
                                                                                            mock_dataverse_client,
                                                                                            mock_message_box):
    # Arrange
    mock_dataverse_client.get_dataverse_list.side_effect = mocker.AsyncMock(return_value="Invalid URL or API token")
    config_dialog.verify_server_url_and_api_token = mocker.MagicMock(return_value=True)
    # Act
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=500):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      config_dialog.dataverseServerLineEdit.setText("InvalidURL")
      config_dialog.apiTokenLineEdit.setText("InvalidToken")
      config_dialog.config_model.dataverse_login_info["dataverse_id"] = "datafest2021"
      qtbot.mouseClick(config_dialog.dataverseVerifyLoadPushButton, Qt.LeftButton, delay=2)
      assert config_dialog.dataverseListComboBox.currentText() == ""
      assert config_dialog.dataverseListComboBox.count() == 0, "Dataverse list combo box should have 0 items"
      config_dialog.logger.error("Failed to load dataverse list, error: %s", "Invalid URL or API token")
      mock_message_box.warning.assert_any_call(config_dialog.instance, "Error", "Failed to load dataverse list")

  def test_save_button_click_should_save_the_config(self, qtbot, config_dialog, mock_database_api):
    config_dialog.show()
    with qtbot.waitExposed(config_dialog.instance, timeout=1000):
      assert config_dialog.instance.isVisible() is True, "Dataverse config dialog should be shown!"
      config_dialog.dataverseServerLineEdit.setText("https://dataverse.harvard.edu")
      config_dialog.apiTokenLineEdit.setText("123456789")
      qtbot.keyClicks(config_dialog.dataverseListComboBox, "Harvard Datavers-DASH Integration Demo Site", delay=1)
      assert config_dialog.dataverseLineEdit.text() == "HDV_DASH"
      assert config_dialog.config_model.dataverse_login_info[
               "api_token"] == '123456789', "API token should not be encrypted before save"
    qtbot.mouseClick(config_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton, delay=1)
    mock_database_api.save_config_model.assert_called_once_with(config_dialog.config_model)
    assert config_dialog.instance.isVisible() is False, "Dataverse config dialog should be closed!"
