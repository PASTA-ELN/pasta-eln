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
import re
from typing import Any, Tuple

from PySide6.QtCore import QEvent
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QMessageBox, QStyleOptionViewItem
from cloudant import CouchDB


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
      return (r.left() < click_x < r.left() + r.width()
              and r.top() < click_y < r.top() + r.height())
  return False


def adjust_ontology_data_to_v3(ontology_types: dict[str, Any]) -> None:
  """Correct the ontology data and add missing information if the loaded data is of version < 3.0

  Args:
      ontology_types (dict[str, Any]): Ontology types loaded from the database

  Returns: None
  """
  if not ontology_types:
    return None
  for _, type_structure in ontology_types.items():
    type_structure.setdefault("attachments", [])
    metadata = type_structure.get("metadata")
    if metadata is None:
      type_structure["metadata"] = {"default": []}
      continue
    if not isinstance(metadata, dict):
      type_structure["metadata"] = {"default": metadata}
  return None


def show_message(message: str,
                 icon: Any = QMessageBox.Information,
                 standard_buttons: Any = QMessageBox.Ok,
                 default_button: Any = QMessageBox.Ok) -> Any:
  """
  Displays a message to the user using QMessageBox
  Args:
    message (str): Message to be displayed
    icon (Any): Message box icon
    standard_buttons (Any): Standard buttons
    default_button (Any): Default button


  Returns: Return None if message is empty otherwise displays the message

  """
  if message:
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Data Hierarchy Editor")
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setIcon(icon)
    msg_box.setText(message)
    msg_box.setStandardButtons(standard_buttons)
    msg_box.setDefaultButton(default_button)
    return msg_box.exec()
  return None


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
      labels = [int(label.replace('x', '').replace('X', ''))
                for label in existing_type_labels if is_structural_level(label)]
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
  return (client[db_name]
          if db_name in client.all_dbs() else client.create_database(db_name))


def get_types_for_display(types: list[str]) -> list[str]:
  """
  Get the types for display by converting all structural types from format: xn -> 'Structure Level n'
  Args:
    types (list[str]): List of types

  Returns: Return the list of types after converting all structural types

  """
  name_prefix = "Structure level "
  return [
    name.replace('x', name_prefix) if is_structural_level(name) else name
    for name in types
  ]


def adapt_type(title: str) -> str:
  """
  Convert only structural type from format: 'Structure Level n' -> xn
  Args:
    title (str): Title to be adapted

  Returns: Adapted title in the needed format

  """
  return title.replace("Structure level ", "x") \
    if title and title.startswith("Structure level ") \
    else title


def is_structural_level(title: str) -> bool:
  """
  Check if the title is a structural type
  Args:
    title (str): Title to be checked

  Returns: True/False

  """
  return re.compile(r'^[Xx][0-9]+$').match(title) is not None


def generate_empty_type(label: str) -> dict[str, Any]:
  """
  Generate an empty type for creating a new ontology type
  Args:
    label (str): Label of the new type

  Returns: Dictionary representing a bare new type

  """
  return {
    "IRI": "",
    "label": label,
    "metadata": {
      "default": generate_mandatory_metadata()
    },
    "attachments": []
  }


def generate_mandatory_metadata() -> list[dict[str, Any]]:
  """
  Generate a list of mandatory metadata for creating a new ontology type
  Returns (list[dict[str, Any]]): List of mandatory metadata

  """
  return [
    {
      "name": "-name",
      "query": "What is the name of the metadata?",
      "mandatory": True
    },
    {
      "name": "-tags",
      "query": "What are the tags associated with this metadata?",
      "mandatory": True
    }
  ]


