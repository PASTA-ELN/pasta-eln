#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QBoxLayout, QComboBox, QDateTimeEdit, QFrame, QHBoxLayout, QLineEdit, QVBoxLayout
from _pytest.mark import param

from pasta_eln.GUI.dataverse.utility_functions import add_clear_button, add_delete_button, clear_layout_widgets, \
  create_date_time_widget, create_line_edit, create_push_button, \
  delete_layout_and_contents, get_primitive_line_edit_text_value


@pytest.fixture
def create_layout():
  def _create_layout(text_value, widget_pos, layout_type, is_widget_valid=True):
    v_layout = MagicMock(spec=QVBoxLayout)
    h_layout = MagicMock(spec=QHBoxLayout) if layout_type == 'QHBoxLayout' else MagicMock(spec=QBoxLayout)
    line_edit = MagicMock(spec=QLineEdit)
    line_edit.text.return_value = str(text_value)
    v_layout.itemAt.side_effect = lambda x: h_layout
    h_layout.itemAt.return_value.widget.return_value = line_edit if is_widget_valid else None
    h_layout.layout.return_value = h_layout
    return v_layout, widget_pos

  return _create_layout


class TestDataverseUtilityFunctions:
  @pytest.mark.parametrize(
    "button_display_text, object_name, tooltip, expected_text, expected_object_name, expected_tooltip",
    [
      ("Click Me", "btnClickMe", "Click this button",
       "Click Me", "btnClickMe", "Click this button"),
      ("Submit", "btnSubmit", "Submit your data", "Submit",
       "btnSubmit", "Submit your data"),
      ("Cancel", "btnCancel", "Cancel the operation",
       "Cancel", "btnCancel", "Cancel the operation"),
    ],
    ids=["click_me_button", "submit_button", "cancel_button"]
  )
  def test_create_push_button(self, mocker, button_display_text, object_name, tooltip,
                              expected_text, expected_object_name, expected_tooltip):
    mock_push_button = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.QPushButton')
    mock_size_policy = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.QSizePolicy')
    mock_size = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.QSize')
    parent_layout = mocker.MagicMock()
    parent_frame = mocker.MagicMock()
    clicked_callback = mocker.MagicMock()

    # Act
    push_button = create_push_button(button_display_text, object_name, tooltip, parent_frame, parent_layout,
                                     clicked_callback)

    # Assert
    mock_push_button.assert_called_once_with(parent=parent_frame)
    push_button.setText.assert_called_once_with(button_display_text)
    push_button.setObjectName.assert_called_once_with(object_name)
    push_button.setToolTip.assert_called_once_with(tooltip)
    mock_size_policy.assert_called_once_with(mock_size_policy.Policy.Fixed, mock_size_policy.Policy.Fixed)
    size_policy = mock_size_policy.return_value
    size_policy.setHorizontalStretch.assert_called_once_with(0)
    size_policy.setVerticalStretch.assert_called_once_with(0)
    size_policy.setHeightForWidth.assert_called_once_with(
      mock_push_button.return_value.sizePolicy().hasHeightForWidth())
    push_button.setSizePolicy.assert_called_once_with(size_policy)
    mock_size.assert_called_once_with(100, 0)
    push_button.setMinimumSize.assert_called_once_with(mock_size.return_value)
    push_button.clicked.connect.assert_called_once()

  @pytest.mark.parametrize(
    "widget_specs, expected_values",
    [
      # Success path tests
      pytest.param(
        [QLineEdit, QComboBox, QDateTimeEdit],
        ["", "No Value", QDate.fromString("01/01/0001", "dd/MM/yyyy")],
        id="happy_path_all_widgets"
      ),
      pytest.param(
        [QLineEdit],
        [""],
        id="happy_path_qlineedit_only"
      ),
      pytest.param(
        [QComboBox],
        ["No Value"],
        id="happy_path_qcombobox_only"
      ),
      pytest.param(
        [QDateTimeEdit],
        [QDate.fromString("01/01/0001", "dd/MM/yyyy")],
        id="happy_path_qdatetimeedit_only"
      ),
      # Edge cases
      pytest.param(
        [],
        [],
        id="edge_case_empty_layout"
      ),
      pytest.param(
        [None],
        [None],
        id="edge_case_none_widget"
      ),
      # Error cases
      pytest.param(
        [QLineEdit, QComboBox, QDateTimeEdit],
        None,
        id="error_case_none_layout"
      ),
    ]
  )
  def test_clear_layout_widgets(self, mocker, widget_specs, expected_values):
    # Arrange
    widgets = [mocker.MagicMock(spec=widget_spec) if widget_spec is not None else None for widget_spec in widget_specs]
    for widget in widgets:
      if widget is not None:
        mocker.patch.object(widget, "widget", create=True)
        widget.widget.return_value = widget
    layout = mocker.MagicMock(spec=QVBoxLayout) if expected_values is not None else None
    if layout:
      layout.itemAt.side_effect = lambda i: widgets[i] if i < len(widgets) else None
      layout.count.return_value = len(widgets)

    # Act
    clear_layout_widgets(layout)

    # Assert
    if layout:
      for i, widget in enumerate(widgets):
        if widget is None:
          continue
        elif isinstance(widget, QLineEdit):
          widget.clear.assert_called_once()
        elif isinstance(widget, QComboBox):
          widget.setCurrentText.assert_called_once_with(expected_values[i])
        elif isinstance(widget, QDateTimeEdit):
          widget.setDate.assert_called_once_with(expected_values[i])
    else:
      for i, widget in enumerate(widgets):
        if widget is None:
          continue
        elif isinstance(widget, QLineEdit):
          widget.clear.assert_not_called()
        elif isinstance(widget, QComboBox):
          widget.setCurrentText.assert_not_called()
        elif isinstance(widget, QDateTimeEdit):
          widget.setDate.assert_not_called()

  def test_add_delete_button(self, mocker):

    # Arrange
    mock_create_push_button = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.create_push_button')
    parent_layout = mocker.MagicMock()
    parent_frame = mocker.MagicMock()

    # Act
    add_delete_button(parent_frame, parent_layout)

    # Assert
    mock_create_push_button(
      "Delete",
      "deletePushButton",
      "Delete this particular vocabulary entry.",
      parent_frame,
      parent_layout,
      delete_layout_and_contents)
    parent_layout.addWidget.assert_called_once_with(mock_create_push_button.return_value)

  def test_add_clear_button(self, mocker):

    # Arrange
    mock_create_push_button = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.create_push_button')
    parent_layout = mocker.MagicMock()
    parent_frame = mocker.MagicMock()

    # Act
    add_clear_button(parent_frame, parent_layout)

    # Assert
    mock_create_push_button(
      "Clear",
      "clearPushButton",
      "Clear this particular vocabulary entry.",
      parent_frame,
      parent_layout,
      clear_layout_widgets)
    parent_layout.addWidget.assert_called_once_with(mock_create_push_button.return_value)

  @pytest.mark.parametrize(
    "test_id, num_widgets",
    [
      ("success_path_1_widget", 1),  # ID: success_path_1_widget
      ("success_path_multiple_widgets", 3),  # ID: success_path_multiple_widgets
      ("success_path_no_widgets", 0),  # ID: success_path_no_widgets
      ("edge_case_no_layout", 0),  # ID: edge_case_no_layout
    ]
  )
  def test_delete_layout_and_contents(self, mocker, test_id, num_widgets):
    # Arrange
    layout = mocker.MagicMock()
    widgets = [mocker.MagicMock() for _ in range(num_widgets)]
    layout.itemAt = lambda pos: widgets[pos]
    layout.count.return_value = len(widgets)
    layout = None if test_id == "edge_case_no_layout" else layout

    # Act
    delete_layout_and_contents(layout)

    # Assert
    if test_id == "edge_case_no_layout":
      for widget in widgets:
        widget.widget.return_value.setParent.assert_not_called()
    else:
      layout.count.assert_called_once()
      layout.setParent.assert_called_once_with(None)
      for widget in widgets:
        widget.widget.return_value.setParent.assert_called_once_with(None)

  @pytest.mark.parametrize(
    "type_name, type_value, template_value, expected_date, expected_tooltip, expected_object_name",
    [
      # Success path tests
      ("start", "2023-01-01", "2023-01-01", QDate(2023, 1, 1),
       "Enter the start value here. e.g. 2023-01-01, Minimum possible date is 0100-01-02", "startDateTimeEdit"),
      ("end", "2022-12-31", "2022-12-31", QDate(2022, 12, 31),
       "Enter the end value here. e.g. 2022-12-31, Minimum possible date is 0100-01-02", "endDateTimeEdit"),

      # Edge cases
      ("start", "0100-01-02", None, QDate(100, 1, 2),
       "Enter the start value here. e.g. None, Minimum possible date is 0100-01-02", "startDateTimeEdit"),
      (
          "end", "No Value", None, QDate(1, 1, 1),
          "Enter the end value here. e.g. None, Minimum possible date is 0100-01-02",
          "endDateTimeEdit"),

      # Error cases
      ("start", "", None, QDate(1, 1, 1), "Enter the start value here. e.g. None, Minimum possible date is 0100-01-02",
       "startDateTimeEdit"),
      ("end", "invalid-date", None, QDate(1, 1, 1),
       "Enter the end value here. e.g. None, Minimum possible date is 0100-01-02", "endDateTimeEdit"),
    ],
    ids=[
      "success_path_start_date",
      "success_path_end_date",
      "edge_case_min_date",
      "edge_case_no_value",
      "error_case_empty_string",
      "error_case_invalid_date",
    ]
  )
  def test_create_date_time_widget(self, mocker, type_name, type_value, template_value, expected_date, expected_tooltip,
                                   expected_object_name):
    # Arrange
    mock_adjust_type_name = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.adjust_type_name',
                                         return_value=type_name)
    mock_date_time_edit = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.QDateTimeEdit')
    parent_frame = mocker.MagicMock(spec=QFrame)

    # Act
    date_time_edit = create_date_time_widget(type_name, type_value, parent_frame, template_value)

    # Assert
    mock_date_time_edit.assert_called_once_with(parent=parent_frame)
    mock_date_time_edit.return_value.setSpecialValueText.assert_called_once_with("No Value")
    mock_date_time_edit.return_value.setMinimumDate.assert_called_once_with(
      QDate.fromString("0100-01-01", 'yyyy-MM-dd'))
    mock_adjust_type_name.assert_called_once_with(type_name)
    mock_date_time_edit.return_value.setToolTip.assert_called_once_with(
      f"Enter the {mock_adjust_type_name.return_value} value here. e.g. {template_value}, Minimum possible date is 0100-01-02"
    )
    mock_date_time_edit.return_value.setObjectName.assert_called_once_with(f"{type_name}DateTimeEdit")
    mock_date_time_edit.return_value.setDate.assert_called_once_with(
      QDate.fromString(type_value, 'yyyy-MM-dd')
      if type_value and type_value != 'No Value'
      else QDate.fromString("0001-01-01", 'yyyy-MM-dd')
    )
    mock_date_time_edit.return_value.setDisplayFormat.assert_called_once_with('yyyy-MM-dd')
    assert date_time_edit == mock_date_time_edit.return_value

  @pytest.mark.parametrize(
    "type_name, type_value, template_value, expected_placeholder, expected_tooltip, expected_object_name, expected_text",
    [
      # Success path tests
      ("username", "john_doe", "example_user", "Enter the username here.",
       "Enter the username value here. e.g. example_user", "usernameLineEdit", "john_doe"),
      ("email", "john@example.com", "example@example.com", "Enter the email here.",
       "Enter the email value here. e.g. example@example.com", "emailLineEdit", "john@example.com"),

      # Edge cases
      ("", "", "", "Enter the  here.", "Enter the  value here. e.g. ", "LineEdit", ""),
      ("a" * 100, "b" * 100, "c" * 100, "Enter the " + "a" * 100 + " here.",
       "Enter the " + "a" * 100 + " value here. e.g. " + "c" * 100, "a" * 100 + "LineEdit", "b" * 100),

      # Error cases
      ("username", None, "example_user", "Enter the username here.", "Enter the username value here. e.g. example_user",
       "usernameLineEdit", ""),  # type_value is None
      (None, "john_doe", "example_user", "Enter the None here.", "Enter the None value here. e.g. example_user",
       "NoneLineEdit", "john_doe"),  # type_name is None
    ],
    ids=[
      "success_path_username",
      "success_path_email",
      "edge_case_empty_strings",
      "edge_case_long_strings",
      "error_case_type_value_none",
      "error_case_type_name_none",
    ]
  )
  def test_create_line_edit(self, mocker, type_name, type_value, template_value, expected_placeholder, expected_tooltip,
                            expected_object_name, expected_text):
    # Arrange
    mock_adjust_type_name = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.adjust_type_name',
                                         return_value=type_name)
    mock_line_edit = mocker.patch('pasta_eln.GUI.dataverse.utility_functions.QLineEdit',
                                  return_value=mocker.MagicMock(spec=QLineEdit))
    parent_frame = mocker.MagicMock(spec=QFrame)

    # Act
    line_edit = create_line_edit(type_name, type_value, parent_frame, template_value)

    # Assert
    assert isinstance(line_edit, QLineEdit)
    assert line_edit == mock_line_edit.return_value
    mock_line_edit.assert_called_once_with(parent=parent_frame)
    mock_line_edit.return_value.setPlaceholderText.assert_called_once_with(expected_placeholder)
    mock_line_edit.return_value.setToolTip.assert_called_once_with(expected_tooltip)
    mock_line_edit.return_value.setClearButtonEnabled.assert_called_once_with(True)
    mock_adjust_type_name.assert_called_once_with(type_name)
    mock_line_edit.return_value.setObjectName.assert_called_once_with(f"{type_name}LineEdit")
    mock_line_edit.return_value.setText.assert_called_once_with(expected_text)

  @pytest.mark.parametrize("text_value, widget_pos, layout_type, expected", [
    param("test", 0, 'QHBoxLayout', "test", id="success_path_1"),
    param("another test", 0, 'QHBoxLayout', "another test", id="success_path_2"),
    param("", 0, 'QHBoxLayout', "", id="empty_string"),
    param("edge case", 1, 'QHBoxLayout', "", id="invalid_widget_pos"),
    param("wrong layout", 0, 'QBoxLayout', "", id="wrong_layout_type"),
    param("no widget", 0, 'QHBoxLayout', "", id="no_widget_in_layout"),
  ], ids=lambda x: x[-1])
  def test_get_primitive_line_edit_text_value(self, create_layout, text_value, widget_pos, layout_type, expected):
    # Arrange
    v_layout, widget_pos = create_layout(text_value, widget_pos, layout_type,
                                         is_widget_valid=text_value not in ["edge case", "no widget"])

    # Act
    result = get_primitive_line_edit_text_value(v_layout, widget_pos)

    # Assert
    assert result == expected
