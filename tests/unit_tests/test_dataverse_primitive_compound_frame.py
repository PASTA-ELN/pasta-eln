#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_primitive_compound_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import patch

import pytest
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QBoxLayout

from pasta_eln.GUI.dataverse.primitive_compound_frame import PrimitiveCompoundFrame


# Mock the Qt dependencies to avoid issues with the actual GUI components during testing
@pytest.fixture
def qtbot(mocker):
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QFrame')
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QLineEdit')
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QDateTimeEdit')
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QVBoxLayout')
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QHBoxLayout')
  mocker.patch.object(PrimitiveCompoundFrame, 'addPushButton', create=True)
  mocker.patch.object(PrimitiveCompoundFrame, 'mainVerticalLayout', create=True)


# Fixture to create a PrimitiveCompoundFrame instance with a mocked parent
@pytest.fixture
def primitive_compound_frame(qtbot, mocker):
  mocker.patch(
    'pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi')
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.logging.getLogger')
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.add_clear_button')
  mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.add_delete_button')
  type_field = {
    'typeClass': 'primitive',
    'multiple': False,
    'typeName': 'testType',
    'value': 'testValue',
    'valueTemplate': 'testTemplate'
  }
  return PrimitiveCompoundFrame(type_field)


def create_mock_line_edit(mocker, name, text):
  line_edit = mocker.MagicMock()
  line_edit.objectName.return_value = f"{name}LineEdit"
  line_edit.text.return_value = text
  line_edit.widget.return_value = line_edit
  return line_edit


