#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_upload_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QDialogButtonBox

from pasta_eln.GUI.dataverse.upload_config_dialog import UploadConfigDialog
from pasta_eln.dataverse.config_model import ConfigModel


# Mock the external dependencies
@pytest.fixture
def mock_database_api():
  with patch('pasta_eln.dataverse.database_api.DatabaseAPI') as mock:
    yield mock


@pytest.fixture
def mock_config_model():
  return MagicMock(spec=ConfigModel)


@pytest.fixture
def mock_dialog(mocker, mock_database_api, mock_config_model):
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.logging')
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.QDialog')
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.QCheckBox')
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog_base.Ui_UploadConfigDialog.setupUi')
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog_base.Ui_UploadConfigDialog.__init__')
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.DatabaseAPI',
               return_value=mock_database_api)
  mocker.patch.object(UploadConfigDialog, 'config_reloaded', new_callable=mocker.PropertyMock)
  mocker.patch.object(UploadConfigDialog, 'numParallelComboBox', create=True)
  mocker.patch.object(UploadConfigDialog, 'data_hierarchy_types', create=True)
  mocker.patch.object(UploadConfigDialog, 'buttonBox', create=True)
  mocker.patch.object(UploadConfigDialog, 'projectItemsVerticalLayout', create=True)
  actual_set_data_hierarchy_types = UploadConfigDialog.set_data_hierarchy_types
  mocker.patch.object(UploadConfigDialog, 'set_data_hierarchy_types')
  actual_load_ui = UploadConfigDialog.load_ui
  mocker.patch.object(UploadConfigDialog, 'load_ui')
  dialog = UploadConfigDialog()
  dialog.set_data_hierarchy_types = actual_set_data_hierarchy_types
  dialog.load_ui = actual_load_ui
  dialog.db_api.get_model.return_value = mock_config_model
  return dialog


