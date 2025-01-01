""" Represents the compound data type class. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: compound_data_type_class.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import copy
import logging
from typing import Any
from PySide6.QtWidgets import QBoxLayout, QHBoxLayout
from pasta_eln.dataverse.utils import clear_value, is_date_time_type
from pasta_eln.GUI.dataverse.data_type_class_base import DataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.utility_functions import (add_clear_button, add_delete_button, create_date_time_widget,
                                                       create_line_edit)


class CompoundDataTypeClass(DataTypeClass):
  """
  Represents the compound data type class.
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the CompoundDataTypeClass class.

    Explanation:
        This method creates a new instance of the CompoundDataTypeClass class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the CompoundDataTypeClass class.

    """
    return super().__new__(cls)

  def __init__(self, context: DataTypeClassContext) -> None:
    """
    Initializes the CompoundDataTypeClass instance with the provided context.

    Args:
      context (DataTypeClassContext): The context for the CompoundDataTypeClass instance.
    """

    super().__init__(context)
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

  def add_new_entry(self) -> None:
    """
    Adds a new entry to the compound data type layout based on the provided value template.

    Args:
      self: The instance of the compound data type class.
    """
    new_compound_entry_layout = QHBoxLayout()
    new_compound_entry_layout.setObjectName('compoundHorizontalLayout')
    value_template = self.context.meta_field.get('valueTemplate', [{}])[0]
    for type_val in value_template.values():
      if (not isinstance(type_val, dict)
          or 'typeName' not in type_val
          or 'value' not in type_val):
        self.logger.warning('Invalid type value in valueTemplate: %s', type_val)
        continue
      type_name = type_val['typeName']
      type_value = type_val['value']
      new_compound_entry_layout.addWidget(
        create_date_time_widget(type_name, '', self.context.parent_frame, type_value)
        if is_date_time_type(type_name) else
        create_line_edit(type_name, '', self.context.parent_frame, type_value))
    add_clear_button(self.context.parent_frame, new_compound_entry_layout)
    add_delete_button(self.context.parent_frame, new_compound_entry_layout)
    self.context.main_vertical_layout.addLayout(new_compound_entry_layout)

  def populate_entry(self) -> None:
    """
    Populates the entry based on the provided value template and value.
    """
    value_template = self.context.meta_field.get('valueTemplate')
    value = self.context.meta_field.get('value')
    if self.context.meta_field['multiple']:
      if isinstance(value, list) and isinstance(value_template, list):
        if len(value) == 0:
          empty_entry = copy.deepcopy(value_template[0])
          clear_value(empty_entry)
          self.populate_compound_entry(empty_entry, value_template[0])
        else:
          for compound in value:
            self.populate_compound_entry(compound, value_template[0])
    else:
      self.context.add_push_button.setDisabled(True)
      if value:
        self.populate_compound_entry(value, value_template, False)
      else:
        empty_entry = copy.deepcopy(value_template)
        clear_value(empty_entry)
        self.populate_compound_entry(empty_entry, value_template, False)

  def save_modifications(self) -> None:
    """
    Saves modifications based on the context's meta-field values.
    """

    if self.context.meta_field.get('multiple'):
      self.context.meta_field['value'].clear()
      for layout_pos in range(self.context.main_vertical_layout.count()):
        compound_horizontal_layout_item = self.context.main_vertical_layout.itemAt(layout_pos)
        if isinstance(compound_horizontal_layout_item, QHBoxLayout):
          value_template = self.context.meta_field.get('valueTemplate', [{}])[0]
          self.save_compound_horizontal_layout_values(
            compound_horizontal_layout_item,
            value_template)
    else:
      self.context.meta_field['value'] = {}
      compound_horizontal_layout = self.context.main_vertical_layout.findChild(QHBoxLayout,
                                                                               'compoundHorizontalLayout')
      if not isinstance(compound_horizontal_layout, QHBoxLayout):
        self.logger.error('Compound horizontal layout not found')
        return
      value_template = self.context.meta_field.get('valueTemplate')
      value_template = value_template if isinstance(value_template, dict) else {}
      self.save_compound_horizontal_layout_values(
        compound_horizontal_layout,
        value_template)

  def save_compound_horizontal_layout_values(self,
                                             compound_horizontal_layout: QBoxLayout,
                                             value_template: dict[str, Any]) -> None:
    """
    Saves the values from the compound horizontal layout to the meta_field.

    Args:
        self: The instance of the class.
        compound_horizontal_layout (QBoxLayout): The compound horizontal layout to save.
        value_template (dict[str, Any]): The template for the compound values.

    Explanation:
        This method saves the values from the compound horizontal layout to the meta_field.
        It iterates over the widgets in the compound horizontal layout and updates the meta_field accordingly.
        The values are extracted from the widgets and stored in the meta_field['value'] attribute.
        If the widget value is empty or None, the corresponding entry in the meta_field is not updated.

    """
    if not compound_horizontal_layout.layout():
      return
    empty_entry = copy.deepcopy(value_template)
    update_needed = False
    layout_items_count = compound_horizontal_layout.count()
    for widget_pos in range(layout_items_count):
      widget = compound_horizontal_layout.itemAt(widget_pos).widget()
      name = widget.objectName().removesuffix('LineEdit').removesuffix('DateTimeEdit')
      if name in empty_entry:
        text = widget.text()  # type: ignore[attr-defined]
        empty_entry[name]['value'] = text if text and text != 'No Value' else ''
        update_needed = bool(update_needed or empty_entry[name]['value'])
    if update_needed:
      if isinstance(self.context.meta_field['value'], dict):
        self.context.meta_field['value'] = {**self.context.meta_field['value'], **empty_entry}
      elif isinstance(self.context.meta_field['value'], list):
        self.context.meta_field['value'].append(empty_entry)
      else:
        self.context.meta_field['value'] = empty_entry

  def populate_compound_entry(self,
                              compound_entry: dict[str, Any],
                              template_entry: dict[str, Any] | None = None,
                              enable_delete_button: bool = True) -> None:
    """
    Populates the compound entry layout based on the compound_entry and template_entry information.

    Args:
        self: The instance of the class.
        compound_entry (dict[str, Any]): The compound entry information.
        template_entry (dict[str, Any] | None, optional): The template entry information. Defaults to None.
        enable_delete_button (bool, optional): Whether to enable the delete button. Defaults to True.

    Explanation:
        This method populates the compound entry layout based on the compound_entry and template_entry information.
        It creates a new QHBoxLayout and adds widgets to it based on the compound_entry values.
        The widgets can be either QDateTimeEdit or QLineEdit, depending on the type of the compound entry.
        The template_entry is used to provide default values for the widgets.
        The new QHBoxLayout is then added to the mainVerticalLayout of the class instance.

    """
    new_compound_entry_layout = QHBoxLayout()
    new_compound_entry_layout.setObjectName('compoundHorizontalLayout')
    for compound_type_name, compound_type in compound_entry.items():
      template_value = template_entry.get(compound_type_name, {}).get('value') if template_entry else None
      new_compound_entry_layout.addWidget(
        create_date_time_widget(compound_type_name, compound_type['value'], self.context.parent_frame, template_value)
        if is_date_time_type(compound_type_name)
        else create_line_edit(compound_type_name, compound_type['value'], self.context.parent_frame, template_value))
    if new_compound_entry_layout.count() > 0:
      add_clear_button(self.context.parent_frame, new_compound_entry_layout)
      add_delete_button(self.context.parent_frame, new_compound_entry_layout,
                        enable_delete_button)
      self.context.main_vertical_layout.addLayout(new_compound_entry_layout)