class TestDataversePrimitiveCompoundFrame:
  # Parametrized test for __init__ method happy path
  # Parametrized test for the happy path of PrimitiveCompoundFrame initialization
  @pytest.mark.parametrize("type_field, expected_logger_name", [
    # Test ID: #1
    (
        {'typeClass': 'primitive', 'multiple': True, 'typeName': 'testType', 'value': [],
         'valueTemplate': ['testTemplate']},
        "pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame"
    ),
    # Test ID: #2
    (
        {'typeClass': 'compound', 'multiple': False, 'typeName': 'testType', 'value': {},
         'valueTemplate': {'testType': {'value': 'testValue'}}},
        "pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame"
    ),
  ], ids=["happy-path-primitive-multiple", "happy-path-compound-single"])
  def test_primitive_compound_frame_init(self, mocker, qtbot, type_field, expected_logger_name):
    # Arrange
    mock_load_ui = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.load_ui')
    with patch(
        'pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi') as mock_setup_ui:
      # Act
      frame = PrimitiveCompoundFrame(type_field)

      # Assert
      assert frame.logger.name == expected_logger_name
      mock_setup_ui.assert_called_once()
      mock_load_ui.assert_called_once()

  @pytest.mark.parametrize("meta_field, expected_disabled, expected_calls, test_id", [
    # Happy path tests
    ({"typeClass": "primitive", "multiple": False}, True, "primitive_entry", "success_primitive_single"),
    ({"typeClass": "primitive", "multiple": True}, False, "primitive_entry", "success_primitive_multiple"),
    ({"typeClass": "compound", "multiple": True, "value": [], "valueTemplate": [{}]}, False, "compound_entry_empty",
     "success_compound_multiple_empty"),
    ({"typeClass": "compound", "multiple": True, "value": [{}], "valueTemplate": [{}]}, False, "compound_entry_filled",
     "success_compound_multiple_filled"),
    ({"typeClass": "compound", "multiple": False, "value": {}, "valueTemplate": {}}, True, "compound_entry_single",
     "success_compound_single"),

    # Edge cases
    ({"typeClass": "compound", "multiple": False, "value": None, "valueTemplate": {}}, True, "compound_entry_none",
     "edge_compound_none_value"),

    # Error cases
    ({"typeClass": "unknown"}, None, "error", "error_unknown_typeClass"),
    ({"typeClass": "compound", "multiple": False, "value": None, "valueTemplate": None}, True, "compound_entry_single",
     "error_compound_value_value_template_none"),
    ({"typeClass": "compound", "multiple": False}, True, "compound_entry_single",
     "error_compound_value_value_template_missing"),
    ({}, False, "empty_meta_field",
     "error_empty_meta_field"),
  ])
  def test_load_ui(self, mocker, primitive_compound_frame, meta_field, expected_disabled, expected_calls, test_id):
    # Arrange
    mocker.resetall()
    primitive_compound_frame.meta_field = meta_field
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.populate_primitive_entry')
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.populate_compound_entry')

    # Act
    primitive_compound_frame.load_ui()

    # Assert
    primitive_compound_frame.logger.info.assert_called_with("Loading UI for %s", meta_field)
    if expected_disabled is not None and expected_disabled:
      primitive_compound_frame.addPushButton.setDisabled.assert_called_with(expected_disabled)
    if "primitive_entry" in expected_calls:
      primitive_compound_frame.populate_primitive_entry.assert_called
    if "compound_entry_empty" in expected_calls:
      primitive_compound_frame.populate_compound_entry.assert_called_with({}, {})
    if "compound_entry_filled" in expected_calls:
      primitive_compound_frame.populate_compound_entry.assert_called_with({}, {})
    if "compound_entry_single" in expected_calls:
      primitive_compound_frame.populate_compound_entry.assert_called_with(meta_field.get('value'),
                                                                          meta_field.get('valueTemplate'), False)
    if "error" in expected_calls:
      primitive_compound_frame.logger.error.assert_called_with("Unknown typeClass: %s", 'unknown')

  # Parametrized test for the add_new_entry method
  @pytest.mark.parametrize("meta_field, expected_error_log", [
    # Test ID: #3
    (
        {'typeClass': 'primitive', 'multiple': False, 'typeName': 'testType', 'value': 'testValue',
         'valueTemplate': ['testTemplate']},
        'Add operation not supported for non-multiple entries'
    ),
    # Test ID: #4
    (
        {'typeClass': 'unknown', 'multiple': True, 'typeName': 'testType', 'value': [],
         'valueTemplate': ['testTemplate']},
        ('Unknown type class: %s', 'unknown')
    ),
  ], ids=["error-primitive-multiple-false", "error-unknown-typeclass"])
  def test_add_new_entry_errors(self, mocker, primitive_compound_frame, meta_field, expected_error_log):
    # Arrange
    primitive_compound_frame.meta_field = meta_field
    primitive_compound_frame.logger.error = mocker.MagicMock()

    # Act
    primitive_compound_frame.add_new_entry()
    # Assert
    if isinstance(expected_error_log, str):
      primitive_compound_frame.logger.error.assert_called_with(expected_error_log)
    else:
      primitive_compound_frame.logger.error.assert_called_with(*expected_error_log)

  # Parametrized test case for the add_delete_button method

  @pytest.mark.parametrize(
    "parent_layout, expected_exception",
    [
      (None, AttributeError),  # error case: parent is None
    ],
    ids=["parent_none"]
  )
  def test_add_delete_button_with_invalid_parent(self, primitive_compound_frame, qtbot, mocker, parent_layout,
                                                 expected_exception):
    # Arrange
    mock_self = mocker.MagicMock()
    mock_self.instance = mocker.MagicMock()

    # Act / Assert
    with pytest.raises(expected_exception):
      primitive_compound_frame.add_delete_button(parent_layout)

  @pytest.mark.parametrize(
    "test_id, type_name, type_value, template_value, expected_placeholder, expected_tooltip, expected_object_name", [
      (
          "happy-1", "Name", "John Doe", "John Smith", "Enter the Name here.",
          "Enter the Name value here. e.g. John Smith",
          "NameLineEdit"),
      ("happy-2", "Date", "", "2023-01-01", "Enter the Date here.", "Enter the Date value here. e.g. 2023-01-01",
       "DateLineEdit"),
      ("happy-3", "Number", "42", "100", "Enter the Number here.", "Enter the Number value here. e.g. 100",
       "NumberLineEdit"),
    ])
  def test_create_line_edit_happy_path(self, mocker, primitive_compound_frame, test_id, type_name, type_value,
                                       template_value, expected_placeholder,
                                       expected_tooltip, expected_object_name):
    # Arrange
    mocker.resetall()
    adjust_type_name = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.adjust_type_name',
                                    return_value=type_name)

    # Act
    line_edit = primitive_compound_frame.create_line_edit(type_name=type_name, type_value=type_value,
                                                          template_value=template_value)

    # Assert
    adjust_type_name.assert_called_once_with(type_name)
    line_edit.setPlaceholderText.assert_called_once_with(expected_placeholder)
    line_edit.setToolTip.assert_called_once_with(expected_tooltip)
    line_edit.setObjectName.assert_called_once_with(expected_object_name)
    line_edit.setText.assert_called_once_with(type_value)
    line_edit.setClearButtonEnabled.assert_called_once_with(True)

  # Parametrized test for edge cases
  @pytest.mark.parametrize("test_id, type_name, type_value, template_value", [
    ("edge-1", "", "", None),  # Empty type_name and type_value
    ("edge-2", "LongTypeName" * 10, "Value", "Template"),  # Very long type_name
    ("edge-3", "Name", "John Doe" * 10, "John Smith"),  # Very long type_value
  ])
  def test_create_line_edit_edge_cases(self, mocker, test_id, primitive_compound_frame, type_name, type_value,
                                       template_value):
    # Arrange
    mocker.resetall()

    # Act
    line_edit = primitive_compound_frame.create_line_edit(type_name=type_name, type_value=type_value,
                                                          template_value=template_value)

    # Assert
    assert line_edit is not None
    line_edit.setObjectName.assert_called_once_with(f"{type_name}LineEdit")

  # Parametrized test cases for create_date_time_widget
  @pytest.mark.parametrize(
    "type_name, type_value, template_value, expected_date, expected_tooltip, expected_object_name",
    [
      # Success path tests
      ("birthdate", "1990-01-01", "2000-01-01", QDate(1990, 1, 1),
       "Enter the birthdate value here. e.g. 2000-01-01, Minimum possible date is 0100-01-02", "birthdateDateTimeEdit"),
      ("eventdate", "2023-10-10", "2023-01-01", QDate(2023, 10, 10),
       "Enter the eventdate value here. e.g. 2023-01-01, Minimum possible date is 0100-01-02", "eventdateDateTimeEdit"),

      # Edge cases
      ("startdate", "0100-01-02", None, QDate(100, 1, 2),
       "Enter the startdate value here. e.g. None, Minimum possible date is 0100-01-02", "startdateDateTimeEdit"),
      ("enddate", "No Value", "2022-12-31", QDate(1, 1, 1),
       "Enter the enddate value here. e.g. 2022-12-31, Minimum possible date is 0100-01-02", "enddateDateTimeEdit"),

      # Error cases
      ("invaliddate", "invalid", None, QDate(1, 1, 1),
       "Enter the invaliddate value here. e.g. None, Minimum possible date is 0100-01-02", "invaliddateDateTimeEdit"),
    ],
    ids=[
      "success_path_birthdate",
      "success_path_eventdate",
      "edge_case_startdate",
      "edge_case_enddate",
      "error_case_invaliddate",
    ]
  )
  def test_create_date_time_widget(self, mocker, primitive_compound_frame, type_name, type_value, template_value,
                                   expected_date, expected_tooltip,
                                   expected_object_name):
    # Arrange
    mock_qdate_time_edit = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QDateTimeEdit')
    adjust_type_name = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.adjust_type_name',
                                    return_value=type_name)

    # Act
    date_time_widget = primitive_compound_frame.create_date_time_widget(type_name, type_value, template_value)

    # Assert
    mock_qdate_time_edit.assert_called_once_with(parent=primitive_compound_frame.instance)
    assert date_time_widget == mock_qdate_time_edit.return_value
    date_time_widget.setSpecialValueText.assert_called_once_with("No Value")
    date_time_widget.setMinimumDate.assert_called_once_with(QDate.fromString("0100-01-01", 'yyyy-MM-dd'))
    adjust_type_name.assert_called_once_with(type_name)
    date_time_widget.setToolTip.assert_called_once_with(
      f"Enter the {type_name} value here. e.g. {template_value}, Minimum possible date is 0100-01-02")
    date_time_widget.setObjectName.assert_called_once_with(f"{type_name}DateTimeEdit")
    date_time_widget.setDate.assert_called_once_with(QDate.fromString(type_value, 'yyyy-MM-dd')
                                                     if type_value and type_value != 'No Value'
                                                     else QDate.fromString("0001-01-01", 'yyyy-MM-dd'))
    date_time_widget.setDisplayFormat.assert_called_once_with('yyyy-MM-dd')

  # Parametrized test for error cases
  @pytest.mark.parametrize("meta_field, test_id", [
    ({"typeClass": "primitive", "multiple": False}, "error_primitive_multiple_false"),
    ({"typeClass": "unknown"}, "error_unknown_typeclass"),
    # Add more test cases for different error scenarios
  ])
  def test_add_new_entry_error_cases(self, primitive_compound_frame, meta_field, test_id):
    # Arrange
    primitive_compound_frame.meta_field = meta_field

    # Act
    primitive_compound_frame.add_new_entry()

    # Assert
    assert primitive_compound_frame.logger.error.called

  # Parametrized test cases
  @pytest.mark.parametrize("meta_field,expected_log,expected_error", [
    # ID: HappyPath-Primitive
    ({"typeName": "testType", "typeClass": "primitive", "multiple": True, "valueTemplate": [{"key": "value"}]},
     ('Adding new entry of type %s, name: %s', 'primitive', 'testType'), None),
    # ID: HappyPath-Compound
    ({"typeName": "testType", "typeClass": "compound", "multiple": True,
      "valueTemplate": [
        {"key1": {"typeName": "date", "value": "2023-01-01"}, "key2": {"typeName": "title", "value": "2023-01-01"}}]},
     ('Adding new entry of type %s, name: %s', 'compound', 'testType'), None),
    # ID: ErrorCase-NonMultiple
    ({"typeName": "testType", "typeClass": "primitive", "multiple": False, "valueTemplate": [{"key": "value"}]},
     None, "Add operation not supported for non-multiple entries"),
    # ID: ErrorCase-UnknownTypeClass
    ({"typeName": "testType", "typeClass": "unknown", "multiple": True, "valueTemplate": [{"key": "value"}]},
     None, ('Unknown type class: %s', 'unknown')),
  ], ids=["SuccessCase-Primitive", "SuccessCase-Compound", "ErrorCase-NonMultiple", "ErrorCase-UnknownTypeClass"])
  def test_add_new_entry(self, mocker, primitive_compound_frame, meta_field, expected_log, expected_error):
    mocker.resetall()
    primitive_compound_frame.meta_field = meta_field
    mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.populate_primitive_horizontal_layout')
    mock_qvbox_layout = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QVBoxLayout')
    mock_qhbox_layout = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QHBoxLayout')
    create_date_time_widget = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.create_date_time_widget')
    create_line_edit = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.create_line_edit')
    add_delete_button = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.add_delete_button')
    add_clear_button = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.add_clear_button')

    # Act
    primitive_compound_frame.add_new_entry()

    # Assert
    if meta_field['typeClass'] == "primitive" and not expected_error:
      primitive_compound_frame.mainVerticalLayout.findChild.assert_called_once_with(
        mock_qvbox_layout,
        "primitiveVerticalLayout"
      )
      primitive_compound_frame.populate_primitive_horizontal_layout.assert_called_once_with(
        primitive_compound_frame.mainVerticalLayout.findChild.return_value,
        meta_field['typeName'],
        "",
        meta_field['valueTemplate'][0]
      )
    elif meta_field['typeClass'] == "compound" and not expected_error:
      mock_qhbox_layout.assert_called_once()
      mock_qhbox_layout.return_value.setObjectName.assert_called_once_with("compoundHorizontalLayout")
      create_date_time_widget.assert_called_once()
      create_line_edit.assert_called_once()
      add_clear_button.assert_called_once_with(primitive_compound_frame.instance, mock_qhbox_layout.return_value)
      add_delete_button.assert_called_once_with(primitive_compound_frame.instance, mock_qhbox_layout.return_value)
      primitive_compound_frame.mainVerticalLayout.addLayout.assert_called_once_with(mock_qhbox_layout.return_value)
      mock_qhbox_layout.return_value.addWidget.assert_has_calls(
        [mocker.call(create_date_time_widget.return_value), mocker.call(create_line_edit.return_value)])
    if expected_log:
      primitive_compound_frame.logger.info.assert_called_with(expected_log[0], expected_log[1], expected_log[2])
    if expected_error:
      if isinstance(expected_error, tuple):
        primitive_compound_frame.logger.error.assert_called_with(*expected_error)
      else:
        primitive_compound_frame.logger.error.assert_called_with(expected_error)

  # Parametrized test cases
  @pytest.mark.parametrize(
    "test_id, compound_entry, template_entry, is_date_time_type_return, expected_widget_calls",
    [
      # Success path tests with various realistic test values
      ("SuccessCase-1",
       {"date": {"value": "2021-01-01"}},
       {"date": {"value": "2020-01-01"}},
       True,
       [('create_date_time_widget', 1), ('create_line_edit', 0)]),
      ("SuccessCase-2",
       {"text": {"value": "Sample Text"}},
       {"text": {"value": "Default Text"}},
       False,
       [('create_date_time_widget', 0), ('create_line_edit', 1)]),
      # Edge cases
      ("EdgeCase-1",
       {},
       {},
       False,
       []),

      # Error cases
      # Assuming that an error case would be when template_entry is missing a key present in compound_entry
      ("ErrorCase-1",
       {"date": {"value": "2021-01-01"}},
       {},
       True,
       [('create_date_time_widget', 1)]),  # KeyError should be raised when template_entry is missing
    ]
  )
  def test_populate_compound_entry(self, mocker, primitive_compound_frame, test_id, compound_entry, template_entry,
                                   is_date_time_type_return,
                                   expected_widget_calls):
    # Arrange
    mocker.resetall()
    is_date_time_type = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.is_date_time_type',
                                     return_value=is_date_time_type_return)
    mock_qhbox_layout = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QHBoxLayout')
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.create_date_time_widget')
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.create_line_edit')
    mock_add_delete_button = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.add_delete_button')
    mock_add_clear_button = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.add_clear_button')
    mock_qhbox_layout.return_value.count.return_value = len(compound_entry)

    # Act
    primitive_compound_frame.populate_compound_entry(compound_entry, template_entry)

    # Assert
    for widget_name, call_count in expected_widget_calls:
      assert getattr(primitive_compound_frame, widget_name).call_count == call_count
    if test_id == "EdgeCase-1":
      mock_add_delete_button.assert_not_called()
    if compound_entry:
      is_date_time_type.assert_called_once()
      mock_add_delete_button.assert_called_once_with(primitive_compound_frame.instance, mock_qhbox_layout.return_value,
                                                     True)
      mock_add_clear_button.assert_called_once_with(primitive_compound_frame.instance, mock_qhbox_layout.return_value)
      mock_qhbox_layout.return_value.addWidget.assert_has_calls(
        [mocker.call(primitive_compound_frame.create_date_time_widget.return_value) if is_date_time_type_return else
         mocker.call(primitive_compound_frame.create_line_edit.return_value)]
      )
      primitive_compound_frame.mainVerticalLayout.addLayout.assert_called_once_with(mock_qhbox_layout.return_value)

  @pytest.mark.parametrize(
    "meta_field, expected_calls, test_id",
    [
      # Happy path tests
      (
          {'value': ['val1', 'val2'], 'typeName': 'String', 'valueTemplate': ['tmpl'], 'multiple': True},
          2,
          "happy_path_multiple_values"
      ),
      (
          {'value': 'single_val', 'typeName': 'Number', 'valueTemplate': 'tmpl', 'multiple': False},
          1,
          "happy_path_single_value"
      ),
      # Edge cases
      (
          {'value': [], 'typeName': 'String', 'valueTemplate': ['tmpl'], 'multiple': True},
          1,
          "edge_case_empty_value_list"
      ),
      (
          {'value': '', 'typeName': 'Number', 'valueTemplate': 'tmpl', 'multiple': False},
          1,
          "edge_case_empty_string_value"
      ),
      # Error cases
      (
          {'value': None, 'typeName': 'Number', 'valueTemplate': 'tmpl', 'multiple': False},
          1,
          "error_case_none_value"
      ),
      (
          {'value': 'single_val', 'typeName': None, 'valueTemplate': 'tmpl', 'multiple': False},
          1,
          "error_case_none_type_name"
      ),
    ],
  )
  def test_populate_primitive_entry(self, mocker, primitive_compound_frame, meta_field, expected_calls, test_id):
    # Arrange
    mocker.resetall()
    primitive_compound_frame.meta_field = meta_field
    mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.populate_primitive_horizontal_layout')
    mock_qvbox_layout = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QVBoxLayout')
    # Act
    primitive_compound_frame.populate_primitive_entry()

    # Assert
    mock_qvbox_layout.assert_called_once()
    mock_qvbox_layout.return_value.setObjectName.assert_called_once_with('primitiveVerticalLayout')
    assert primitive_compound_frame.populate_primitive_horizontal_layout.call_count == expected_calls
    if expected_calls > 0:
      primitive_compound_frame.mainVerticalLayout.addLayout.assert_called_once_with(mock_qvbox_layout.return_value)
    primitive_compound_frame.logger.info.assert_called_with(
      "Populating new entry of type primitive, name: %s", meta_field.get('typeName')
    )

  # Parametrized test cases
  # Parametrized test cases
  @pytest.mark.parametrize("type_name,type_value,type_value_template,is_date_time", [
    # Test ID: #1 - Happy path, date time type
    ("date", "2021-01-01T00:00:00", "YYYY-MM-DDTHH:MM:SS", True),
    # Test ID: #2 - Happy path, non-date time type
    ("text", "example", "{template}", False),
    # Add more test cases for edge and error cases
  ])
  def test_populate_primitive_horizontal_layout(self, mocker, type_name, primitive_compound_frame, type_value,
                                                type_value_template, is_date_time):
    # Arrange
    mock_layout = mocker.MagicMock(spec=QBoxLayout)
    mock_qhbox_layout = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QHBoxLayout')
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.create_date_time_widget')
    mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.create_line_edit')
    mock_add_delete_button = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.add_delete_button')
    mock_add_clear_button = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.add_clear_button')
    is_date_time_type_mock = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.is_date_time_type',
                                          return_value=is_date_time)

    # Act
    primitive_compound_frame.populate_primitive_horizontal_layout(mock_layout, type_name, type_value,
                                                                  type_value_template)

    # Assert
    is_date_time_type_mock.assert_called_once_with(type_name)
    mock_qhbox_layout.return_value.setObjectName.assert_called_once_with('primitiveHorizontalLayout')
    if is_date_time:
      primitive_compound_frame.create_date_time_widget.assert_called_once_with(type_name, type_value,
                                                                               type_value_template)
      mock_qhbox_layout.return_value.addWidget.assert_has_calls(
        primitive_compound_frame.create_date_time_widget.return_value)
    else:
      primitive_compound_frame.create_line_edit.assert_called_once_with(type_name, type_value, type_value_template)
      mock_qhbox_layout.return_value.addWidget.assert_has_calls(
        primitive_compound_frame.create_line_edit.return_value)
    mock_add_delete_button.assert_called_once_with(primitive_compound_frame.instance, mock_qhbox_layout.return_value,
                                                   True)
    mock_add_clear_button.assert_called_once_with(primitive_compound_frame.instance, mock_qhbox_layout.return_value)
    mock_layout.addLayout.assert_called_once_with(mock_qhbox_layout.return_value)

  @pytest.mark.parametrize("type_class, multiple, expected_value, test_id", [
    # Success path tests
    ("primitive", False, "single_value", "success_single_primitive"),
    ("primitive", True, ["value1", "value2"], "success_multiple_primitive"),
    ("compound", False, {"key": "value"}, "success_single_compound"),
    ("compound", True, [{"key1": "value1"}, {"key2": "value2"}], "success_multiple_compound"),

    # Edge cases
    ("primitive", True, [], "edge_no_values_primitive"),
    ("compound", True, [], "edge_no_values_compound"),

    # Error cases
    ("unsupported", False, None, "error_unsupported_type_class"),
  ])
  def test_save_modifications(self, type_class, mocker, primitive_compound_frame, multiple, expected_value, test_id):
    # Arrange
    mock_qvbox_layout = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QVBoxLayout')
    mock_qhbox_layout = mocker.patch('pasta_eln.GUI.dataverse.primitive_compound_frame.QHBoxLayout')
    mock_save_compound_horizontal_layout_values = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_frame.PrimitiveCompoundFrame.save_compound_horizontal_layout_values')
    mocker.resetall()
    primitive_compound_frame.meta_field = {
      'typeName': 'testTypeName',
      'typeClass': type_class,
      'multiple': multiple,
      'value': ["test"] if multiple else "",
      'valueTemplate': ["test"] if multiple else ""
    }
    primitive_compound_frame.mainVerticalLayout.findChild.return_value.count.return_value = 1 if multiple else 0
    primitive_compound_frame.mainVerticalLayout.count.return_value = 1 if multiple else 0

    # Act
    primitive_compound_frame.save_modifications()

    # Assert
    if type_class == "unsupported":
      primitive_compound_frame.logger.error.assert_called_once_with("Unsupported typeClass: %s",
                                                                    primitive_compound_frame.meta_field.get(
                                                                      'typeClass'))
    else:
      if type_class == "primitive":
        primitive_compound_frame.mainVerticalLayout.findChild.assert_called_once_with(mock_qvbox_layout,
                                                                                      "primitiveVerticalLayout")
        if multiple:
          primitive_compound_frame.mainVerticalLayout.findChild.return_value.count.assert_called_once()
          assert (primitive_compound_frame.meta_field['value'] ==
                  [primitive_compound_frame.mainVerticalLayout.findChild.return_value.itemAt.return_value.
                  itemAt.return_value.widget.return_value.text.return_value])
        else:
          assert (primitive_compound_frame.meta_field[
                    'value'] == primitive_compound_frame.mainVerticalLayout.findChild.return_value
                  .itemAt.return_value.itemAt.return_value.widget.return_value.text.return_value)
      elif type_class == "compound":
        if multiple:
          primitive_compound_frame.mainVerticalLayout.count.assert_called_once()
          primitive_compound_frame.mainVerticalLayout.itemAt.assert_called_once_with(0)
          mock_save_compound_horizontal_layout_values.assert_called_once_with(
            primitive_compound_frame.mainVerticalLayout.itemAt.return_value,
            primitive_compound_frame.meta_field.get('valueTemplate')[0]
          )
        else:
          primitive_compound_frame.mainVerticalLayout.findChild.assert_called_once_with(mock_qhbox_layout,
                                                                                        "compoundHorizontalLayout")
          mock_save_compound_horizontal_layout_values.assert_called_once_with(
            primitive_compound_frame.mainVerticalLayout.findChild.return_value,
            primitive_compound_frame.meta_field.get('valueTemplate') or {}
          )

      primitive_compound_frame.logger.info.assert_called_once_with(
        "Saving changes to meta_field for type, name: %s, class: %s",
        primitive_compound_frame.meta_field.get('typeName'),
        primitive_compound_frame.meta_field.get('typeClass'))

  # Parametrized test cases
  @pytest.mark.parametrize(
    "test_id, layout_widgets, value_template, expected_meta_field_value",
    [
      # Happy path tests with various realistic test values
      ("success-1", [("name1", "value1"), ("name2", "value2")], {"name1": {}, "name2": {}},
       [{"name1": {"value": "value1"}, "name2": {"value": "value2"}}]),
      ("success-2", [("name3", ""), ("name4", "value4")], {"name3": {}, "name4": {}},
       [{"name3": {"value": ""}, "name4": {"value": "value4"}}]),

      # Edge cases
      ("edge-1", [], {"name1": {}}, []),  # No widgets in layout
      ("edge-2", [("name1", None)], {"name1": {}}, []),  # Widget text is None
    ]
  )
  def test_save_compound_horizontal_layout_values(self, mocker, primitive_compound_frame, test_id, layout_widgets,
                                                  value_template, expected_meta_field_value):
    # Arrange
    mocker.resetall()
    primitive_compound_frame.meta_field = {'value': []}

    compound_horizontal_layout = mocker.MagicMock(spec=QBoxLayout)
    compound_horizontal_layout.count.return_value = len(layout_widgets)
    # Create mock widgets and add them to the layout
    compound_horizontal_layout.itemAt = lambda pos, _widgets=layout_widgets: create_mock_line_edit(mocker, *_widgets[
      pos]) if pos < len(_widgets) else None

    # Act
    primitive_compound_frame.save_compound_horizontal_layout_values(compound_horizontal_layout, value_template)

    # Assert
    assert primitive_compound_frame.meta_field['value'] == expected_meta_field_value
