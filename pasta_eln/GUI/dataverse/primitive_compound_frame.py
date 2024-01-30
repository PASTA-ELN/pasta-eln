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
from PySide6.QtCore import QSize

from pasta_eln.GUI.dataverse.primitive_compound_frame_base import Ui_PrimitiveCompoundFrame


class PrimitiveCompoundFrame(Ui_PrimitiveCompoundFrame):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    """
    return super(PrimitiveCompoundFrame, cls).__new__(cls)

  def __init__(self, types_dict: dict[str, Any]) -> None:
    """
    Initializes the creation type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QtWidgets.QFrame()
    super().setupUi(self.instance)
    self.types_dict = types_dict
    for type_val in types_dict.values():
      if ("Date" in type_val['typeName']
          or "Time" in type_val['typeName']
          or "time" in type_val['typeName']
          or "date" in type_val['typeName']):
        date_time_edit = QtWidgets.QDateTimeEdit(parent=self.instance)
        date_time_edit.setToolTip(f"Enter the {type_val['typeName']} value here. e.g. {type_val['value']}")
        date_time_edit.setObjectName("entryLineEdit")
        self.compoundHorizontalLayout.addWidget(date_time_edit)
      else:
        entry_line_edit = QtWidgets.QLineEdit(parent=self.instance)
        entry_line_edit.setPlaceholderText(f"Enter the {type_val['typeName']} here.")
        entry_line_edit.setToolTip(f"Enter the {type_val['typeName']} value here. e.g. {type_val['value']}")
        entry_line_edit.setClearButtonEnabled(True)
        entry_line_edit.setObjectName("entryLineEdit")
        self.compoundHorizontalLayout.addWidget(entry_line_edit)
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
    self.compoundHorizontalLayout.addWidget(delete_push_button)
    self.addPushButton.clicked.connect(self.add_new_compound_entry)

  def add_new_compound_entry(self):
    new_compound_entry_layout = QtWidgets.QHBoxLayout()
    new_compound_entry_layout.setObjectName("compoundHorizontalLayout")
    for type_val in self.types_dict.values():
      if ("Date" in type_val['typeName']
          or "Time" in type_val['typeName']
          or "time" in type_val['typeName']
          or "date" in type_val['typeName']):
        date_time_edit = QtWidgets.QDateTimeEdit(parent=self.instance)
        date_time_edit.setToolTip(f"Enter the {type_val['typeName']} value here. e.g. {type_val['value']}")
        date_time_edit.setObjectName("entryLineEdit")
        new_compound_entry_layout.addWidget(date_time_edit)
      else:
        entry_line_edit = QtWidgets.QLineEdit(parent=self.instance)
        entry_line_edit.setPlaceholderText(f"Enter the {type_val['typeName']} here.")
        entry_line_edit.setToolTip(f"Enter the {type_val['typeName']} value here. e.g. {type_val['value']}")
        entry_line_edit.setClearButtonEnabled(True)
        entry_line_edit.setObjectName("entryLineEdit")
        new_compound_entry_layout.addWidget(entry_line_edit)
    delete_push_button = QtWidgets.QPushButton(parent=self.instance)
    delete_push_button.setObjectName("deletePushButton")
    delete_push_button.setText("Delete")
    delete_push_button.setToolTip("Delete this particular entry.")
    size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy(size_policy)
    delete_push_button.setMinimumSize(QSize(100, 0))
    new_compound_entry_layout.addWidget(delete_push_button)
    self.mainVerticalLayout.addLayout(new_compound_entry_layout)


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
