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
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFrame

from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName
from pasta_eln.GUI.dataverse.edit_metadata_dialog import EditMetadataDialog
from pasta_eln.GUI.dataverse.metadata_frame_base import MetadataFrame
from pasta_eln.dataverse.config_model import ConfigModel


class MockComboBox:
  def __init__(self):
    self.items = []
    self.visible = True

  def hide(self):
    self.visible = False

  def show(self):
    self.visible = True

  def clear(self):
    self.items.clear()

  def addItem(self, display_name, userData=None):
    self.items.append((display_name, userData))

  def addItems(self, items):
    self.items.extend(items)


# Mocking the dependencies that are not directly related to the EditMetadataDialog
# to isolate the class for testing
@pytest.fixture
def mock_dependencies(mocker):
  with patch("pasta_eln.GUI.dataverse.edit_metadata_dialog.DatabaseAPI") as mock_db_api, \
      patch("pasta_eln.GUI.dataverse.edit_metadata_dialog.QDialog") as mock_qdialog, \
      patch(
        "pasta_eln.GUI.dataverse.edit_metadata_dialog.EditMetadataSummaryDialog") as mock_edit_metadata_summary_dialog, \
      patch("pasta_eln.GUI.dataverse.edit_metadata_dialog.Ui_EditMetadataDialog.setupUi") as mock_setup_ui:
    mocker.patch("pasta_eln.GUI.dataverse.edit_metadata_dialog.logging.getLogger")
    mocker.patch.object(EditMetadataDialog, "metadataBlockComboBox", create=True)
    mocker.patch.object(EditMetadataDialog, "typesComboBox", create=True)
    mocker.patch.object(EditMetadataDialog, "minimalFullComboBox", create=True)
    mocker.patch.object(EditMetadataDialog, "buttonBox", create=True)
    mocker.patch.object(EditMetadataDialog, "licenseNameLineEdit", create=True)
    mocker.patch.object(EditMetadataDialog, "licenseURLLineEdit", create=True)
    mocker.patch.object(EditMetadataDialog, "primitive_compound_frame", create=True)
    mocker.patch.object(EditMetadataDialog, "controlled_vocab_frame", create=True)
    mocker.patch.object(EditMetadataDialog, "metadataScrollVerticalLayout", create=True)
    mock_db_api_instance = mock_db_api.return_value
    mock_db_api_instance.get_model.return_value = MagicMock(
      metadata={'datasetVersion': {'metadataBlocks': {}, 'license': {'name': '', 'uri': ''}}})
    yield {
      "db_api": mock_db_api_instance,
      "qdialog": mock_qdialog,
      "setup_ui": mock_setup_ui,
      "edit_metadata_summary_dialog": mock_edit_metadata_summary_dialog
    }


@pytest.fixture
def mock_edit_metadata_dialog(mock_dependencies):
  current_path = realpath(join(getcwd(), dirname(__file__)))
  with open(join(current_path, "..//..//pasta_eln//dataverse", "dataset-create-new-all-default-fields.json"),
            encoding="utf-8") as config_file:
    file_data = config_file.read()
    config = ConfigModel(_id=123456789, metadata=json.loads(file_data))
  mock_dependencies['db_api'].get_model.return_value = config
  return EditMetadataDialog()