class TestUploadConfigDialog:
  # Parametrized test cases
  def test_upload_config_dialog_init(self, mocker, mock_database_api):
    # Arrange
    mock_logger = mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.logging')
    mock_dialog = mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.QDialog')
    mock_setup_ui = mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog_base.Ui_UploadConfigDialog.setupUi')
    mock_super_init = mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog_base.Ui_UploadConfigDialog.__init__')
    mock_db_api = mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.DatabaseAPI',
                               return_value=mock_database_api)
    mocker.patch.object(UploadConfigDialog, 'config_reloaded', new_callable=mocker.PropertyMock)
    mocker.patch.object(UploadConfigDialog, 'numParallelComboBox', create=True)
    mocker.patch.object(UploadConfigDialog, 'data_hierarchy_types', create=True)
    mocker.patch.object(UploadConfigDialog, 'buttonBox', create=True)
    mock_set_data_hierarchy_types = mocker.patch(
      'pasta_eln.GUI.dataverse.upload_config_dialog.UploadConfigDialog.set_data_hierarchy_types')
    mock_load_ui = mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.UploadConfigDialog.load_ui')

    # Act
    dialog = UploadConfigDialog()

    # Assert
    # Assertions to verify that the dialog has been initialized correctly
    mock_super_init.assert_called_once_with()
    mock_logger.getLogger.assert_called_once_with('pasta_eln.GUI.dataverse.upload_config_dialog.UploadConfigDialog')
    mock_dialog.assert_called_once_with()
    assert dialog.instance == mock_dialog.return_value, "Dialog instance should be set to the mock dialog"
    mock_setup_ui.assert_called_once_with(dialog.instance)
    mock_db_api.assert_called_once_with()
    mock_set_data_hierarchy_types.assert_called_once_with()
    mock_load_ui.assert_called_once_with()
    dialog.instance.setWindowModality.assert_called_once_with(QtCore.Qt.ApplicationModal)
    dialog.numParallelComboBox.addItems.assert_called_once()  # Mock the addItems
    dialog.numParallelComboBox.setCurrentIndex.assert_called_once_with(2)
    dialog.numParallelComboBox.currentTextChanged[str].connect.assert_called_once()
    dialog.buttonBox.button.assert_called_once_with(QDialogButtonBox.Save)
    dialog.buttonBox.button.return_value.clicked.connect.assert_called_once_with(dialog.save_ui)

  @pytest.mark.parametrize(
    "config_doc_id, data_hierarchy_types, parallel_uploads_count, projects_items_layout_count, expected_check_states", [
      # Test ID: Success-Path-1
      ('config-id-1', ['Type1', 'Type2'], 3, 2, [True, True]),
      # Test ID: Success-Path-2
      ('config-id-2', ['Type3'], 1, 3, [False]),
      # Add more test cases as needed
    ], ids=["Success-Path-1", "Success-Path-2"])
  def test_load_ui_success_path(self, mocker, mock_dialog, mock_config_model, config_doc_id,
                                data_hierarchy_types, parallel_uploads_count, projects_items_layout_count,
                                expected_check_states):
    # Arrange
    mock_config_model.project_upload_items = dict(zip(data_hierarchy_types, expected_check_states))
    mock_config_model.parallel_uploads_count = parallel_uploads_count
    mock_dialog.config_model = None
    mock_dialog.data_hierarchy_types = data_hierarchy_types
    mock_dialog.db_api.config_doc_id = config_doc_id
    mock_dialog.projectItemsVerticalLayout.count.return_value = projects_items_layout_count
    mock_check_box = mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.QCheckBox')

    # Act
    mock_dialog.load_ui(mock_dialog)

    # Assert
    mock_dialog.logger.info.assert_called_once_with("Loading data and initializing UI...")
    mock_dialog.db_api.get_model.assert_called_once_with(config_doc_id, ConfigModel)
    assert mock_dialog.numParallelComboBox.setCurrentText.called_once_with(str(parallel_uploads_count))
    for pos in range(projects_items_layout_count):
      mock_dialog.projectItemsVerticalLayout.itemAt.assert_any_call(pos)
      mock_dialog.projectItemsVerticalLayout.itemAt.return_value.widget.return_value.setParent.assert_any_call(None)
    for i, data_type in enumerate(data_hierarchy_types):
      mock_check_box.assert_any_call(text=data_type, parent=mock_dialog.instance,
                                     checkState=QtCore.Qt.Checked if expected_check_states[i] else QtCore.Qt.Unchecked)
      mock_dialog.projectItemsVerticalLayout.addWidget.assert_any_call(mock_check_box.return_value)
      mock_check_box.return_value.stateChanged.connect.assert_called()

  # Parametrized test for error cases
  @pytest.mark.parametrize("config_doc_id, error_message", [
    # Test ID: Error-Case-1
    ('config-id-1', "Failed to load config model!"),
    # Add more test cases as needed
  ], ids=["Error-Case-1"])
  def test_load_ui_error_cases(self, mock_dialog, mock_config_model, config_doc_id, error_message):
    # Arrange
    mock_dialog.db_api.get_model.return_value = None
    mock_dialog.db_api.config_doc_id = config_doc_id

    # Act
    mock_dialog.load_ui(mock_dialog)

    # Assert
    mock_dialog.db_api.get_model.assert_called_once_with(config_doc_id, ConfigModel)
    mock_dialog.logger.error.assert_called_once_with(error_message)

  # Parametrized test cases
  @pytest.mark.parametrize("test_id, data_hierarchy, expected_result", [
    # Success path tests
    ("SuccessCase_1", ["x0", "x3", "x4"], ["X3", "X4", "Unidentified"]),
    ("SuccessCase_2", ["x1", "x5", "x6"], ["X5", "X6", "Unidentified"]),
    ("SuccessCase_3", ["x2", "x7", "x8"], ["X7", "X8", "Unidentified"]),

    # Edge cases
    ("EdgeCase_1", [], ["Unidentified"]),  # Empty data hierarchy
    ("EdgeCase_2", ["x0", "x1", "x2"], ["Unidentified"]),  # Only excluded types
    ("EdgeCase_3", None, []),  # None as data hierarchy

    # Error cases
    # Assuming that the method should handle unexpected data types
    ("ErrorCase_1", ["", "  ", None], ["Unidentified"]),  # Empty strings and None in data hierarchy
  ])
  def test_set_data_hierarchy_types(self, mock_dialog, test_id, data_hierarchy, expected_result):
    # Arrange
    mock_dialog.db_api.get_data_hierarchy.return_value = data_hierarchy

    # Act
    mock_dialog.set_data_hierarchy_types(mock_dialog)

    # Assert
    assert mock_dialog.data_hierarchy_types == expected_result, f"Failed test case {test_id}"

  @pytest.mark.parametrize(
    "state, project_item_name, expected",
    [
      (QtCore.Qt.Checked, "Item1", True),
      (QtCore.Qt.Unchecked, "Item2", False),
      (QtCore.Qt.Unchecked, "Item5", False),
      # Edge cases could include unusual but valid project item names
      (QtCore.Qt.Checked, "", True),
      (QtCore.Qt.Checked, " ", True),
      # Error cases are not applicable here as the function does not handle errors
    ], ids=[
      "success-path-checked",
      "success-path-unchecked1",
      "success-path-unchecked2",
      "edge-case-empty-string",
      "edge-case-space"
    ]
  )
  def test_check_box_changed_callback(self, mock_dialog, mock_config_model, state, project_item_name, expected):
    # Arrange
    mock_config_model.project_upload_items = {}
    mock_dialog.config_model = mock_config_model

    # Act
    mock_dialog.check_box_changed_callback(state, project_item_name)

    # Assert
    assert (mock_config_model.project_upload_items.get(project_item_name) == expected
            ), "Test failed for check_box_changed_callback"

  @pytest.mark.parametrize(
    "test_id, setup_logger, expected_log_info, expected_log_error, expect_emit", [
      # Success path test with realistic test values
      ("success_case_1", "Saving config model...", "Saving config model...", None, True),

      # Error case: config_model is None
      (
          "error_no_config_model", "Failed to load config model!", None, "Failed to load config model!", False),
    ])
  def test_save_ui(self, mock_dialog, mock_config_model, test_id, setup_logger, expected_log_info, expected_log_error,
                   expect_emit):
    # Arrange
    mock_dialog.config_model = None if test_id == "error_no_config_model" else mock_config_model

    # Act
    mock_dialog.save_ui()

    # Assert
    mock_dialog.logger.info.assert_called_with("Saving config model...")
    if expected_log_info:
      mock_dialog.logger.info.assert_called_with(expected_log_info)
    if expected_log_error:
      mock_dialog.logger.error.assert_called_with(expected_log_error)
    if expect_emit:
      mock_dialog.config_reloaded.emit.assert_called_once()
    else:
      mock_dialog.config_reloaded.emit.assert_not_called()
    if mock_dialog.config_model:
      mock_dialog.db_api.update_model_document.assert_called_with(mock_dialog.config_model)
    else:
      mock_dialog.db_api.update_model_document.assert_not_called()

  @pytest.mark.parametrize("test_id", [
    ("success_case_1")
  ])
  def test_show(self, test_id, mock_dialog):
    # Arrange

    # Act
    mock_dialog.show()

    # Assert
    mock_dialog.instance.show.assert_called_once()
