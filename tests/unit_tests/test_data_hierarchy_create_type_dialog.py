#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_data_hierarchy_create_type_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QMessageBox
from _pytest.mark import param

from pasta_eln.GUI.data_hierarchy.create_type_dialog import CreateTypeDialog
from pasta_eln.GUI.data_hierarchy.generic_exception import GenericException


@pytest.fixture
def type_dialog(mocker):
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.logging.getLogger')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconFontCollectionComboBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iconComboBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeDisplayedTitleLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.typeLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.iriLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.shortcutLineEdit', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.TypeDialog.buttonBox', create=True)
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QDialog')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.LookupIriAction')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.show_message')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QTAIconsSingleton',
               MagicMock(font_collections=['Font1', 'Font2']))
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog_base.Ui_TypeDialogBase.setupUi')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.DataTypeInfo')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpression')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QRegularExpressionValidator')
  mocker.patch('pasta_eln.GUI.data_hierarchy.type_dialog.QTAIconsSingleton',
               MagicMock(font_collections=['Font1', 'Font2']))
  return CreateTypeDialog(MagicMock(), MagicMock())


class TestDataHierarchyCreateTypeDialog:

  @pytest.mark.parametrize(
    "validate_type_info, data_hierarchy_types, type_info, expected_log, expected_exception, expected_message",
    [
      # Happy path: New type added
      param(True, {}, MagicMock(datatype="new_type", title="New Type"),
            "User created a new type and added to the data_hierarchy document: Datatype: {%s}, Displayed Title: {%s}",
            None, None, id="success_path_new_type"),

      # Edge case: Type already exists
      param(True, {"existing_type": MagicMock()}, MagicMock(datatype="existing_type", title="Existing Type"),
            None, None,
            "Type (datatype: existing_type displayed title: Existing Type) cannot be added since it exists in DB already....",
            id="edge_case_existing_type"),

      # Error case: Null data_hierarchy_types
      param(True, None, MagicMock(datatype="any_type", title="Any Type"),
            "Null data_hierarchy_types, erroneous app state",
            GenericException, None, id="error_case_null_data_hierarchy_types"),

      # Error case: Invalid type info
      param(False, {}, MagicMock(datatype="invalid_type", title="Invalid Type"),
            None, None, None, id="error_case_invalid_type_info"),
    ]
  )
  def test_accepted_callback(self, type_dialog, validate_type_info, data_hierarchy_types, type_info, expected_log,
                             expected_exception,
                             expected_message, request):
    # Arrange
    type_dialog.validate_type_info = MagicMock()
    type_dialog.validate_type_info.return_value = validate_type_info
    type_dialog.data_hierarchy_types = data_hierarchy_types
    type_dialog.type_info = type_info
    type_dialog.accepted_callback_parent = MagicMock()

    with patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.show_message') as mock_show_message, \
        patch('pasta_eln.GUI.data_hierarchy.create_type_dialog.generate_data_hierarchy_type',
              return_value=MagicMock()) as mock_generate_data_hierarchy_type:

      # Act
      if expected_exception:
        with pytest.raises(expected_exception):
          type_dialog.accepted_callback()
      else:
        type_dialog.accepted_callback()

      # Assert
      if expected_log:
        if expected_exception:
          type_dialog.logger.error.assert_called_with(expected_log)
        else:
          type_dialog.logger.info.assert_called_with(expected_log, type_info.datatype, type_info.title)
      else:
        type_dialog.logger.info.assert_not_called()

      if expected_message:
        mock_show_message.assert_called_once_with(expected_message, QMessageBox.Icon.Warning)
      else:
        mock_show_message.assert_not_called()

      if data_hierarchy_types is not None and validate_type_info and (
          type_info.datatype not in data_hierarchy_types or request.node.callspec.id == "success_path_new_type"):
        assert type_info.datatype in type_dialog.data_hierarchy_types
        mock_generate_data_hierarchy_type.assert_called_once_with(type_info)
        type_dialog.instance.close.assert_called_once()
        type_dialog.accepted_callback_parent.assert_called_once()
      else:
        mock_generate_data_hierarchy_type.assert_not_called()
        type_dialog.instance.close.assert_not_called()
        type_dialog.accepted_callback_parent.assert_not_called()

  @pytest.mark.parametrize(
    "mock_return_value, expected_call_count",
    [
      # Happy path test cases
      (None, 1),  # ID: happy_path_none
      ("some_value", 1),  # ID: happy_path_some_value

      # Edge cases
      (0, 1),  # ID: edge_case_zero
      ("", 1),  # ID: edge_case_empty_string

      # Error cases
      (Exception("error"), 1),  # ID: error_case_exception
    ],
    ids=[
      "success_path_none",
      "success_path_some_value",
      "edge_case_zero",
      "edge_case_empty_string",
      "error_case_exception",
    ]
  )
  def test_rejected_callback(self, type_dialog, mock_return_value, expected_call_count):
    # Arrange
    type_dialog.rejected_callback_parent.return_value = mock_return_value

    # Act
    type_dialog.rejected_callback()

    # Assert
    type_dialog.rejected_callback_parent.assert_called_once()
    assert type_dialog.rejected_callback_parent.call_count == expected_call_count

  @pytest.mark.parametrize(
    "data_hierarchy_types, expected",
    [
      # Success path tests
      param({"type1": "value1", "type2": "value2"}, {"type1": "value1", "type2": "value2"},
            id="success_path_multiple_types"),
      param({"type1": 123, "type2": [1, 2, 3]}, {"type1": 123, "type2": [1, 2, 3]}, id="success_path_mixed_values"),
      param({"type1": None}, {"type1": None}, id="success_path_none_value"),

      # Edge cases
      param({}, {}, id="edge_case_empty_dict"),
      param({"": "empty_key"}, {"": "empty_key"}, id="edge_case_empty_string_key"),
      param({"type1": ""}, {"type1": ""}, id="edge_case_empty_string_value"),

      # Error cases
      param(None, None, id="error_case_none_input"),
    ],
    ids=lambda x: x[2]
  )
  def test_set_data_hierarchy_types(self, type_dialog, data_hierarchy_types, expected):
    # Arrange

    # Act
    type_dialog.set_data_hierarchy_types(data_hierarchy_types)

    # Assert
    assert type_dialog.data_hierarchy_types == expected
