#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_primitive_data_type_class.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QBoxLayout, QFrame, QPushButton, QVBoxLayout
from _pytest.mark import param

from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.primitive_data_type_class import PrimitiveDataTypeClass


@pytest.fixture
def data_context():
  context = MagicMock(spec=DataTypeClassContext)
  context.main_vertical_layout = MagicMock(spec=QVBoxLayout)
  context.meta_field = {
    'typeName': 'testType',
    'value': 'testValue',
    'valueTemplate': ['templateValue'],
    'multiple': False
  }
  context.add_push_button = MagicMock(spec=QPushButton)
  context.parent_frame = MagicMock(spec=QFrame)
  return context


@pytest.fixture
def mock_primitive_data_type_class(mocker, data_context):
  mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.logging.getLogger")
  return PrimitiveDataTypeClass(data_context)


class TestPrimitiveDataTypeClass:

  def test_init_success(self, mocker, data_context):
    # Arrange
    mock_get_logger = mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.logging.getLogger")
    # Act
    instance = PrimitiveDataTypeClass(data_context)

    # Assert
    mock_get_logger.assert_called_with("pasta_eln.GUI.dataverse.primitive_data_type_class.PrimitiveDataTypeClass")
    assert isinstance(instance, PrimitiveDataTypeClass)
    assert instance.context == data_context
    assert instance.logger == mock_get_logger.return_value

  @pytest.mark.parametrize(
    "context, expected_exception",
    [
      (None, TypeError),
      # Add more edge cases if needed
    ],
    ids=[
      "none_context",
      # Add more unique IDs for each test case
    ]
  )
  def test_init_edge_cases(self, context, expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
      PrimitiveDataTypeClass(context)

  @pytest.mark.parametrize(
    "context, expected_exception",
    [
      ("invalid_context", TypeError),
      # Add more error cases if needed
    ],
    ids=[
      "string_context",
      # Add more unique IDs for each test case
    ]
  )
  def test_init_error_cases(self, context, expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
      PrimitiveDataTypeClass(context)

  @pytest.mark.parametrize(
    "meta_field, expected_calls",
    [
      # Success path with single value
      (
          {'value': 'test_value', 'typeName': 'test_type', 'valueTemplate': 'template'},
          [("test_type", "test_value", "template", False)]
      ),
      # Success path with multiple values
      (
          {'value': ['value1', 'value2'], 'typeName': 'test_type', 'valueTemplate': ['template1', 'template2'],
           'multiple': True},
          [("test_type", "value1", "template1"), ("test_type", "value2", "template1")]
      ),
      # Edge case with empty value list
      (
          {'value': [], 'typeName': 'test_type', 'valueTemplate': ['template1'], 'multiple': True},
          [("test_type", "", "template1")]
      ),
      # Edge case with no valueTemplate
      (
          {'value': 'test_value', 'typeName': 'test_type'},
          [("test_type", "test_value", "", False)]
      ),
      # Error case with non-list value for multiple
      (
          {'value': 'test_value', 'typeName': 'test_type', 'valueTemplate': 'template', 'multiple': True},
          [("test_type", "test_value", "template", False)]
      ),
    ],
    ids=[
      "single_value",
      "multiple_values",
      "empty_value_list",
      "no_value_template",
      "non_list_value_for_multiple"
    ]
  )
  def test_populate_primitive_entry(self, mocker, mock_primitive_data_type_class, meta_field, expected_calls):
    # Arrange
    mock_primitive_data_type_class.populate_primitive_horizontal_layout = MagicMock()
    mock_qv_box_layout = mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.QVBoxLayout")
    mock_primitive_data_type_class.context.meta_field = meta_field

    # Act
    mock_primitive_data_type_class.populate_primitive_entry()

    # Assert
    mock_primitive_data_type_class.logger.info.assert_called_once_with(
      "Populating new entry of type primitive, name: %s", meta_field.get('typeName'))
    mock_qv_box_layout.assert_called_once()
    mock_qv_box_layout.return_value.setObjectName.assert_called_once_with("primitiveVerticalLayout")
    assert mock_primitive_data_type_class.populate_primitive_horizontal_layout.call_count == len(expected_calls)
    for call, expected in zip(mock_primitive_data_type_class.populate_primitive_horizontal_layout.call_args_list,
                              expected_calls):
      expected = (mock_qv_box_layout.return_value,) + expected
      mock_primitive_data_type_class.populate_primitive_horizontal_layout.assert_any_call(*expected)
    mock_primitive_data_type_class.context.main_vertical_layout.addLayout.assert_called_once_with(
      mock_qv_box_layout.return_value)

  @pytest.mark.parametrize("meta_field, widget_texts, expected_value", [
    # Happy path: single value
    ({"typeName": "testType", "typeClass": "testClass", "multiple": False, "value": []}, ["Test Value"], "Test Value"),
    # Happy path: multiple values
    ({"typeName": "testType", "typeClass": "testClass", "multiple": True, "value": []}, ["Value 1", "Value 2"],
     ["Value 1", "Value 2"]),
    # Edge case: single value with "No Value"
    ({"typeName": "testType", "typeClass": "testClass", "multiple": False, "value": []}, ["No Value"], ""),
    # Edge case: multiple values with "No Value"
    ({"typeName": "testType", "typeClass": "testClass", "multiple": True, "value": []}, ["No Value", "Value 2"],
     ["Value 2"]),
    # Error case: primitive_vertical_layout is None
    ({"typeName": "testType", "typeClass": "testClass", "multiple": False, "value": []}, None, None),
  ], ids=[
    "single_value",
    "multiple_values",
    "single_value_no_value",
    "multiple_values_with_no_value",
    "primitive_vertical_layout_none"
  ])
  def test_save_modifications(self, mocker, mock_primitive_data_type_class, data_context, meta_field, widget_texts,
                              expected_value):
    # Arrange
    mock_get_primitive_line_edit_text_value = mocker.patch(
      "pasta_eln.GUI.dataverse.primitive_data_type_class.get_primitive_line_edit_text_value")
    data_context.meta_field = meta_field
    primitive_vertical_layout = MagicMock(spec=QVBoxLayout) if widget_texts is not None else None
    if primitive_vertical_layout:
      primitive_vertical_layout.count.return_value = len(widget_texts)
      mock_get_primitive_line_edit_text_value.side_effect = widget_texts
      data_context.main_vertical_layout.findChild.return_value = primitive_vertical_layout
    else:
      data_context.main_vertical_layout.findChild.return_value = None

    # Act
    mock_primitive_data_type_class.save_modifications()

    # Assert
    mock_primitive_data_type_class.context.main_vertical_layout.findChild.assert_called_once_with(QVBoxLayout,
                                                                                                  "primitiveVerticalLayout")
    if widget_texts is not None:
      if meta_field['multiple']:
        primitive_vertical_layout.count.assert_called_once()
        assert data_context.meta_field['value'] == expected_value
      else:
        assert data_context.meta_field['value'] == expected_value
    else:
      assert data_context.meta_field['value'] == []
      if primitive_vertical_layout:
        primitive_vertical_layout.logger.error.assert_called_once_with("Failed to find primitiveVerticalLayout!")

  @pytest.mark.parametrize(
    "layout_exists, layout_type, value_template, type_name, expected_log_call",
    [
      # Happy path tests
      (True, QVBoxLayout, ["template1"], "type1", None),
      (True, QVBoxLayout, ["template2"], "type2", None),

      # Edge cases
      (True, QVBoxLayout, [""], "", None),
      (True, QVBoxLayout, [], "", None),

      # Error cases
      (False, QVBoxLayout, ["template1"], "type1", "Failed to find primitiveVerticalLayout!"),
      (True, QBoxLayout, ["template1"], "type1", "Failed to find primitiveVerticalLayout!"),
    ],
    ids=[
      "happy_path_template1_type1",
      "happy_path_template2_type2",
      "edge_case_empty_template_empty_type",
      "edge_case_no_template_empty_type",
      "error_case_layout_not_found",
      "error_case_wrong_layout_type",
    ]
  )
  def test_add_new_entry(self, mock_primitive_data_type_class, layout_exists, layout_type, value_template, type_name,
                         expected_log_call):

    # Arrange
    mock_primitive_data_type_class.populate_primitive_horizontal_layout = MagicMock()
    if layout_exists:
      layout = MagicMock(spec=layout_type)
      mock_primitive_data_type_class.context.main_vertical_layout.findChild.return_value = layout
    else:
      mock_primitive_data_type_class.context.main_vertical_layout.findChild.return_value = None
    mock_primitive_data_type_class.context.meta_field = {'valueTemplate': value_template, 'typeName': type_name}

    # Act
    mock_primitive_data_type_class.add_new_entry()

    # Assert
    if expected_log_call:
      mock_primitive_data_type_class.logger.error.assert_called_once_with(expected_log_call)
      mock_primitive_data_type_class.populate_primitive_horizontal_layout.assert_not_called()
    else:
      mock_primitive_data_type_class.logger.error.assert_not_called()
      mock_primitive_data_type_class.populate_primitive_horizontal_layout.assert_called_once_with(
        mock_primitive_data_type_class.context.main_vertical_layout.findChild.return_value,
        type_name,
        "",
        value_template[0] if value_template else ""
      )

  @pytest.mark.parametrize(
    "meta_field, expected_disabled",
    [
      param({"multiple": False}, True, id="multiple_false"),
      param({"multiple": True}, False, id="multiple_true"),
      param({}, True, id="multiple_missing"),
    ],
    ids=lambda x: x[-1]
  )
  def test_populate_entry(self, mock_primitive_data_type_class, meta_field, expected_disabled):
    # Arrange
    mock_primitive_data_type_class.populate_primitive_entry = MagicMock()
    mock_primitive_data_type_class.context.meta_field = meta_field

    # Act
    mock_primitive_data_type_class.populate_entry()

    # Assert
    if meta_field.get('multiple'):
      mock_primitive_data_type_class.context.add_push_button.setDisabled.assert_not_called()
    else:
      mock_primitive_data_type_class.context.add_push_button.setDisabled.assert_called_once_with(expected_disabled)
    mock_primitive_data_type_class.populate_primitive_entry.assert_called_once()

  @pytest.mark.parametrize(
    "meta_field",
    [
      param({"multiple": None}, id="multiple_none"),
      param({"multiple": "unexpected_string"}, id="multiple_unexpected_string"),
    ],
    ids=lambda param: param[-1]
  )
  def test_populate_entry_edge_cases(self, mock_primitive_data_type_class, meta_field):
    # Arrange
    mock_primitive_data_type_class.populate_primitive_entry = MagicMock()
    mock_primitive_data_type_class.context.meta_field = meta_field

    # Act
    mock_primitive_data_type_class.populate_entry()

    # Assert
    if meta_field.get('multiple'):
      mock_primitive_data_type_class.context.add_push_button.setDisabled.assert_not_called()
    else:
      mock_primitive_data_type_class.context.add_push_button.setDisabled.assert_called_once_with(True)
    mock_primitive_data_type_class.populate_primitive_entry.assert_called_once()

  @pytest.mark.parametrize(
    "meta_field",
    [
      param({"multiple": 123}, id="multiple_integer"),
      param({"multiple": []}, id="multiple_list"),
      param({"multiple": {}}, id="multiple_dict"),
    ],
    ids=lambda param: param[-1]
  )
  def test_populate_entry_error_cases(self, mock_primitive_data_type_class, meta_field):
    # Arrange
    mock_primitive_data_type_class.populate_primitive_entry = MagicMock()
    mock_primitive_data_type_class.context.meta_field = meta_field

    # Act
    mock_primitive_data_type_class.populate_entry()

    # Assert
    if meta_field.get('multiple'):
      mock_primitive_data_type_class.context.add_push_button.setDisabled.assert_not_called()
    else:
      mock_primitive_data_type_class.context.add_push_button.setDisabled.assert_called_once_with(True)
    mock_primitive_data_type_class.populate_primitive_entry.assert_called_once()

  @pytest.mark.parametrize(
    "type_name, type_value, type_value_template, enable_delete_button, expected_widget_type",
    [
      param("datetime", "2023-10-01T12:00:00", "2023-10-01T12:00:00", True, "QDateTimeEdit",
            id="success_path_datetime"),
      param("string", "test_value", "default_value", True, "QLineEdit", id="success_path_string"),
      param("datetime", "2023-10-01T12:00:00", "2023-10-01T12:00:00", False, "QDateTimeEdit",
            id="disable_delete_button"),
      param("string", "", "", True, "QLineEdit", id="empty_string_value"),
      param("datetime", "", "", True, "QDateTimeEdit", id="empty_datetime_value"),
    ],
    ids=lambda x: x[-1]
  )
  def test_populate_primitive_horizontal_layout(self, mocker, mock_primitive_data_type_class, type_name, type_value,
                                                type_value_template,
                                                enable_delete_button, expected_widget_type):
    # Arrange
    mock_qh_box_layout = mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.QHBoxLayout")
    mock_is_date_time_type = mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.is_date_time_type",
                                          return_value='date' in type_name or 'time' in type_name)
    mock_create_date_time_widget = mocker.patch(
      "pasta_eln.GUI.dataverse.primitive_data_type_class.create_date_time_widget")
    mock_add_clear_button = mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.add_clear_button")
    mock_add_delete_button = mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.add_delete_button")
    mock_create_line_edit = mocker.patch("pasta_eln.GUI.dataverse.primitive_data_type_class.create_line_edit")
    mock_new_primitive_entry_layout = MagicMock(spec=QBoxLayout)

    # Act
    mock_primitive_data_type_class.populate_primitive_horizontal_layout(mock_new_primitive_entry_layout,
                                                                        type_name,
                                                                        type_value,
                                                                        type_value_template,
                                                                        enable_delete_button)

    # Assert
    mock_qh_box_layout.assert_called_once()
    mock_qh_box_layout.return_value.setObjectName.assert_called_once_with("primitiveHorizontalLayout")
    mock_new_primitive_entry_layout.addLayout.assert_called_once_with(mock_qh_box_layout.return_value)
    mock_is_date_time_type.assert_called_once_with(type_name)
    mock_qh_box_layout.return_value.addWidget.assert_called_once_with(
      mock_create_date_time_widget.return_value if mock_is_date_time_type.return_value else mock_create_line_edit.return_value
    )
    mock_add_clear_button.assert_called_once_with(mock_primitive_data_type_class.context.parent_frame,
                                                  mock_qh_box_layout.return_value)
    mock_add_delete_button.assert_called_once_with(mock_primitive_data_type_class.context.parent_frame,
                                                   mock_qh_box_layout.return_value, enable_delete_button)
