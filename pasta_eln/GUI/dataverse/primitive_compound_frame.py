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

from PySide6 import QtWidgets
from PySide6.QtCore import QDateTime, QSize

from pasta_eln.GUI.dataverse.primitive_compound_controller_frame_base import Ui_PrimitiveCompoundControlledBaseFrame


def is_date_time_type(type_name):
  return any(
    map(type_name.lower().__contains__, ["date", "time"]))


def clear_value(item: dict[str, Any] = None):
  for i in item.values():
    i['value'] = None


def delete(layout):
  for widget_pos in reversed(range(layout.count())):
    if item := layout.itemAt(widget_pos):
      item.widget().setParent(None)
  layout.setParent(None)


class PrimitiveCompoundFrame(Ui_PrimitiveCompoundControlledBaseFrame):
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

  def __init__(self, type_field: dict[str, Any]) -> None:
    """
    Initializes the PrimitiveCompoundFrame.

    Explanation:
        This method initializes the PrimitiveCompoundFrame class.
        It sets up the UI and initializes the types dictionary.

    Args:
        type_field (dict[str, Any]): The dictionary containing the types information.

    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QtWidgets.QFrame()
    super().setupUi(self.instance)
    self.meta_field = type_field
    match self.meta_field['typeClass']:
      case "primitive":
        if not self.meta_field['multiple']:
          self.addPushButton.setDisabled(True)
        self.populate_primitive_entry()
      case "compound":
        if self.meta_field['multiple']:
          if len(self.meta_field['value']) == 0:
            empty_entry = copy.deepcopy(self.meta_field['valueTemplate'][0])
            clear_value(empty_entry)
            self.populate_compound_entry(empty_entry, self.meta_field['valueTemplate'][0])
          else:
            for compound in self.meta_field['value']:
              self.populate_compound_entry(compound, self.meta_field['valueTemplate'][0])
        else:
          self.addPushButton.setDisabled(True)
          if self.meta_field['value']:
            self.populate_compound_entry(self.meta_field['value'], self.meta_field['valueTemplate'])
          else:
            empty_entry = copy.deepcopy(self.meta_field['valueTemplate'])
            clear_value(empty_entry)
            self.populate_compound_entry(empty_entry, self.meta_field['valueTemplate'])
    self.addPushButton.clicked.connect(self.add_new_entry)

  def create_delete_button(self, parent, enabled=True):
    delete_push_button = QtWidgets.QPushButton()
    delete_push_button.setText("Delete")
    delete_push_button.setEnabled(enabled)
    delete_push_button.setObjectName("deletePushButton")
    delete_push_button.setToolTip("Delete this particular entry.")
    size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy(size_policy)
    delete_push_button.setMinimumSize(QSize(100, 0))
    delete_push_button.clicked.connect(lambda _: delete(parent))
    return delete_push_button

  def create_line_edit(self, type_name, type_value, template_value=None):
    entry_line_edit = QtWidgets.QLineEdit(parent=self.instance)
    entry_line_edit.setPlaceholderText(f"Enter the {type_name} here.")
    entry_line_edit.setToolTip(f"Enter the {type_name} value here. e.g. {template_value}")
    entry_line_edit.setClearButtonEnabled(True)
    entry_line_edit.setObjectName(f"{type_name}LineEdit")
    entry_line_edit.setText(type_value)
    return entry_line_edit

  def create_date_time_widget(self, type_name, type_value, template_value=None):
    date_time_edit = QtWidgets.QDateTimeEdit(parent=self.instance)
    date_time_edit.setToolTip(f"Enter the {type_name} value here. e.g. {template_value}")
    date_time_edit.setObjectName(f"{type_name}LineEdit")
    date_time_edit.setDateTime(QDateTime.fromString(type_value, 'yyyy-MM-dd'))
    date_time_edit.setDisplayFormat('yyyy-MM-dd')
    return date_time_edit

  def add_new_entry(self) -> None:
    """
    Adds a new compound entry.

    Explanation:
        This method adds a new compound entry to the UI.
        It creates a new layout for the entry and adds the appropriate UI elements based on the types dictionary.

    Args:
        None

    """
    match self.meta_field['typeClass']:
      case "primitive":
        if self.meta_field['multiple']:
          new_primitive_entry_layout = self.mainVerticalLayout.findChild(QtWidgets.QVBoxLayout,
                                                                         "primitiveVerticalLayout")
          self.populate_primitive_horizontal_layout(
            new_primitive_entry_layout,
            self.meta_field['typeName'],
            "",
            self.meta_field['valueTemplate'][0])
        else:
          self.logger.error("Add operation not supported for primitive type with multiple set to False.")
      case "compound":
        new_compound_entry_layout = QtWidgets.QHBoxLayout()
        new_compound_entry_layout.setObjectName("compoundHorizontalLayout")
        for type_val in self.meta_field['valueTemplate'][0].values():
          type_name = type_val['typeName']
          type_value = type_val['value']
          new_compound_entry_layout.addWidget(
            self.create_date_time_widget(type_name, '', type_value) if is_date_time_type(
              type_name) else self.create_line_edit(
              type_name, '', type_value))
        new_compound_entry_layout.addWidget(self.create_delete_button(new_compound_entry_layout))
        self.mainVerticalLayout.addLayout(new_compound_entry_layout)
      case _:
        self.logger.error(f"Unknown type class: {self.meta_field['typeClass']}")

  def populate_compound_entry(self, compound_entry, template_entry=None) -> None:
    """
    Adds a new compound entry.

    Explanation:
        This method adds a new compound entry to the UI.
        It creates a new layout for the entry and adds the appropriate UI elements based on the types dictionary.

    Args:
        None

    """
    new_compound_entry_layout = QtWidgets.QHBoxLayout()
    new_compound_entry_layout.setObjectName("compoundHorizontalLayout")
    for compound_type_name, compound_type in compound_entry.items():
      template_value = template_entry[compound_type_name]['value']
      new_compound_entry_layout.addWidget(
        self.create_date_time_widget(compound_type_name, compound_type['value'], template_value) if is_date_time_type(
          compound_type_name) else self.create_line_edit(
          compound_type_name, compound_type['value'], template_value))
    new_compound_entry_layout.addWidget(self.create_delete_button(new_compound_entry_layout))
    if new_compound_entry_layout.count() > 0:
      self.mainVerticalLayout.addLayout(new_compound_entry_layout)

  def populate_primitive_entry(self) -> None:
    """
    Adds a new compound entry.

    Explanation:
        This method adds a new compound entry to the UI.
        It creates a new layout for the entry and adds the appropriate UI elements based on the types dictionary.

    Args:
        None

    """
    new_primitive_entry_layout = QtWidgets.QVBoxLayout()
    new_primitive_entry_layout.setObjectName("primitiveVerticalLayout")
    if self.meta_field['multiple']:
      if len(self.meta_field['value']) == 0:
        self.populate_primitive_horizontal_layout(
          new_primitive_entry_layout,
          self.meta_field['typeName'],
          "",
          self.meta_field['valueTemplate'][0])
      else:
        for value in self.meta_field['value']:
          self.populate_primitive_horizontal_layout(
            new_primitive_entry_layout,
            self.meta_field['typeName'],
            value,
            self.meta_field['valueTemplate'][0])
    else:
      self.populate_primitive_horizontal_layout(
        new_primitive_entry_layout,
        self.meta_field['typeName'],
        self.meta_field['value'],
        self.meta_field['valueTemplate'])
    self.mainVerticalLayout.addLayout(new_primitive_entry_layout)

  def populate_primitive_horizontal_layout(self, new_primitive_entry_layout, type_name, type_value,
                                           type_value_template):
    new_primitive_entry_horizontal_layout = QtWidgets.QHBoxLayout()
    new_primitive_entry_horizontal_layout.setObjectName("primitiveHorizontalLayout")
    new_primitive_entry_horizontal_layout.addWidget(
      self.create_date_time_widget(type_name, type_value, type_value_template) if is_date_time_type(
        type_name) else self.create_line_edit(type_name, type_value, type_value_template))
    new_primitive_entry_horizontal_layout.addWidget(
      self.create_delete_button(new_primitive_entry_horizontal_layout, False))
    new_primitive_entry_layout.addLayout(new_primitive_entry_horizontal_layout)

  def save_modifications(self):
    match self.meta_field['typeClass']:
      case "primitive":
        primitive_vertical_layout = self.mainVerticalLayout.findChild(QtWidgets.QVBoxLayout,
                                                                      "primitiveVerticalLayout")
        if self.meta_field['multiple']:
          self.meta_field['value'].clear()
          for widget_pos in range(primitive_vertical_layout.count()):
            if text := primitive_vertical_layout.itemAt(widget_pos).itemAt(0).widget().text():
              self.meta_field['value'].append(text)
        else:
          self.meta_field['value'] = primitive_vertical_layout.itemAt(0).itemAt(0).widget().text()
      case "compound":
        if self.meta_field['multiple']:
          self.meta_field['value'].clear()
          for layout_pos in range(self.mainVerticalLayout.count()):
            compound_horizontal_layout = self.mainVerticalLayout.itemAt(layout_pos)
            self.save_compound_horizontal_layout_values(compound_horizontal_layout, self.meta_field['valueTemplate'][0])
        else:
          self.meta_field['value'] = {}
          compound_horizontal_layout = self.mainVerticalLayout.findChild(QtWidgets.QHBoxLayout,
                                                                         "compoundHorizontalLayout")
          self.save_compound_horizontal_layout_values(compound_horizontal_layout, self.meta_field['valueTemplate'])

  def save_compound_horizontal_layout_values(self, compound_horizontal_layout, value_template):
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

  def clear_main_layout(self):
    for widget_pos in range(self.mainVerticalLayout.count()):
      child = self.mainVerticalLayout.itemAt(widget_pos)
      if child and child.layout():
        for pos in range(child.count()):
          in_child = child.itemAt(pos)
          if in_child and in_child.layout():
            for in_pos in range(in_child.count()):
              in_in_child = in_child.itemAt(in_pos)
              if in_in_child and in_in_child.widget():
                in_in_child.widget().setParent(None)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = PrimitiveCompoundFrame({
    "authorName": {
      "typeName": "authorName",
      "multiple": False,
      "typeClass": "primitive",
      "value": "LastAuthor1, FirstAuthor1"
    },
    "authorAffiliation": {
      "typeName": "authorAffiliation",
      "multiple": False,
      "typeClass": "primitive",
      "value": "AuthorAffiliation1"
    },
    "authorIdentifierScheme": {
      "typeName": "authorIdentifierScheme",
      "multiple": False,
      "typeClass": "controlledVocabulary",
      "value": "ORCID"
    },
    "authorIdentifier": {
      "typeName": "authorIdentifier",
      "multiple": False,
      "typeClass": "primitive",
      "value": "AuthorIdentifier1"
    }
  })
  ui.instance.show()
  sys.exit(app.exec())
