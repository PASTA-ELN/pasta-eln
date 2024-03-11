#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_edit_metadata_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import json
from os import getcwd
from os.path import dirname, join, realpath

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from pasta_eln.GUI.dataverse.edit_metadata_dialog import EditMetadataDialog
from pasta_eln.dataverse.config_model import ConfigModel


@pytest.fixture
def mock_message_box(mocker):
  mock = mocker.patch('PySide6.QtWidgets.QMessageBox')
  return mock.return_value


@pytest.fixture
def mock_database_api(mocker):
  mock = mocker.patch('pasta_eln.dataverse.database_api.DatabaseAPI')
  mock_instance = mock.return_value
  current_path = realpath(join(getcwd(), dirname(__file__)))
  with open(join(current_path, "..//..//pasta_eln//dataverse", "dataset-create-new-all-default-fields.json"),
            encoding="utf-8") as config_file:
    file_data = config_file.read()
    mock_instance.get_model.return_value = ConfigModel(_id="test_id",
                                                       _rev="test_rev",
                                                       dataverse_login_info={"server_url": "http://valid.url",
                                                                             "api_token": "encrypted_api_token",
                                                                             "dataverse_id": "test_dataverse_id"},
                                                       parallel_uploads_count=1,
                                                       project_upload_items={},
                                                       metadata=json.loads(file_data))
  return mock_instance


@pytest.fixture
def edit_metadata_dialog(qtbot, mocker, mock_message_box, mock_database_api):
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_dialog.DatabaseAPI', return_value=mock_database_api)
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_dialog.logging')
  dialog = EditMetadataDialog()
  mocker.resetall()
  qtbot.addWidget(dialog.instance)
  return dialog


class TestDataverseEditMetadataDialog:
  def test_component_launch_should_display_all_ui_elements(self, qtbot, edit_metadata_dialog):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.instance.isVisible() is True, "EditMetadataDialog should be shown!"
      assert edit_metadata_dialog.buttonBox.isVisible() is True, "EditMetadataDialog dialog button box not shown!"
      assert edit_metadata_dialog.minimalFullComboBox.isVisible(), "EditMetadataDialog minimalFullComboBox should be shown!"
      assert edit_metadata_dialog.metadataBlockComboBox.isVisible(), "EditMetadataDialog metadataBlockComboBox should be shown!"
      assert edit_metadata_dialog.typesComboBox.isVisible(), "EditMetadataDialog typesComboBox should be shown!"
      assert edit_metadata_dialog.licenseURLLineEdit.isVisible(), "EditMetadataDialog licenseURLLineEdit should be shown!"
      assert edit_metadata_dialog.licenseNameLineEdit.isVisible(), "EditMetadataDialog licenseNameLineEdit should be shown!"
      assert edit_metadata_dialog.buttonBox.button(
        edit_metadata_dialog.buttonBox.Save).isVisible(), "EditMetadataDialog Save button should be shown!"
      assert edit_metadata_dialog.buttonBox.button(
        edit_metadata_dialog.buttonBox.Cancel).isVisible(), "EditMetadataDialog Cancel button should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      primitive_vertical_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QVBoxLayout,
        "primitiveVerticalLayout")
      assert primitive_vertical_layout, "EditMetadataDialog primitive_compound_frame should be present!"
      delete_button = primitive_vertical_layout.itemAt(0).itemAt(1).widget()
      assert delete_button.isVisible(), "EditMetadataDialog primitive_compound_frame delete button should be shown!"
      assert not delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete button should be disabled!"
      assert not edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be disabled!"

      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Citation Metadata", "metadataBlockComboBox must be initialized with default 'Citation Metadata' option"
      assert edit_metadata_dialog.typesComboBox.currentText() == "Title", "typesComboBox must be initialized with default 'Title' option"
      assert edit_metadata_dialog.licenseNameLineEdit.text() == "CC0 1.0", "licenseNameLineEdit must be initialized with default 'CC0 1.0' option"
      assert edit_metadata_dialog.licenseURLLineEdit.text() == "http://creativecommons.org/publicdomain/zero/1.0", "licenseURLLineEdit must be initialized with default 'http://creativecommons.org/publicdomain/zero/1.0' option"
    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(edit_metadata_dialog.buttonBox.Cancel), Qt.LeftButton)
