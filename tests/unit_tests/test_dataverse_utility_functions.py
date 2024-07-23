#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateTimeEdit, QLineEdit, QVBoxLayout

from pasta_eln.GUI.dataverse.utility_functions import add_clear_button, add_delete_button, clear_layout_widgets, \
  create_push_button, \
  delete_layout_and_contents


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
