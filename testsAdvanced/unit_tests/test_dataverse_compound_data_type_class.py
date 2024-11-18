""" Unit tests for the compound data type class. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_compound_data_type_class.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from unittest.mock import MagicMock, call

import pytest
from PySide6.QtWidgets import QBoxLayout, QDateTimeEdit, QFrame, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout
from _pytest.mark import param

from pasta_eln.GUI.dataverse.compound_data_type_class import CompoundDataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext


@pytest.fixture
def mock_widget():
  widget = MagicMock(spec=QLineEdit)
  widget.objectName.return_value = "testLineEdit"
  widget.text.return_value = "test_value"
  return widget


@pytest.fixture
def mock_layout(mock_widget):
  layout = MagicMock(spec=QBoxLayout)
  layout.count.return_value = 1
  layout.itemAt.return_value.widget.return_value = mock_widget
  return layout


@pytest.fixture
def setup_context():
  context = MagicMock(spec=DataTypeClassContext)
  context.meta_field = {
    'valueTemplate': [{'typeName': 'date', 'value': '2023-10-01'}, {'typeName': 'text', 'value': 'Sample Text'}]}
  context.parent_frame = MagicMock(spec=QFrame)
  context.add_push_button = MagicMock(spec=QPushButton)
  context.main_vertical_layout = MagicMock(spec=QVBoxLayout)
  return context


@pytest.fixture
def mock_compound_data_type_class(mocker, setup_context):
  mocker.patch("pasta_eln.GUI.dataverse.compound_data_type_class.logging.getLogger")
  return CompoundDataTypeClass(setup_context)


class TestCompoundDataTypeClass:

  def test_init_happy_path(self, mocker):
    # Arrange
    mock_base_class_init = mocker.patch("pasta_eln.GUI.dataverse.compound_data_type_class.DataTypeClass.__init__")
    mock_context = mocker.MagicMock(spec=DataTypeClassContext)
    mock_logger = mocker.patch("pasta_eln.GUI.dataverse.compound_data_type_class.logging.getLogger")

    # Act
    instance = CompoundDataTypeClass(mock_context)

    # Assert
    mock_base_class_init.assert_called_once_with(mock_context)
    mock_logger.assert_called_once_with('pasta_eln.GUI.dataverse.compound_data_type_class.CompoundDataTypeClass')
    assert instance.logger == mock_logger.return_value

  @pytest.mark.parametrize("value_template, expected_widgets_added, expected_calls", [
    # Success path with various realistic test values
    ([
       {
         "journalVolume": {
           "typeName": "journalVolume",
           "multiple": False,
           "typeClass": "primitive",
           "value": "JournalVolume1"
         },
         "journalIssue": {
           "typeName": "journalIssue",
           "multiple": False,
           "typeClass": "primitive",
           "value": "JournalIssue1"
         },
         "journalPubDate": {
           "typeName": "journalPubDate",
           "multiple": False,
           "typeClass": "primitive",
           "value": "1008-01-01"
         }
       }
     ], [QLineEdit, QLineEdit, QDateTimeEdit], 3),
    # Edge case: empty valueTemplate
    ([{}], [], 0),
    # Edge case: valueTemplate with non-dict values
    ([{'typeName': {'typeName': 'dateTime', 'value': '2023-10-10'}}, 'invalid'], [QDateTimeEdit], 1),
    # Error case: valueTemplate with missing typeName
    ([{'typeName': {'value': '2023-10-10'}}], [], 0),
    # Error case: valueTemplate with missing value
    ([{'typeName': 'dateTime'}], [], 0),
  ], ids=["success_path", "empty_value_template", "non_dict_value", "missing_type_name", "missing_value"])
  def test_add_new_entry_parametrized(self, mocker, mock_compound_data_type_class, value_template,
                                      expected_widgets_added, expected_calls):
    # Arrange
    mock_qhbox_layout = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.QHBoxLayout')
    mock_add_clear_button = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.add_clear_button')
    mock_add_delete_button = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.add_delete_button')
    mock_create_line_edit = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.create_line_edit')
    mock_create_date_time_widget = mocker.patch(
      'pasta_eln.GUI.dataverse.compound_data_type_class.create_date_time_widget')
    mock_is_date_time_type = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.is_date_time_type')
    mock_is_date_time_type.side_effect = lambda x: x.lower() == 'dateTime' or 'date' in x.lower() or 'time' in x.lower()
    mock_create_date_time_widget.return_value = MagicMock()
    mock_create_line_edit.return_value = MagicMock()
    mock_add_clear_button.return_value = None
    mock_add_delete_button.return_value = None
    mock_compound_data_type_class.context.meta_field = {'valueTemplate': value_template}

    # Act
    mock_compound_data_type_class.add_new_entry()

    # Assert
    assert mock_create_date_time_widget.call_count + mock_create_line_edit.call_count == expected_calls
    assert mock_add_clear_button.called
    assert mock_add_delete_button.called
    if expected_calls > 0:
      mock_qhbox_layout.return_value.addWidget.assert_has_calls(
        [mocker.call(mock_create_line_edit.return_value) if w is QLineEdit else mocker.call(
          mock_create_date_time_widget.return_value) for w in expected_widgets_added]
      )
      mock_compound_data_type_class.context.main_vertical_layout.addLayout.assert_called_once_with(
        mock_qhbox_layout.return_value)

  @pytest.mark.parametrize(
    "meta_field, expected_calls",
    [
      # Success path: single value, not multiple
      param(
        {'valueTemplate': {'key': 'template'}, 'value': {'key': 'value'}, 'multiple': False},
        [call({'key': 'value'}, {'key': 'template'}, False)],
        id="single_value_not_multiple"
      ),
      # Success path: multiple values, empty list
      param(
        {'valueTemplate': [{'key': 'template'}], 'value': [], 'multiple': True},
        [call({'key': 'template'}, {'key': 'template'})],
        id="multiple_values_empty_list"
      ),
      # Happy path: multiple values, non-empty list
      param(
        {'valueTemplate': [{'key': 'template'}], 'value': [{'key': 'value1'}, {'key': 'value2'}], 'multiple': True},
        [call({'key': 'value1'}, {'key': 'template'}), call({'key': 'value2'}, {'key': 'template'})],
        id="multiple_values_non_empty_list"
      ),
      # Edge case: single value, no value provided
      param(
        {'valueTemplate': {'key': 'template'}, 'value': None, 'multiple': False},
        [call({'key': 'template'}, {'key': 'template'}, False)],
        id="single_value_no_value_provided"
      ),
      # Edge case: multiple values, no value template
      param(
        {'valueTemplate': None, 'value': [{'key': 'value1'}], 'multiple': True},
        [],
        id="multiple_values_no_value_template"
      ),
      # Error case: valueTemplate is not a list when multiple is True
      param(
        {'valueTemplate': {'key': 'template'}, 'value': [], 'multiple': True},
        [],
        id="value_template_not_list_multiple_true"
      ),
      # Error case: value is not a list when multiple is True
      param(
        {'valueTemplate': [{'key': 'template'}], 'value': {'key': 'value'}, 'multiple': True},
        [],
        id="value_not_list_multiple_true"
      ),
    ],
    ids=lambda x: x[-1]
  )
  def test_populate_entry(self, mock_compound_data_type_class, meta_field, expected_calls):
    # Arrange
    mock_compound_data_type_class.populate_compound_entry = MagicMock()
    mock_compound_data_type_class.context.meta_field = meta_field

    # Act
    mock_compound_data_type_class.populate_entry()

    # Assert
    assert mock_compound_data_type_class.context.add_push_button.setDisabled.called == (not meta_field['multiple'])
    assert mock_compound_data_type_class.populate_compound_entry.call_args_list == expected_calls

  @pytest.mark.parametrize(
    "meta_field, layout_items, expected_value, log_error_called",
    [
      # Success path: multiple is True, with valueTemplate
      (
          {'multiple': True, 'value': [1, 2, 3], 'valueTemplate': [{'key': 'value'}]},
          [MagicMock(spec=QHBoxLayout), MagicMock(spec=QHBoxLayout)],
          [],
          False
      ),
      # Success path: multiple is False, with valueTemplate
      (
          {'multiple': False, 'value': [1, 2, 3], 'valueTemplate': {'key': 'value'}},
          [MagicMock(spec=QHBoxLayout)],
          {},
          False
      ),
      # Edge case: multiple is True, no valueTemplate
      (
          {'multiple': True, 'value': [1, 2, 3]},
          [MagicMock(spec=QHBoxLayout)],
          [],
          False
      ),
      # Edge case: multiple is False, no valueTemplate
      (
          {'multiple': False, 'value': [1, 2, 3]},
          [MagicMock(spec=QHBoxLayout)],
          {},
          False
      ),
      # Error case: multiple is False, compound horizontal layout not found
      (
          {'multiple': False, 'value': [1, 2, 3]},
          [],
          {},
          True
      ),
    ],
    ids=[
      "multiple_true_with_valueTemplate",
      "multiple_false_with_valueTemplate",
      "multiple_true_no_valueTemplate",
      "multiple_false_no_valueTemplate",
      "multiple_false_layout_not_found",
    ]
  )
  def test_save_modifications(self, mock_compound_data_type_class, meta_field, layout_items, expected_value,
                              log_error_called):
    # Arrange
    main_vertical_layout = MagicMock(spec=QHBoxLayout)
    if meta_field.get('multiple'):
      main_vertical_layout.itemAt.side_effect = layout_items
    else:
      main_vertical_layout.findChild.return_value = layout_items[0] if layout_items else None

    mock_compound_data_type_class.context.meta_field = meta_field
    mock_compound_data_type_class.context.main_vertical_layout = main_vertical_layout

    # Act
    mock_compound_data_type_class.save_modifications()

    # Assert
    assert mock_compound_data_type_class.context.meta_field['value'] == expected_value
    if log_error_called:
      mock_compound_data_type_class.logger.error.assert_called_once_with("Compound horizontal layout not found")
    else:
      mock_compound_data_type_class.logger.error.assert_not_called()

  @pytest.mark.parametrize(
    "widget_text, expected_value, initial_meta_field, expected_meta_field",
    [
      ("test_value", "test_value", {}, {'test': {'value': 'test_value'}}),
      ("No Value", "", {}, {}),
      ("", "", {}, {}),
      ("test_value", "test_value", {'test': {'value': 'initial_value'}}, {'test': {'value': 'test_value'}}),
      ("test_value", "test_value", [], [{'test': {'value': 'test_value'}}]),
    ],
    ids=[
      "normal_value",
      "no_value",
      "empty_value",
      "overwrite_existing_value",
      "append_to_list"
    ]
  )
  def test_save_compound_horizontal_layout_values(self, mock_compound_data_type_class, mock_layout, widget_text,
                                                  expected_value,
                                                  initial_meta_field, expected_meta_field):
    # Arrange
    mock_compound_data_type_class.context.meta_field['value'] = initial_meta_field
    mock_layout.itemAt.return_value.widget.return_value.text.return_value = widget_text
    value_template = {'test': {'value': ''}}
    mock_compound_data_type_class.context.meta_field['valueTemplate'] = value_template

    # Act
    mock_compound_data_type_class.save_compound_horizontal_layout_values(mock_layout, value_template)

    # Assert
    assert mock_compound_data_type_class.context.meta_field['value'] == expected_meta_field

  @pytest.mark.parametrize(
    "layout_count, initial_meta_field, expected_meta_field",
    [
      (0, {}, {}),
      (0, [], []),
    ],
    ids=[
      "empty_layout_dict",
      "empty_layout_list"
    ]
  )
  def test_save_compound_horizontal_layout_values_empty_layout(self, mock_compound_data_type_class, layout_count,
                                                               initial_meta_field,
                                                               expected_meta_field):
    # Arrange
    mock_compound_data_type_class.context.meta_field['value'] = initial_meta_field
    mock_layout = MagicMock(spec=QBoxLayout)
    mock_layout.count.return_value = layout_count
    value_template = {'test': {'value': ''}}
    mock_compound_data_type_class.context.meta_field['valueTemplate'] = value_template

    # Act
    mock_compound_data_type_class.save_compound_horizontal_layout_values(mock_layout, value_template)

    # Assert
    assert mock_compound_data_type_class.context.meta_field['value'] == expected_meta_field

  @pytest.mark.parametrize(
    "initial_meta_field, expected_meta_field",
    [
      ({'value': 'string_value'}, {'test': {'value': 'test_value'}, 'value': 'string_value'}),
      (None, {'test': {'value': 'test_value'}}),
    ],
    ids=[
      "initial_value_string",
      "initial_value_none"
    ]
  )
  def test_save_compound_horizontal_layout_values_non_dict_list_initial_value(self, mock_compound_data_type_class,
                                                                              mock_layout,
                                                                              initial_meta_field, expected_meta_field):
    # Arrange
    mock_compound_data_type_class.context.meta_field['value'] = initial_meta_field
    mock_layout.itemAt.return_value.widget.return_value.text.return_value = "test_value"
    value_template = {'test': {'value': ''}}
    mock_compound_data_type_class.context.meta_field['valueTemplate'] = value_template

    # Act
    mock_compound_data_type_class.save_compound_horizontal_layout_values(mock_layout, value_template)

    # Assert
    assert mock_compound_data_type_class.context.meta_field['value'] == expected_meta_field

  @pytest.mark.parametrize(
    "compound_entry, template_entry, enable_delete_button, expected_widget_count",
    [
      # Success path test cases
      pytest.param(
        {"date": {"value": "2023-10-01T12:00:00"}},
        {"date": {"value": "2023-10-01T12:00:00"}},
        True,
        3,
        id="success_path_with_date"
      ),
      pytest.param(
        {"text": {"value": "example"}},
        {"text": {"value": "example"}},
        True,
        3,
        id="success_path_with_text"
      ),
      # Edge cases
      pytest.param(
        {},
        None,
        True,
        0,
        id="empty_compound_entry"
      ),
      pytest.param(
        {"date": {"value": "2023-10-01T12:00:00"}},
        None,
        False,
        2,
        id="no_template_entry"
      ),
      # Error cases
      pytest.param(
        {"date": {"value": "invalid-date"}},
        None,
        True,
        2,
        id="invalid_date_value"
      ),
      pytest.param(
        {"unknown_type": {"value": "example"}},
        None,
        True,
        2,
        id="unknown_type"
      ),
    ]
  )
  def test_populate_compound_entry(self, mock_compound_data_type_class, mocker, compound_entry, template_entry,
                                   enable_delete_button,
                                   expected_widget_count):
    # Arrange
    mock_is_date_time_type = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.is_date_time_type',
                                          lambda x: x == 'date')
    mock_compound_create_date_time_widget = mocker.patch(
      'pasta_eln.GUI.dataverse.compound_data_type_class.create_date_time_widget')
    mock_create_line_edit = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.create_line_edit')
    mock_add_delete_button = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.add_delete_button')
    mock_add_clear_button = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.add_clear_button')
    mock_qhbox_layout = mocker.patch('pasta_eln.GUI.dataverse.compound_data_type_class.QHBoxLayout')
    mock_qhbox_layout.return_value.count.return_value = len(compound_entry)

    # Act
    mock_compound_data_type_class.populate_compound_entry(compound_entry, template_entry, enable_delete_button)

    # Assert
    mock_qhbox_layout.assert_called_once()
    mock_qhbox_layout.return_value.setObjectName.assert_called_once_with("compoundHorizontalLayout")
    assert mock_compound_data_type_class.context.main_vertical_layout.addLayout.call_count == (
      1 if expected_widget_count > 0 else 0)
    if expected_widget_count > 0:
      mock_qhbox_layout.return_value.addWidget.call_count == expected_widget_count
      mock_add_clear_button.assert_called_once_with(mock_compound_data_type_class.context.parent_frame,
                                                    mock_qhbox_layout.return_value)
      mock_add_delete_button.assert_called_once_with(mock_compound_data_type_class.context.parent_frame,
                                                     mock_qhbox_layout.return_value, enable_delete_button)
      mock_compound_data_type_class.context.main_vertical_layout.addLayout.assert_called_once_with(
        mock_qhbox_layout.return_value)
