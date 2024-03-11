""" Adds a new compound entry. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: primitive_compound_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import copy
import logging
from typing import Any

from PySide6.QtCore import QDateTime, QSize
from PySide6.QtWidgets import QBoxLayout, QDateTimeEdit, QFrame, QHBoxLayout, QLineEdit, QPushButton, \
  QSizePolicy, \
  QVBoxLayout

from pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base import Ui_PrimitiveCompoundControlledFrameBase
from pasta_eln.dataverse.utils import adjust_type_name, clear_value, delete_layout_and_contents, is_date_time_type


class PrimitiveCompoundFrame(Ui_PrimitiveCompoundControlledFrameBase):
  """
  Adds a new compound entry.

  Explanation:
      This method adds a new compound entry to the UI.
      It creates a new layout for the entry and adds the appropriate UI elements based on the types dictionary.

  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the PrimitiveCompoundFrame class.

    Explanation:
        This method creates a new instance of the PrimitiveCompoundFrame class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the PrimitiveCompoundFrame class.
    """
    return super(PrimitiveCompoundFrame, cls).__new__(cls)

  def __init__(self, meta_field: dict[str, Any]) -> None:
    """
    Initializes the PrimitiveCompoundFrame.

    Explanation:
        This method initializes the PrimitiveCompoundFrame class.
        It sets up the UI and initializes the types dictionary.

    Args:
        meta_field (dict[str, Any]): The dictionary containing the metadata field information.
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QFrame()
    super().setupUi(self.instance)
    self.meta_field = meta_field
    self.addPushButton.clicked.connect(self.add_new_entry)
    self.load_ui()

  def load_ui(self):
    """
    Loads the UI based on the meta_field information.

    Args:
        self: The instance of the class.

    Explanation:
        This method loads the UI based on the meta_field information.
        It handles different cases based on the 'typeClass' value in the meta_field dictionary.
        - For 'primitive' type, it disables the addPushButton if 'multiple' is False and populates the primitive entry.
        - For 'compound' type, it handles the cases of 'multiple' being True or False.
          - If 'multiple' is True and the 'value' is empty, it creates an empty entry and populates the compound entry.
          - If 'multiple' is True and the 'value' is not empty, it populates the compound entry for each compound in the 'value'.
          - If 'multiple' is False and the 'value' is not empty, it populates the compound entry with the 'value'.
          - If 'multiple' is False and the 'value' is empty, it creates an empty entry and populates the compound entry.
        - For any other 'typeClass' value, it logs an error for unknown typeClass.

    """
    self.logger.info("Loading UI for %s", self.meta_field)
    match self.meta_field.get('typeClass'):
      case "primitive":
        if not self.meta_field.get('multiple'):
          self.addPushButton.setDisabled(True)
        self.populate_primitive_entry()
      case "compound":
        value_template = self.meta_field.get('valueTemplate')
        value = self.meta_field.get('value')
        if self.meta_field['multiple']:
          if len(value) == 0:
            empty_entry = copy.deepcopy(value_template[0])
            clear_value(empty_entry)
            self.populate_compound_entry(empty_entry, value_template[0])
          else:
            for compound in value:
              self.populate_compound_entry(compound, value_template[0])
        else:
          self.addPushButton.setDisabled(True)
          if value:
            self.populate_compound_entry(value, value_template)
          else:
            empty_entry = copy.deepcopy(value_template)
            clear_value(empty_entry)
            self.populate_compound_entry(empty_entry, value_template)
      case _:
        self.logger.error("Unknown typeClass: %s", self.meta_field.get('typeClass'))

  def create_delete_button(self,
                           parent: QBoxLayout,
                           enabled: bool = True) -> QPushButton:
    """
    Creates a delete button widget.

    Args:
        parent (QBoxLayout): The parent QBoxLayout object.
        enabled (bool, optional): Whether the button should be enabled or disabled.
        Defaults to True.

    Returns:
        QPushButton: The created delete button widget.

    Explanation:
        This function creates a QPushButton widget with the specified properties.
        The button is labeled as "Delete" and can be enabled or disabled based on the 'enabled' parameter.
        It is connected to a lambda function that calls the 'delete' function with the parent QBoxLayout as an argument.

    """
    delete_push_button = QPushButton(parent=self.instance)
    delete_push_button.setText("Delete")
    delete_push_button.setEnabled(enabled)
    delete_push_button.setObjectName("deletePushButton")
    delete_push_button.setToolTip("Delete this particular entry.")
    size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy(size_policy)
    delete_push_button.setMinimumSize(QSize(100, 0))
    delete_push_button.clicked.connect(lambda _: delete_layout_and_contents(parent))
    return delete_push_button

  def create_line_edit(self,
                       type_name: str,
                       type_value: str,
                       template_value: str | None = None) -> QLineEdit:
    """
    Creates a line edit widget.

    Args:
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
    entry_line_edit = QLineEdit(parent=self.instance)
    adjusted_name = adjust_type_name(type_name)
    entry_line_edit.setPlaceholderText(f"Enter the {adjusted_name} here.")
    entry_line_edit.setToolTip(f"Enter the {adjusted_name} value here. e.g. {template_value}")
    entry_line_edit.setClearButtonEnabled(True)
    entry_line_edit.setObjectName(f"{type_name}LineEdit")
    entry_line_edit.setText(type_value)
    return entry_line_edit

  def create_date_time_widget(self,
                              type_name: str,
                              type_value: str,
                              template_value: str | None = None) -> QDateTimeEdit:
    """
    Creates a date-time edit widget.

    Args:
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
    date_time_edit = QDateTimeEdit(parent=self.instance)
    adjusted_name = adjust_type_name(type_name)
    date_time_edit.setToolTip(f"Enter the {adjusted_name} value here. e.g. {template_value}")
    date_time_edit.setObjectName(f"{type_name}LineEdit")
    date_time_edit.setDateTime(QDateTime.fromString(type_value, 'yyyy-MM-dd'))
    date_time_edit.setDisplayFormat('yyyy-MM-dd')
    return date_time_edit

  def add_new_entry(self) -> None:
    """
        Adds a new entry based on the meta_field information.

        Explanation:
            This method adds a new entry based on the meta_field information.
            It handles different cases based on the 'typeClass' value in the meta_field dictionary.
            - For 'primitive' type, it populates the primitive horizontal layout with the specified values.
            - For 'compound' type, it creates a new compound horizontal layout and populates it with the specified values.
            - For any other 'typeClass' value, it logs an error for unknown typeClass.

    """
    type_name = self.meta_field.get('typeName')
    type_class = self.meta_field.get('typeClass')
    self.logger.info("Adding new entry of type %s, name: %s", type_class, type_name)
    if not self.meta_field.get('multiple'):
      self.logger.error("Add operation not supported for non-multiple entries")
      return
    match type_class:
      case "primitive":
        new_primitive_entry_layout = self.mainVerticalLayout.findChild(QVBoxLayout,
                                                                       "primitiveVerticalLayout")
        self.populate_primitive_horizontal_layout(
          new_primitive_entry_layout,
          type_name,
          "",
          self.meta_field.get('valueTemplate')[0])
      case "compound":
        new_compound_entry_layout = QHBoxLayout()
        new_compound_entry_layout.setObjectName("compoundHorizontalLayout")
        for type_val in self.meta_field.get('valueTemplate')[0].values():
          type_name = type_val.get('typeName')
          type_value = type_val.get('value')
          new_compound_entry_layout.addWidget(
            self.create_date_time_widget(type_name, '', type_value)
            if is_date_time_type(type_name) else
            self.create_line_edit(type_name, '', type_value))
        new_compound_entry_layout.addWidget(self.create_delete_button(new_compound_entry_layout))
        self.mainVerticalLayout.addLayout(new_compound_entry_layout)
      case _:
        self.logger.error("Unknown type class: %s", type_class)

  def populate_compound_entry(self,
                              compound_entry: dict[str, Any],
                              template_entry: dict[str, Any] | None = None) -> None:
    """
    Populates the compound entry layout based on the compound_entry and template_entry information.

    Args:
        self: The instance of the class.
        compound_entry (dict[str, Any]): The compound entry information.
        template_entry (dict[str, Any] | None, optional): The template entry information. Defaults to None.

    Explanation:
        This method populates the compound entry layout based on the compound_entry and template_entry information.
        It creates a new QHBoxLayout and adds widgets to it based on the compound_entry values.
        The widgets can be either QDateTimeEdit or QLineEdit, depending on the type of the compound entry.
        The template_entry is used to provide default values for the widgets.
        The new QHBoxLayout is then added to the mainVerticalLayout of the class instance.

    """
    new_compound_entry_layout = QHBoxLayout()
    new_compound_entry_layout.setObjectName("compoundHorizontalLayout")
    for compound_type_name, compound_type in compound_entry.items():
      template_value = template_entry.get(compound_type_name, {}).get('value')
      new_compound_entry_layout.addWidget(
        self.create_date_time_widget(compound_type_name, compound_type['value'], template_value)
        if is_date_time_type(compound_type_name)
        else self.create_line_edit(compound_type_name, compound_type['value'], template_value))
    if new_compound_entry_layout.count() > 0:
      new_compound_entry_layout.addWidget(self.create_delete_button(new_compound_entry_layout))
      self.mainVerticalLayout.addLayout(new_compound_entry_layout)

  def populate_primitive_entry(self) -> None:
    """
    Populates the primitive entry layout based on the meta_field information.

    Explanation:
        This method populates the primitive entry layout based on the meta_field information.
        It creates a new QVBoxLayout and adds widgets to it based on the meta_field values.
        The widgets are created using the create_primitive_widget function.
        The new QVBoxLayout is then added to the mainVerticalLayout of the class instance.

    """
    type_value = self.meta_field.get('value')
    type_name = self.meta_field.get('typeName')
    type_template = self.meta_field.get('valueTemplate')

    self.logger.info("Populating new entry of type primitive, name: %s", type_name)

    new_primitive_entry_layout = QVBoxLayout()
    new_primitive_entry_layout.setObjectName("primitiveVerticalLayout")
    if self.meta_field.get('multiple'):
      if len(type_value) == 0:
        self.populate_primitive_horizontal_layout(
          new_primitive_entry_layout,
          type_name,
          "",
          type_template[0])
      else:
        for value in type_value:
          self.populate_primitive_horizontal_layout(
            new_primitive_entry_layout,
            type_name,
            value,
            type_template[0])
    else:
      self.populate_primitive_horizontal_layout(
        new_primitive_entry_layout,
        type_name,
        type_value,
        type_template,
        False)
    self.mainVerticalLayout.addLayout(new_primitive_entry_layout)

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
    new_primitive_entry_horizontal_layout.setObjectName("primitiveHorizontalLayout")
    new_primitive_entry_horizontal_layout.addWidget(
      self.create_date_time_widget(type_name, type_value, type_value_template)
      if is_date_time_type(type_name) else
      self.create_line_edit(type_name, type_value, type_value_template))
    new_primitive_entry_horizontal_layout.addWidget(
      self.create_delete_button(new_primitive_entry_horizontal_layout, enable_delete_button))
    new_primitive_entry_layout.addLayout(new_primitive_entry_horizontal_layout)

  def save_modifications(self):
    """
    Saves the changes made in UI elements to the meta_field.

    Args:
        self: The instance of the class.

    Explanation:
        This method saves the changes made to the meta_field.
        It handles different cases based on the 'typeClass' value in the meta_field dictionary.
        - For 'primitive' type, it updates the 'value' attribute of the meta_field.
        - For 'compound' type, it updates the 'value' attribute of the meta_field based on the 'valueTemplate'.
        - For any other 'typeClass' value, it logs an error for unsupported typeClass.
    """
    self.logger.info("Saving changes to meta_field for type, name: %s, class: %s",
                     self.meta_field.get('typeName'),
                     self.meta_field.get('typeClass'))
    match self.meta_field.get('typeClass'):
      case "primitive":
        primitive_vertical_layout = self.mainVerticalLayout.findChild(QVBoxLayout,
                                                                      "primitiveVerticalLayout")
        if self.meta_field.get('multiple'):
          self.meta_field['value'].clear()
          for widget_pos in range(primitive_vertical_layout.count()):
            if text := primitive_vertical_layout.itemAt(widget_pos).itemAt(0).widget().text():
              self.meta_field['value'].append(text)
        else:
          self.meta_field['value'] = primitive_vertical_layout.itemAt(0).itemAt(0).widget().text()
      case "compound":
        if self.meta_field.get('multiple'):
          self.meta_field['value'].clear()
          for layout_pos in range(self.mainVerticalLayout.count()):
            compound_horizontal_layout = self.mainVerticalLayout.itemAt(layout_pos)
            self.save_compound_horizontal_layout_values(
              compound_horizontal_layout,
              self.meta_field.get('valueTemplate')[0])
        else:
          self.meta_field['value'] = {}
          compound_horizontal_layout = self.mainVerticalLayout.findChild(QHBoxLayout,
                                                                         "compoundHorizontalLayout")
          self.save_compound_horizontal_layout_values(
            compound_horizontal_layout,
            self.meta_field.get('valueTemplate'))
      case _:
        self.logger.error("Unsupported typeClass: %s", self.meta_field.get('typeClass'))

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
    if compound_horizontal_layout.layout():
      empty_entry = copy.deepcopy(value_template)
      update_needed = False
      layout_items_count = compound_horizontal_layout.count()
      for widget_pos in range(layout_items_count):
        widget = compound_horizontal_layout.itemAt(widget_pos).widget()
        name = widget.objectName().removesuffix("LineEdit")
        if name in empty_entry:
          text = widget.text()
          empty_entry[name]['value'] = text
          update_needed = update_needed or (text != "" and text is not None)
      if update_needed:
        self.meta_field['value'].append(empty_entry)
