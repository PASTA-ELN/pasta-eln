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
from PySide6.QtWidgets import QBoxLayout, QComboBox, QDateTimeEdit, QFrame, QHBoxLayout, QLineEdit, QPushButton, \
  QSizePolicy, QVBoxLayout

from pasta_eln.dataverse.utils import adjust_type_name


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

  Explanation:
      This function creates a QPushButton widget with the specified properties and adds it to the parent layout.
      The button is labeled as "Delete" and can be enabled or disabled based on the 'enabled' parameter.
      It is connected to a lambda function that calls the 'delete' function with the parent QBoxLayout as an argument.
  """
  delete_push_button = create_push_button(
    'Delete',
    'deletePushButton',
    'Delete this particular entry.',
    parent_frame,
    parent,
    delete_layout_and_contents)
  delete_push_button.setEnabled(enabled)
  parent.addWidget(delete_push_button)


def add_clear_button(parent_frame: QFrame,
                     parent: QBoxLayout) -> None:
  """
  Adds a clear button to the layout.

  Args:
      parent_frame (QFrame): The parent QFrame object.
      parent (QBoxLayout): The parent QBoxLayout object.

  Explanation:
      This function creates a QPushButton widget with the specified properties and adds it to the parent layout.
      The button is labeled as "Clear" and can be connected to a lambda function that calls the 'clear' function
      with the parent QBoxLayout as an argument.
  """
  button = create_push_button(
    'Clear',
    'clearPushButton',
    'Clear this particular entry.',
    parent_frame,
    parent,
    clear_layout_widgets,
  )
  parent.addWidget(button)


def create_date_time_widget(type_name: str,
                            type_value: str,
                            parent_frame: QFrame,
                            template_value: str | None = None) -> QDateTimeEdit:
  """
  Creates a date-time edit widget.

  Args:
      parent_frame (QFrame): The parent QFrame object.
      type_name (str): The name of the type.
      type_value (str): The initial value for the date-time edit.
      template_value (str | None, optional): The template value for the date-time edit. Defaults to None.

  Returns:
      QDateTimeEdit: The created date-time edit widget.

  Explanation:
      This function creates a QDateTimeEdit widget with the specified properties.
      The widget is set with a tooltip based on the type name and template value.
      It is assigned an object name based on the type name.
      The initial value is set for the date-time edit, and the display format is set to 'yyyy-MM-dd'.

  """
  date_time_edit = QDateTimeEdit(parent=parent_frame)
  date_time_edit.setSpecialValueText('No Value')
  date_time_edit.setMinimumDate(QDate.fromString('0100-01-01', 'yyyy-MM-dd'))
  adjusted_name = adjust_type_name(type_name)
  date_time_edit.setToolTip(
    f"Enter the {adjusted_name} value here. e.g. {template_value}, Minimum possible date is 0100-01-02")
  date_time_edit.setObjectName(f"{type_name}DateTimeEdit")
  date_time_edit.setDate(QDate.fromString(type_value, 'yyyy-MM-dd')
                         if type_value and type_value != 'No Value'
                         else QDate.fromString('0001-01-01', 'yyyy-MM-dd'))
  date_time_edit.setDisplayFormat('yyyy-MM-dd')
  return date_time_edit


def create_line_edit(type_name: str,
                     type_value: str,
                     parent_frame: QFrame,
                     template_value: str | None = None) -> QLineEdit:
  """
  Creates a line edit widget.

  Args:
      parent_frame (QFrame): The parent QFrame object.
      type_name (str): The name of the type.
      type_value (str): The initial value for the line edit.
      template_value (str | None, optional): The template value for the line edit. Defaults to None.

  Returns:
      QLineEdit: The created line edit widget.

  Explanation:
      This function creates a QLineEdit widget with the specified properties.
      The line edit is set with a placeholder text and a tooltip based on the type name and template value.
      It has a clear button enabled and is assigned an object name based on the type name.
      The initial value is set for the line edit.

  """
  entry_line_edit = QLineEdit(parent=parent_frame)
  adjusted_name = adjust_type_name(type_name)
  entry_line_edit.setPlaceholderText(f"Enter the {adjusted_name} here.")
  entry_line_edit.setToolTip(f"Enter the {adjusted_name} value here. e.g. {template_value}")
  entry_line_edit.setClearButtonEnabled(True)
  entry_line_edit.setObjectName(f"{type_name}LineEdit")
  entry_line_edit.setText(type_value or '')
  return entry_line_edit


def get_primitive_line_edit_text_value(primitive_vertical_layout: QVBoxLayout, widget_pos: int) -> str:
  """
  Retrieves the text value of a QLineEdit widget in a primitive vertical layout.

  Args:
      primitive_vertical_layout (QVBoxLayout): The vertical layout containing the QLineEdit widget.
      widget_pos (int): The position of the widget in the layout.

  Returns:
      str: The text value of the QLineEdit widget if found, otherwise None.

  Explanation:
      This function retrieves the text value of a QLineEdit widget located at the specified position in a primitive vertical layout.
      It first accesses the horizontal layout at the given position and then checks if the widget is a QLineEdit before returning its text value.
  """
  primitive_horizontal_layout = primitive_vertical_layout.itemAt(widget_pos).layout()
  if isinstance(primitive_horizontal_layout, QHBoxLayout):
    line_edit = primitive_horizontal_layout.itemAt(0).widget()
    if isinstance(line_edit, QLineEdit):
      return line_edit.text()
  return ''


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
        widget.setCurrentText('No Value')
      elif isinstance(widget, QDateTimeEdit):
        widget.setDate(QDate.fromString('01/01/0001', 'dd/MM/yyyy'))


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
