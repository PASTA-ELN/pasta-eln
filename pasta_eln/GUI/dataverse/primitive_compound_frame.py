""" Adds a new compound entry. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: primitive_compound_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import QDateTime, QSize

from pasta_eln.GUI.dataverse.primitive_compound_frame_base import Ui_PrimitiveCompoundFrame


def is_date_time_type(type_name):
  return any(
    map(type_name.lower().__contains__, ["date", "time"]))


class PrimitiveCompoundFrame(Ui_PrimitiveCompoundFrame):
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
    self.type_field = type_field
    match self.type_field['typeClass']:
      case "primitive":
        self.populate_primitive_entry()
      case "compound":
        if isinstance(self.type_field['value'], list):
          for compound in self.type_field['value']:
            self.populate_compound_entry(compound)
        else:
          self.populate_compound_entry(self.type_field['value'])
    self.addPushButton.clicked.connect(self.add_new_compound_entry)

  def create_delete_button(self):
    delete_push_button = QtWidgets.QPushButton(parent=self.instance)
    delete_push_button.setText("Delete")
    delete_push_button.setEnabled(False)
    delete_push_button.setObjectName("deletePushButton")
    delete_push_button.setToolTip("Delete this particular entry.")
    size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy(size_policy)
    delete_push_button.setMinimumSize(QSize(100, 0))
    return delete_push_button

  def create_line_edit(self, type_name, type_value):
    entry_line_edit = QtWidgets.QLineEdit(parent=self.instance)
    entry_line_edit.setPlaceholderText(f"Enter the {type_name} here.")
    entry_line_edit.setToolTip(f"Enter the {type_name} value here. e.g. {type_value}")
    entry_line_edit.setClearButtonEnabled(True)
    entry_line_edit.setObjectName("entryLineEdit")
    entry_line_edit.setText(type_value)
    return entry_line_edit

  def create_date_time_widget(self, type_name, type_value):
    date_time_edit = QtWidgets.QDateTimeEdit(parent=self.instance)
    date_time_edit.setToolTip(f"Enter the {type_name} value here. e.g. {type_value}")
    date_time_edit.setObjectName("entryLineEdit")
    date_time_edit.setDateTime(QDateTime.fromString(type_value, 'yyyy-M-d hh:mm:ss'))
    return date_time_edit

  def add_new_compound_entry(self) -> None:
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
    for type_val in self.type_field['value'][0].values():
      type_name = type_val['typeName']
      type_value = type_val['value']
      new_compound_entry_layout.addWidget(
        self.create_date_time_widget(type_val, type_value) if is_date_time_type(type_name) else self.create_line_edit(
          type_val, type_value))
    new_compound_entry_layout.addWidget(self.create_delete_button())
    self.mainVerticalLayout.addLayout(new_compound_entry_layout)

  def populate_compound_entry(self, compound_entry) -> None:
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
      new_compound_entry_layout.addWidget(
        self.create_date_time_widget(compound_type_name, compound_type['value']) if is_date_time_type(compound_type_name) else self.create_line_edit(
          compound_type_name, compound_type['value']))
    new_compound_entry_layout.addWidget(self.create_delete_button())
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
    if self.type_field['multiple']:
      for value in self.type_field['value']:
        new_primitive_entry_horizontal_layout = QtWidgets.QHBoxLayout()
        new_primitive_entry_horizontal_layout.setObjectName("primitiveHorizontalLayout")
        new_primitive_entry_horizontal_layout.addWidget(self.create_line_edit(self.type_field['typeName'], value))
        new_primitive_entry_horizontal_layout.addWidget(self.create_delete_button())
        new_primitive_entry_layout.addLayout(new_primitive_entry_horizontal_layout)
    else:
      new_primitive_entry_horizontal_layout = QtWidgets.QHBoxLayout()
      new_primitive_entry_horizontal_layout.setObjectName("primitiveHorizontalLayout")
      new_primitive_entry_horizontal_layout.addWidget(self.create_date_time_widget(self.type_field['typeName'], self.type_field['value']) if is_date_time_type(
          self.type_field['typeName']) else self.create_line_edit(self.type_field['typeName'],
                                                                  self.type_field['value']))
      new_primitive_entry_horizontal_layout.addWidget(self.create_delete_button())
      new_primitive_entry_layout.addLayout(new_primitive_entry_horizontal_layout)
    self.mainVerticalLayout.addLayout(new_primitive_entry_layout)


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
