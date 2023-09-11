""" Utility function used by the ontology configuration module """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6.QtCore import QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QStyleOptionViewItem, QMessageBox
from cloudant import CouchDB
from cloudant.document import Document


def is_click_within_bounds(event: QEvent,
                           option: QStyleOptionViewItem) -> bool:
  """
  Check if the click event happened within the rect area of the QStyleOptionViewItem
  Args:
    event (QEvent): Mouse event captured from the view
    option (QStyleOptionViewItem): Option send during the edit event

  Returns (bool): True/False

  """
  if event and option:
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
      ontology_doc (Document): Ontology document loaded from the database

  Returns: None
  """
  if not ontology_doc:
    return None
  type_structures = {}
  for data in ontology_doc:
    if isinstance(ontology_doc[data], dict):
      type_structures[data] = ontology_doc[data]
  ontology_doc["-version"] = 3
  if type_structures:
    for _, type_structure in type_structures.items():
      type_structure.setdefault("attachments", [])
      props = type_structure.get("prop")
      if props is None:
        type_structure["prop"] = {"default": []}
        continue
      if not isinstance(props, dict):
        type_structure["prop"] = {"default": props}
  return None


def show_message(message: str) -> None:
  """
  Displays a message to the user using QMessageBox
  Args:
    message (str): Message to be displayed

  Returns: Return None if message is empty otherwise displays the message

  """
  if message:
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.exec()


def get_next_possible_structural_level_label(existing_type_labels: Any) -> str | None:
  """
  Get the title for the next possible structural type level
  Args:
    existing_type_labels (Any): The list of labels existing in the ontology document

  Returns (str|None):
    The next possible name is returned with the decimal part greater than the existing largest one
  """
  if existing_type_labels is not None:
    if len(existing_type_labels) > 0:
      import re
      regexp = re.compile(r'^[Xx][0-9]+$')
      labels = [int(label.replace('x', '').replace('X', ''))
                for label in existing_type_labels if regexp.match(label)]
      new_level = max(labels, default=-1)
      return f"x{new_level + 1}"
    else:
      return "x0"
  else:
    return None


def get_db(db_name: str,
           db_user: str,
           db_pass: str,
           db_url: str,
           logger: logging.Logger) -> CouchDB | None:
  """
  Get the db instance for the test purpose
  Args:
    logger (logging): Logger instance
    db_name (str): Database instance name in CouchDB
    db_user (str): Database user-name used for CouchDB access.
    db_pass (str): Database password used for CouchDB access.
    db_url (str): Database connection URL.

  Returns (CouchDB | None):
    Connected DB instance

  """
  try:
    client = CouchDB(user=db_user,
                     auth_token=db_pass,
                     url=db_url,
                     connect=True)
  except Exception as ex:
    if logger:
      logger.error(f'Could not connect with username+password to local server, error: {ex}')
    return None
  if db_name in client.all_dbs():
    db_instance = client[db_name]
  else:
    db_instance = client.create_database(db_name)
  return db_instance
