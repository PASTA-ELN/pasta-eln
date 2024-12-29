""" Primitive data type class. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: primitive_data_type_class.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Any

from PySide6.QtWidgets import QBoxLayout, QHBoxLayout, QVBoxLayout

from pasta_eln.GUI.dataverse.data_type_class_base import DataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.utility_functions import add_clear_button, add_delete_button, create_date_time_widget, \
  create_line_edit, get_primitive_line_edit_text_value
from pasta_eln.dataverse.utils import is_date_time_type


class PrimitiveDataTypeClass(DataTypeClass):
  """
  Represents the primitive data type class.
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the PrimitiveDataTypeClass class.

    Explanation:
        This method creates a new instance of the PrimitiveDataTypeClass class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the PrimitiveDataTypeClass class.

    """
    return super(PrimitiveDataTypeClass, cls).__new__(cls)

  def __init__(self, context: DataTypeClassContext) -> None:
    """
    Initializes a new instance of the PrimitiveDataTypeClass.

    Args:
        context (DataTypeClassContext): The context for the PrimitiveDataTypeClass.

    Explanation:
        This method initializes a new instance of the PrimitiveDataTypeClass with the provided context.
    """
    super().__init__(context)
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

  def add_new_entry(self) -> None:
    """
    Adds a new entry to the primitive data type class.

    Explanation:
        This method attempts to find the primitiveVerticalLayout in the main vertical layout.
        If the layout is found, it populates the horizontal layout with the provided type information.
        If the layout is not found, it logs an error message.

    """
    new_primitive_entry_layout = self.context.main_vertical_layout.findChild(QVBoxLayout,
                                                                             'primitiveVerticalLayout')
    if not isinstance(new_primitive_entry_layout, QVBoxLayout):
      self.logger.error('Failed to find primitiveVerticalLayout!')
      return
    value_template = self.context.meta_field.get('valueTemplate')
    first_value = str(value_template[0]) if value_template else ''
    self.populate_primitive_horizontal_layout(
      new_primitive_entry_layout,
      self.context.meta_field.get('typeName', ''),
      '',
      first_value)

  def populate_entry(self) -> None:
    """
    Populates the entry based on the meta_field information.

    Explanation:
        This method populates the entry based on the meta_field information.
        It disables the add push button if the meta_field does not have multiple entries.
        It then calls the populate_primitive_entry method to populate the entry.
    """
    if not self.context.meta_field.get('multiple'):
      self.context.add_push_button.setDisabled(True)
    self.populate_primitive_entry()

  def save_modifications(self) -> None:
    """
    Saves modifications to the meta_field based on the type and class.

    Explanation:
        This method saves changes to the meta_field based on the type and class information.
        It retrieves the primitiveVerticalLayout and updates the meta_field value accordingly.
    """
    self.logger.info('Saving changes to meta_field for type, name: %s, class: %s',
                     self.context.meta_field.get('typeName'),
                     self.context.meta_field.get('typeClass'))
    primitive_vertical_layout = self.context.main_vertical_layout.findChild(QVBoxLayout,
                                                                            'primitiveVerticalLayout')
    if primitive_vertical_layout is None:
      return
    if isinstance(primitive_vertical_layout, QVBoxLayout):
      if self.context.meta_field.get('multiple'):
        self.context.meta_field['value'].clear()
        for widget_pos in range(primitive_vertical_layout.count()):
          text = get_primitive_line_edit_text_value(primitive_vertical_layout, widget_pos)
          if text and text != 'No Value':
            self.context.meta_field['value'].append(text)
      else:
        text = get_primitive_line_edit_text_value(primitive_vertical_layout, 0)
        self.context.meta_field['value'] = text if text != 'No Value' else ''
    else:
      self.logger.error('Failed to find primitiveVerticalLayout!')

  def populate_primitive_entry(self) -> None:
    """
    Populates the primitive entry layout based on the meta_field information.

    Explanation:
        This method populates the primitive entry layout based on the meta_field information.
        It creates a new QVBoxLayout and adds widgets to it based on the meta_field values.
        The widgets are created using the create_primitive_widget function.
        The new QVBoxLayout is then added to the mainVerticalLayout of the class instance.

    """
    type_value = self.context.meta_field.get('value')
    type_name = self.context.meta_field.get('typeName', '')
    value_template = self.context.meta_field.get('valueTemplate')

    self.logger.info('Populating new entry of type primitive, name: %s', type_name)

    new_primitive_entry_layout = QVBoxLayout()
    new_primitive_entry_layout.setObjectName('primitiveVerticalLayout')
    if self.context.meta_field.get('multiple') and isinstance(type_value, list):
      template_first = value_template[0] if isinstance(value_template, list) else ''
      if not type_value:
        self.populate_primitive_horizontal_layout(
          new_primitive_entry_layout,
          type_name,
          '',
          template_first)
      else:
        for value in type_value:
          self.populate_primitive_horizontal_layout(
            new_primitive_entry_layout,
            type_name,
            value,
            template_first)
    else:
      self.populate_primitive_horizontal_layout(
        new_primitive_entry_layout,
        type_name,
        type_value or '',
        value_template if isinstance(value_template, str) else '',
        False)
    self.context.main_vertical_layout.addLayout(new_primitive_entry_layout)

  def populate_primitive_horizontal_layout(self,
                                           new_primitive_entry_layout: QBoxLayout,
                                           type_name: str,
                                           type_value: str,
                                           type_value_template: str,
                                           enable_delete_button: bool = True) -> None:
    """
    Populates the horizontal layout for a primitive entry.

    Args:
        enable_delete_button (bool): Enable or disable the delete button.
        new_primitive_entry_layout (QBoxLayout): The layout to populate.
        type_name (str): The name of the primitive type.
        type_value (str): The value of the primitive type.
        type_value_template (str): The template value for the primitive type.

    Explanation:
        This function populates the horizontal layout for a primitive entry.
        It creates a new QHBoxLayout and adds widgets to it based on the provided type_name, type_value, and type_value_template.
        The widgets can be either a QDateTimeEdit or a QLineEdit, depending on the type_name.
        The new QHBoxLayout is then added to the new_primitive_entry_layout, which is added to the main layout.

    """
    new_primitive_entry_horizontal_layout = QHBoxLayout()
    new_primitive_entry_horizontal_layout.setObjectName('primitiveHorizontalLayout')
    new_primitive_entry_horizontal_layout.addWidget(
      create_date_time_widget(type_name, type_value, self.context.parent_frame, type_value_template)
      if is_date_time_type(type_name) else
      create_line_edit(type_name, type_value, self.context.parent_frame, type_value_template))
    add_clear_button(self.context.parent_frame, new_primitive_entry_horizontal_layout)
    add_delete_button(self.context.parent_frame, new_primitive_entry_horizontal_layout, enable_delete_button)
    new_primitive_entry_layout.addLayout(new_primitive_entry_horizontal_layout)
