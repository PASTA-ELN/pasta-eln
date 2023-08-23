#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6.QtCore import QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QStyleOptionViewItem, QMessageBox
from cloudant.document import Document


def is_click_within_bounds(event: QEvent, option: QStyleOptionViewItem) -> bool:
  """
  Check if the click event happened within the rect area of the QStyleOptionViewItem
  Args:
    event (QEvent): Mouse event captured from the view
    option (QStyleOptionViewItem): Option send during the edit event

  Returns: True/False

  """
  if event.type() == QEvent.MouseButtonRelease:
    e = QMouseEvent(event)
    click_x = e.x()
    click_y = e.y()
    r = option.rect
    if r.left() < click_x < r.left() + r.width():
      if r.top() < click_y < r.top() + r.height():
        return True
  return False


def adjust_ontology_data_to_v3(ontology_doc: Document) -> None:
  """Correct the ontology data and add missing information if the loaded data is of version < 3.0

  Args:
      ontology_doc: Ontology document loaded from the database

  Returns:
      None
  """
  type_structures = dict([(data, ontology_doc[data])
                          for data in ontology_doc
                          if type(ontology_doc[data]) is dict])
  if type_structures:
    for _, type_structure in type_structures.items():
      type_structure.setdefault("attachments", [])
      props = type_structure.get("prop")
      if type(props) is not dict:
        type_structure["prop"] = {"default": props}


def show_message(message: str):
  """
  Displays a message to the user using QMessageBox
  Args:
    message (str): Message to be displayed

  Returns:

  """
  msg_box = QMessageBox()
  msg_box.setText(message)
  msg_box.exec()