def check_ontology_types(ontology_types: dict[str, Any]) \
    -> Tuple[dict[str, dict[str, list[str]]], dict[str, list[str]]]:
  """
  Check the ontology data to see if all the mandatory metadata ["-name", "-tags"]
  are present under all groups and also if all the metadata have a name
  Args:
    ontology_types (dict[str, Any]): Ontology types loaded from the database

  Returns (Tuple[dict[str, dict[str, list[str]]], dict[str, str]]):
    Empty tuple if all the mandatory metadata present under all groups and all metadata-item have a name
    otherwise returns a tuple of types with metadata-groups missing mandatory metadata or names

  """
  if not ontology_types:
    return {}, {}
  types_with_missing_metadata: dict[str, dict[str, list[str]]] = {}
  types_with_null_name_metadata: dict[str, list[str]] = {}
  mandatory_metadata = ["-name", "-tags"]
  for type_name, type_structure in ontology_types.items():
    type_name = type_name.replace("x", "Structure level ") \
      if is_structural_level(type_name) \
      else type_name
    if type_structure.get("metadata"):
      for group, metadata in type_structure.get("metadata").items():
        names = [item.get("name") for item in metadata]
        if not all(n and not n.isspace() for n in names):
          if type_name not in types_with_null_name_metadata:
            types_with_null_name_metadata[type_name] = []
          types_with_null_name_metadata[type_name].append(group)
        for req_metadata in mandatory_metadata:
          if req_metadata not in names:
            if type_name not in types_with_missing_metadata:
              types_with_missing_metadata[type_name] = {}
            if group not in types_with_missing_metadata[type_name]:
              types_with_missing_metadata[type_name][group] = []
            types_with_missing_metadata[type_name][group].append(req_metadata)
  return types_with_missing_metadata, types_with_null_name_metadata


def get_missing_metadata_message(types_with_missing_metadata: dict[str, dict[str, list[str]]],
                                 types_with_null_name_metadata: dict[str, list[str]]) -> str:
  """
  Get a formatted message for missing metadata
  Args:
    types_with_null_name_metadata (dict[str, str]): Type groups with missing metadata names
    types_with_missing_metadata (dict[str, dict[str, list[str]]]): Type groups with missing metadata

  Returns (str): Html formatted message

  """
  message = ""
  if (not types_with_missing_metadata
      and not types_with_null_name_metadata):
    return message
  message += "<html>"
  if types_with_missing_metadata:
    message += "<b>Missing mandatory metadata: </b><ul>"
    for type_name, groups in types_with_missing_metadata.items():
      for group, metadata in groups.items():
        for metadata_name in metadata:
          message += (f"<li>Type: <i style=\"color:Crimson\">{type_name}</i>&nbsp;&nbsp;"
                      f"Metadata Group: <i style=\"color:Crimson\">{group}</i>&nbsp;&nbsp;"
                      f"Metadata Name: <i style=\"color:Crimson\">{metadata_name}</i></li>")
    message += "</ul>"
  if types_with_null_name_metadata:
    message += "<b>Missing metadata names:</b><ul>"
    for type_name, groups_list in types_with_null_name_metadata.items():
      for group in groups_list:
        message += (f"<li>Type: <i style=\"color:Crimson\">{type_name}</i>&nbsp;&nbsp;"
                    f"Metadata Group: <i style=\"color:Crimson\">{group}</i></li>")
    message += "</ul>"
  message += "</html>"
  return message


def can_delete_type(existing_types: list[str],
                    selected_type: str) -> bool:
  """
  Check if the selected type can be deleted
    - Non-structural types can be deleted always
    - Structural type 'x0' cannot be deleted at all, the other structural types can
    only be deleted if they are the last one in the hierarchy
  Args:
    existing_types (list[str]): List of existing types
    selected_type (str): Selected type to be deleted

  Returns (bool): True/False depending on whether the selected type can be deleted
  """
  if not selected_type:
    return False
  existing_types = [t for t in existing_types if t]
  if not is_structural_level(selected_type):
    return True
  structural_types = list(filter(is_structural_level, existing_types))
  if selected_type == 'x0':
    return False
  if selected_type not in structural_types:
    return False
  else:
    return max(structural_types) == selected_type