class TestDataverseEditMetadataDialog:
  # Parametrized test for the __init__ method
  @pytest.mark.parametrize("test_id, metadata_blocks, expected_metadata_types", [
    ("SuccessCase_01",
     {'block1': {'displayName': 'Block 1', 'fields': [{'typeName': 'type1', 'typeClass': 'primitive'}]}},
     {'Block 1': [{'name': 'type1', 'displayName': 'Type1'}]}),
    ("EdgeCase_01", {}, {})
  ])
  def test_init(self, mocker, test_id, metadata_blocks, expected_metadata_types, mock_dependencies):
    # Arrange
    mock_copy = mocker.patch("pasta_eln.GUI.dataverse.edit_metadata_dialog.copy")
    mock_dependencies['db_api'].get_model.return_value.metadata['datasetVersion']['metadataBlocks'] = metadata_blocks
    mock_get_metadata_types = mocker.patch.object(EditMetadataDialog, "get_metadata_types",
                                                  return_value=expected_metadata_types)

    # Act
    dialog = EditMetadataDialog()

    # Assert
    assert dialog.metadata_types == expected_metadata_types
    mock_dependencies['setup_ui'].assert_called_once_with(dialog.instance)
    mock_dependencies['qdialog'].assert_called_once()
    mock_dependencies['edit_metadata_summary_dialog'].assert_called_once_with(dialog.save_config)
    mock_get_metadata_types.assert_called_once()
    mock_copy.deepcopy.assert_called_once_with(mock_dependencies['db_api'].get_model.return_value.metadata)
    dialog.instance.setWindowModality.assert_called_once_with(QtCore.Qt.ApplicationModal)
    mock_dependencies['db_api'].get_model.assert_called_once_with(dialog.db_api.config_model_id, ConfigModel)
    dialog.typesComboBox.currentTextChanged.connect.assert_called_once_with(dialog.change_metadata_type)
    dialog.metadataBlockComboBox.currentTextChanged.connect.assert_called_once_with(dialog.change_metadata_block)
    dialog.minimalFullComboBox.currentTextChanged[str].connect.assert_called_once_with(dialog.toggle_minimal_full)
    dialog.buttonBox.button.assert_called_once_with(QtWidgets.QDialogButtonBox.Save)

  # Parametrized test for the get_metadata_types method
  @pytest.mark.parametrize("test_id, metadata, expected_result", [
    ("SuccessCase_01", {'datasetVersion': {'metadataBlocks': {
      'block1': {'displayName': 'Block 1', 'fields': [{'typeName': 'type1', 'typeClass': 'primitive'}]}}}},
     {'Block 1': [{'name': 'type1', 'displayName': 'Type'}]}),
    ("SuccessCase_02", {'datasetVersion': {'metadataBlocks': {
      'block1': {'displayName': 'Block 1',
                 'fields': [{'typeName': 'type.NameRestricted', 'typeClass': 'primitive'}]}}}},
     {'Block 1': [{'name': 'type.NameRestricted', 'displayName': 'Type Name Restricted'}]}),
    ("EdgeCase_01", None, {}),
    ("EdgeCase_02", {'datasetVersion': {'metadataBlocks': {}}}, {}),
  ])
  def test_get_metadata_types(self, test_id, mocker, metadata, expected_result, mock_dependencies,
                              mock_edit_metadata_dialog):
    # Arrange
    mock_edit_metadata_dialog.metadata = metadata

    # Act
    result = mock_edit_metadata_dialog.get_metadata_types()

    # Assert
    assert result == expected_result
    mock_edit_metadata_dialog.logger.info.assert_has_calls([mocker.call('Loading metadata types mapping...'),
                                                            mocker.call('Loading metadata types mapping...')])

  # Parametrized test for the change_metadata_block method
  @pytest.mark.parametrize("test_id, new_metadata_block, metadata_types, expected_items", [
    ("SuccessCase_01", 'Block 1', {'Block 1': [{'name': 'type1', 'displayName': 'Type1'}]}, ['Type1']),
    ("EdgeCase_01", 'Block 2', {'Block 1': [{'name': 'type1', 'displayName': 'Type1'}]}, []),
    ("EdgeCase_02", None, {'Block 1': [{'name': 'type1', 'displayName': 'Type1'}]}, []),
  ])
  def test_change_metadata_block(self, test_id, new_metadata_block, metadata_types, expected_items,
                                 mock_edit_metadata_dialog):
    # Arrange
    mock_edit_metadata_dialog.metadata_types = metadata_types
    mock_edit_metadata_dialog.typesComboBox.clear = MagicMock()
    mock_edit_metadata_dialog.typesComboBox.addItem = MagicMock()

    # Act
    mock_edit_metadata_dialog.change_metadata_block(new_metadata_block)

    # Assert
    if new_metadata_block:
      assert mock_edit_metadata_dialog.typesComboBox.clear.called
      add_item_calls = [call[0][0] for call in mock_edit_metadata_dialog.typesComboBox.addItem.call_args_list]
      assert add_item_calls == expected_items

  # Parametrized test for the save_ui method
  @pytest.mark.parametrize("metadata, expected_message, test_id", [
    # Test ID: #1 - Success path with both frames and metadata
    ({"key": "value"}, "Formatted message", "Test message with both frames and metadata"),
    # Test ID: #2 - Success path with no frames but with metadata
    ({"key": "value"}, "Formatted message", "Test message with metadata but no frames"),
    # Test ID: #3 - Edge case with empty metadata and both frames
    ({}, "Empty metadata message", "Test message with empty metadata and both frames"),
    # Test ID: #4 - Error case with None as metadata (assuming get_formatted_metadata_message handles None gracefully)
    (None, "None metadata message", "Test message with None as metadata"),
  ])
  def test_save_ui(self, mocker, metadata, expected_message, test_id,
                   mock_dependencies,
                   mock_edit_metadata_dialog):
    # Arrange
    mock_edit_metadata_dialog.metadata = metadata
    mock_edit_metadata_dialog.metadata_summary_dialog = mocker.MagicMock()
    mock_edit_metadata_dialog.metadata_summary_dialog.summaryTextEdit = mocker.MagicMock()
    mock_edit_metadata_dialog.metadata_summary_dialog.summaryTextEdit.setText = mocker.MagicMock()
    mock_edit_metadata_dialog.metadata_frame = mocker.MagicMock(spec=MetadataFrame)
    mock_get_formatted = mocker.patch("pasta_eln.GUI.dataverse.edit_metadata_dialog.get_formatted_metadata_message",
                                      return_value=expected_message)

    # Act
    mock_edit_metadata_dialog.save_ui()

    # Assert
    mock_get_formatted.assert_called_once_with(metadata or {})
    mock_edit_metadata_dialog.metadata_summary_dialog.summaryTextEdit.setText.assert_called_once_with(expected_message)
    mock_edit_metadata_dialog.metadata_summary_dialog.show.assert_called_once()
    mock_edit_metadata_dialog.metadata_frame.save_modifications.assert_called_once()
    mock_edit_metadata_dialog.logger.info.assert_called_with("Saving Config Model...")

  # Success path tests with various realistic test values
  @pytest.mark.parametrize("new_metadata_type, type_class, test_id", [
    ('title', 'primitive', 'success_primitive'),
    ('author', 'compound', 'success_compound'),
    ('author', 'compound', 'success_primitive_pre_exists'),
    ('subject', 'controlledVocabulary', 'success_controlledVocabulary'),
  ])
  def test_change_metadata_type_success_path(self, mocker, mock_edit_metadata_dialog, mock_dependencies,
                                             new_metadata_type, type_class, test_id):
    # Arrange
    pre_metadata_frame = MagicMock(spec=MetadataFrame)
    pre_metadata_frame_instance = MagicMock(spec=QFrame)
    mock_edit_metadata_dialog.metadata_frame = pre_metadata_frame
    mock_edit_metadata_dialog.metadata_frame.instance = pre_metadata_frame_instance
    mock_edit_metadata_dialog.metadata = {
      'datasetVersion': {
        'metadataBlocks': {
          'citation': {
            'fields': [
              {'typeName': 'title', 'typeClass': 'primitive'},
              {'typeName': 'author', 'typeClass': 'compound'},
              {'typeName': 'subject', 'typeClass': 'controlledVocabulary'}
            ]
          }
        }
      }
    }
    mock_edit_metadata_dialog.typesComboBox.currentData.return_value = new_metadata_type
    mock_edit_metadata_dialog.metadataScrollVerticalLayout.count.return_value = 2
    mock_edit_metadata_dialog.metadata_frame_factory = mocker.MagicMock()

    # Act
    mock_edit_metadata_dialog.change_metadata_type()

    # Assert
    mock_edit_metadata_dialog.metadataScrollVerticalLayout.itemAt.assert_has_calls(
      [mocker.call(1), mocker.call().widget(), mocker.call().widget().setParent(None), mocker.call(0),
       mocker.call().widget(), mocker.call().widget().setParent(None)])
    mock_edit_metadata_dialog.logger.info.assert_has_calls(
      [mocker.call("Loading %s metadata type of class: %s...", new_metadata_type, type_class)])
    pre_metadata_frame_instance.setParent.assert_called_once_with(None)
    mock_edit_metadata_dialog.metadata_frame_factory.make_metadata_frame.assert_called_once_with(
      DataTypeClassName(type_class),
      next(f for f in mock_edit_metadata_dialog
           .metadata['datasetVersion']['metadataBlocks']['citation']['fields']
           if f['typeName'] == new_metadata_type)
    )
    assert mock_edit_metadata_dialog.metadata_frame == mock_edit_metadata_dialog.metadata_frame_factory.make_metadata_frame.return_value
    mock_edit_metadata_dialog.metadataScrollVerticalLayout.addWidget.assert_called_once_with(
      mock_edit_metadata_dialog.metadata_frame.instance)
    pre_metadata_frame.save_modifications.assert_called_once()
    pre_metadata_frame_instance.close.assert_called_once()

  # Edge cases
  @pytest.mark.parametrize("new_metadata_type, test_id", [
    ('', 'edge_empty_string'),
    (None, 'edge_none'),
  ])
  def test_change_metadata_type_edge_cases(self, mocker, mock_edit_metadata_dialog, new_metadata_type, test_id):
    # Arrange
    mock_edit_metadata_dialog.typesComboBox.currentData.return_value = new_metadata_type

    # Act
    mock_edit_metadata_dialog.change_metadata_type()

    # Assert
    mock_edit_metadata_dialog.logger.info.assert_has_calls(
      [mocker.call('Loading metadata types mapping...')]
    )

  # Error cases
  @pytest.mark.parametrize("metadata, test_id", [
    (None, 'error_no_metadata'),
    ({}, 'error_empty_metadata'),
    ({'datasetVersion': {}}, 'error_no_metadataBlocks'),
  ])
  def test_change_metadata_type_error_cases(self, mock_edit_metadata_dialog, metadata, test_id):
    # Arrange
    mock_edit_metadata_dialog.metadata = metadata

    # Act
    mock_edit_metadata_dialog.change_metadata_type()

    # Assert
    if test_id == 'error_no_metadataBlocks':
      mock_edit_metadata_dialog.logger.error.assert_not_called()
    else:
      mock_edit_metadata_dialog.logger.error.assert_called_with("Failed to load metadata model!")

  @pytest.mark.parametrize("selection, expected_types, expected_visibility, test_id", [
    # Happy path tests
    ("Minimal", [('Title', 'title'), ('Author', 'author')], False, "happy_minimal"),
    ("Full", list({'title': 'Title', 'author': 'Author', 'date': 'Date'}.keys()), True, "happy_full"),

    # Edge cases
    ("", [], False, "edge_empty_selection"),
    ("Random", [], True, "edge_random_selection"),

    # Error cases
    (None, [], True, "error_none_selection"),
    (123, [], True, "error_non_string_selection"),
  ])
  def test_toggle_minimal_full(self, mock_edit_metadata_dialog, selection, expected_types, expected_visibility,
                               test_id):
    # Arrange
    mock_edit_metadata_dialog.typesComboBox = MockComboBox()
    mock_edit_metadata_dialog.metadataBlockComboBox = MockComboBox()
    minimal_metadata = [
      {'displayName': 'Title', 'name': 'title'},
      {'displayName': 'Author', 'name': 'author'}
    ]
    metadata_types = {'title': 'Title', 'author': 'Author', 'date': 'Date'}
    mock_edit_metadata_dialog.minimal_metadata = minimal_metadata
    mock_edit_metadata_dialog.metadata_types = metadata_types

    # Act
    mock_edit_metadata_dialog.toggle_minimal_full(selection)

    # Assert
    mock_edit_metadata_dialog.logger.info.assert_called_with("Toggled to %s view...", selection)
    if selection == "Minimal":
      assert mock_edit_metadata_dialog.typesComboBox.items == expected_types
      assert mock_edit_metadata_dialog.metadataBlockComboBox.visible == expected_visibility
    elif selection == "Full":
      assert mock_edit_metadata_dialog.metadataBlockComboBox.items == expected_types
      assert mock_edit_metadata_dialog.metadataBlockComboBox.visible == expected_visibility
    else:
      # For edge and error cases, we assume the default behavior is to show the full view
      assert mock_edit_metadata_dialog.metadataBlockComboBox.visible

  @pytest.mark.parametrize("test_id, metadata_types, metadata_config, expected_license_name, expected_license_uri", [
    # Success path tests with various realistic test values
    ("SuccessCase_01", {'Type1': None, 'Type2': None},
     {'datasetVersion': {'license': {'name': 'CC0', 'uri': 'http://creativecommons.org/publicdomain/zero/1.0/'}}, },
     'CC0', 'http://creativecommons.org/publicdomain/zero/1.0/'),

    # Edge cases could include empty metadata_types or metadata_config
    ("EdgeCase_01", {}, {'datasetVersion': {'license': {'name': '', 'uri': ''}}}, '', ''),
    # Add more edge cases as needed

    # Error cases could include missing keys in metadata_config
    ("ErrorCase_01", {'Type1': None}, {}, '', ''),
    # Add more error cases as needed
  ])
  def test_load_ui(self, mocker, mock_edit_metadata_dialog, test_id, metadata_types, metadata_config,
                   expected_license_name,
                   expected_license_uri):
    # Arrange
    mock_copy = mocker.patch("pasta_eln.GUI.dataverse.edit_metadata_dialog.copy")
    mock_edit_metadata_dialog.get_metadata_types = mocker.MagicMock(return_value=metadata_types)
    mock_edit_metadata_dialog.metadata_types = metadata_types
    mock_edit_metadata_dialog.config_model = MagicMock()
    mock_edit_metadata_dialog.config_model.metadata = metadata_config
    mock_copy.deepcopy.return_value = metadata_config
    mocker.resetall()

    # Act
    mock_edit_metadata_dialog.load_ui()

    # Assert
    mock_edit_metadata_dialog.minimalFullComboBox.addItems.assert_called_once_with(["Full", "Minimal"])
    mock_edit_metadata_dialog.licenseNameLineEdit.setText.assert_called_once_with(expected_license_name)
    mock_edit_metadata_dialog.licenseURLLineEdit.setText.assert_called_once_with(expected_license_uri)

  @pytest.mark.parametrize("test_id, instance_method", [
    # Happy path tests with various realistic test values
    ("succes_path", 'show'),
  ])
  def test_show_method(self, mock_edit_metadata_dialog, test_id, instance_method):
    # Act
    mock_edit_metadata_dialog.show()

    # Assert
    getattr(mock_edit_metadata_dialog.instance, instance_method).assert_called_once()
