""" Utility function used by the dataverse module """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Callable

from PySide6.QtCore import QDate, QSize
from PySide6.QtWidgets import QBoxLayout, QComboBox, QDateTimeEdit, QFrame, QLineEdit, QPushButton, QSizePolicy


def create_push_button(button_display_text: str,
                       object_name: str,
                       tooltip: str,
                       parent_frame: QFrame,
                       parent_layout: QBoxLayout,
                       clicked_callback: Callable[[QBoxLayout], None]) -> QPushButton:
  """
  Creates a push button widget with specified properties.

  Args:
    button_display_text (str): The text to display on the button.
    object_name (str): The object name for the button.
    tooltip (str): The tooltip text for the button.
    parent_frame (QFrame): The parent QFrame object.
    parent_layout (QBoxLayout): The parent QBoxLayout object.
    clicked_callback (Callable[[QBoxLayout], None]): The callback function to execute when the button is clicked.


  Returns:
    QPushButton: The created push button widget.
  """
  push_button = QPushButton(parent=parent_frame)
  push_button.setText(button_display_text)
  push_button.setObjectName(object_name)
  push_button.setToolTip(tooltip)
  size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
  size_policy.setHorizontalStretch(0)
  size_policy.setVerticalStretch(0)
  size_policy.setHeightForWidth(push_button.sizePolicy().hasHeightForWidth())
  push_button.setSizePolicy(size_policy)
  push_button.setMinimumSize(QSize(100, 0))
  push_button.clicked.connect(lambda: clicked_callback(parent_layout))
  return push_button


def add_delete_button(parent_frame: QFrame,
                      parent: QBoxLayout,

                      enabled: bool = True) -> None:
  """
  Adds a delete button to the layout.
  Args:
      parent_frame (QFrame): The parent QFrame object.
      parent (QBoxLayout): The parent QBoxLayout object.
      enabled (bool, optional): Whether the button should be enabled or disabled.
      Defaults to True.

  Returns:
      QPushButton: The created delete button widget.

  Explanation:
      This function creates a QPushButton widget with the specified properties and adds it to the parent layout.
      The button is labeled as "Delete" and can be enabled or disabled based on the 'enabled' parameter.
      It is connected to a lambda function that calls the 'delete' function with the parent QBoxLayout as an argument.

  """
  delete_push_button = create_push_button(
    "Delete",
    "deletePushButton",
    "Delete this particular entry.",
    parent_frame,
    parent,
    delete_layout_and_contents)
  delete_push_button.setEnabled(enabled)
  parent.addWidget(delete_push_button)


def add_clear_button(parent_frame: QFrame,
                     parent: QBoxLayout) -> None:
  button = create_push_button(
    "Clear",
    "clearPushButton",
    "Clear this particular entry.",
    parent_frame,
    parent,
    clear_layout_widgets,
  )
  parent.addWidget(button)


def clear_layout_widgets(layout: QBoxLayout) -> None:
  """
  Clears the widgets in the given layout by resetting QLineEdit, QComboBox, and QDateTimeEdit widgets.

  Args:
    layout (QBoxLayout): The layout containing the widgets to be cleared.
  """
  if layout is None:
    return
  for widget_pos in reversed(range(layout.count())):
    if item := layout.itemAt(widget_pos):
      widget = item.widget()
      if isinstance(widget, QLineEdit):
        widget.clear()
      elif isinstance(widget, QComboBox):
        widget.setCurrentText("No Value")
      elif isinstance(widget, QDateTimeEdit):
        widget.setDate(QDate.fromString("01/01/0001", "dd/MM/yyyy"))


def delete_layout_and_contents(layout: QBoxLayout) -> None:
  """
  Deletes the layout and its contents.

  Args:
      layout (QBoxLayout): The layout to delete.

  Explanation:
      This function deletes the given layout and its contents.
      It iterates over the widgets in the layout and removes them from their parent.
      Finally, it sets the layout's parent to None.

  """
  if layout is None:
    return
  for widget_pos in reversed(range(layout.count())):
    if item := layout.itemAt(widget_pos):
      item.widget().setParent(None)
  layout.setParent(None)
