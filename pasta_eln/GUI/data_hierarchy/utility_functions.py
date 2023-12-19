""" Utility function used by the data hierarchy configuration module """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import copy
import logging
import re
from typing import Any

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


def adjust_data_hierarchy_data_to_v4(data_hierarchy_types: dict[str, Any]) -> None:
  """Correct the data hierarchy data and add missing information if the loaded data is of version < 4.0

  Args:
      data_hierarchy_types (dict[str, Any]): Data hierarchy types loaded from the database

  Returns: None
  """
  if not data_hierarchy_types:
    return None
  for type_structure in data_hierarchy_types.values():
    # Adjustments previous versions <= v3.0
    type_structure.setdefault("attachments", [])
    properties = type_structure.get("prop")
    if properties is None:
      properties = {"default": []}
      type_structure["prop"] = properties
    if not isinstance(properties, dict):
      type_structure["prop"] = {"default": properties}
    # Adjustments for v4.0
    if "prop" in type_structure:
      # replace "meta" with "prop" only if it does not exist
      type_structure.setdefault("meta", type_structure["prop"])
      del type_structure["prop"]
    if "label" in type_structure:
      type_structure.setdefault("title", type_structure["label"])
      del type_structure["label"]
    type_structure.setdefault("title", "")
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


  Returns: Return None if a message is empty otherwise displays the message

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


def get_next_possible_structural_level_title(existing_type_titles: Any) -> str | None:
  """
  Get the title for the next possible structural type level
  Args:
    existing_type_titles (Any): The list of titles existing in the data hierarchy document

  Returns (str|None):
    The next possible name is returned with the decimal part greater than the existing largest one
  """
  if existing_type_titles is None:
    return None
  if len(existing_type_titles) <= 0:
    return "x0"
  titles = [int(title.replace('x', '').replace('X', ''))
            for title in existing_type_titles if is_structural_level(title)]
  new_level = max(titles, default=-1)
  return f"x{new_level + 1}"


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
  Convert only structural-type from format: 'Structure Level n' -> xn
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


def generate_empty_type(displayed_title: str) -> dict[str, Any]:
  """
  Generate an empty type for creating a new data hierarchy type
  Args:
    displayed_title (str): displayed_title of the new type

  Returns: Dictionary representing a bare new type

  """
  return {
    "IRI": "",
    "title": displayed_title,
    "meta": {
      "default": generate_required_metadata()
    },
    "attachments": []
  }


def generate_required_metadata() -> list[dict[str, Any]]:
  """
  Generate a list of required metadata for creating a new data hierarchy type
  Returns (list[dict[str, Any]]): List of required metadata

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
      "mandatory": False
    }
  ]


def check_data_hierarchy_types(data_hierarchy_types: dict[str, Any]) -> tuple[
  dict[str, dict[str, list[str]]],
  dict[str, list[str]],
  dict[str, dict[str, list[str]]]]:
  """
  Check the data hierarchy types to see:
    1. If all the required metadata ["-name", "-tags"] present in default-group
    2. If all the meta-data have name property
    3. If all the meta-data are unique across all groups
  Args:
    data_hierarchy_types (dict[str, Any]): Data hierarchy types loaded from the database

  Returns (tuple[
  dict[str, dict[str, list[str]]],
  dict[str, list[str]],
  dict[str, dict[str, list[str]]]
  ]):
    Empty tuple if all the mandatory metadata present under default group and all meta-data have a name and all meta-data are unique
    Otherwise returns a tuple containing:
      1. Types with metadata-groups missing required metadata
      2. Types with metadata-groups missing names
      3. Types with duplicate metadata name and list of groups where the name is duplicated

  """
  if not data_hierarchy_types:
    return {}, {}, {}
  types_with_null_name_metadata: dict[str, list[str]] = {}
  types_with_missing_metadata: dict[str, dict[str, list[str]]] = {}
  types_with_duplicate_metadata: dict[str, dict[str, list[str]]] = {}
  for type_name, type_value in data_hierarchy_types.items():
    type_name = type_name.replace("x", "Structure level ") \
      if is_structural_level(type_name) \
      else type_name
    if type_value.get("meta"):
      # Check if all required meta-data are present in the default metadata group
      set_types_missing_required_metadata(type_name, type_value, types_with_missing_metadata)
      # Check if all meta-data have a name
      set_types_without_name_in_metadata(type_name, type_value, types_with_null_name_metadata)
      # Check if all meta-data are unique across all groups
      set_types_with_duplicate_metadata(type_name, type_value, types_with_duplicate_metadata)
  return types_with_missing_metadata, types_with_null_name_metadata, types_with_duplicate_metadata


def set_types_missing_required_metadata(type_name: str,
                                        type_value: dict[str, Any],
                                        types_with_missing_metadata: dict[str, dict[str, list[str]]]) -> None:
  """
  Set types and respective groups with missing required metadata in types_with_missing_metadata.
  Args:
    type_name (str): Data hierarchy type name.
    type_value (dict[str, Any]): Data hierarchy type value.
    types_with_missing_metadata (dict[str, dict[str, list[str]]]): Type groups mapping with missing metadata.

  Returns: Nothing

  """
  if not type_name:
    return
  if default_metadata := type_value.get("meta").get("default"):  # type: ignore[union-attr]
    names_in_default_group = [item.get("name") for item in default_metadata]
    required_metadata = ["-name", "-tags"]
    for req_metadata in required_metadata:
      if req_metadata not in names_in_default_group:
        if type_name not in types_with_missing_metadata:
          types_with_missing_metadata[type_name] = {}
        if "default" not in types_with_missing_metadata[type_name]:
          types_with_missing_metadata[type_name]["default"] = []
        types_with_missing_metadata[type_name]["default"].append(req_metadata)


def set_types_without_name_in_metadata(type_name: str,
                                       type_value: dict[str, Any],
                                       types_with_null_name_metadata: dict[str, list[str]]) -> None:
  """
  Set types and respective groups containing metadata with missing name in types_with_null_name_metadata.
  Args:
    type_name (str): Data hierarchy type name.
    type_value (dict[str, Any]): Data hierarchy type value.
    types_with_null_name_metadata (dict[str, list[str]]): Type groups mapping with missing name.

  Returns: Nothing

  """
  if not type_name:
    return
  for group, metadata in type_value.get("meta").items():  # type: ignore[union-attr]
    if metadata:
      names = [item.get("name") for item in metadata]
      if not all(name and not name.isspace() for name in names):
        if type_name not in types_with_null_name_metadata:
          types_with_null_name_metadata[type_name] = []
        types_with_null_name_metadata[type_name].append(group)


def set_types_with_duplicate_metadata(type_name: str,
                                      type_value: dict[str, Any],
                                      types_with_duplicate_metadata: dict[str, dict[str, list[str]]]) -> None:
  """
  Set types and respective groups containing duplicate metadata in types_with_duplicate_metadata.
  Args:
    type_name (str): Data hierarchy type name.
    type_value (dict[str, Any]): Data hierarchy type value.
    types_with_duplicate_metadata (dict[str, dict[str, list[str]]]): Type groups mapping with duplicate metadata.

  Returns: Nothing

  """
  if not type_name:
    return
  metadata_copy = copy.deepcopy(type_value.get("meta"))
  for group, metadata in type_value.get("meta").items():  # type: ignore[union-attr]
    # Check if any duplicate metadata within the same group
    names: list[str] = list(filter(None, [item.get("name") for item in metadata] if metadata else []))
    duplicates: list[str] = [name for name in names if names.count(name) > 1]
    set_duplicates(types_with_duplicate_metadata, type_name, duplicates, group)
    metadata_copy.pop(group)  # type: ignore[union-attr]
    for neighbour_group, neighbour_metadata in metadata_copy.items():  # type: ignore[union-attr]
      # Get all duplicate names after filtering away the empty strings
      duplicates = list({item.get("name") for item in metadata}.intersection(
        [item.get("name") for item in neighbour_metadata]))
      duplicates = list(filter(None, duplicates))
      set_duplicates(types_with_duplicate_metadata, type_name, duplicates, group, neighbour_group)


def set_duplicates(types_with_duplicate_metadata: dict[str, dict[str, list[str]]],
                   type_name: str,
                   duplicates: list[str],
                   group: str,
                   neighbour_group: str = "") -> None:
  """
  Set duplicates in types_with_duplicate_metadata
  Args:
    types_with_duplicate_metadata (dict[str, dict[str, list[str]]]): Type groups with duplicate metadata.
    type_name (str): Data hierarchy type name.
    duplicates (list[str]): List of duplicate metadata names
    group (str): Group name.
    neighbour_group (str, optional): Neighbour group name.

  Returns: Nothing

  """
  for name in duplicates:
    if type_name not in types_with_duplicate_metadata:
      types_with_duplicate_metadata[type_name] = {}
    if name not in types_with_duplicate_metadata[type_name]:
      types_with_duplicate_metadata[type_name][name] = []
    if neighbour_group:
      types_with_duplicate_metadata[type_name][name].extend([group, neighbour_group])
    else:
      types_with_duplicate_metadata[type_name][name].append(group)
    # Remove duplicate groups if any exists
    types_with_duplicate_metadata[type_name][name] \
      = list(set(types_with_duplicate_metadata[type_name][name]))


def get_missing_metadata_message(types_with_missing_metadata: dict[str, dict[str, list[str]]],
                                 types_with_null_name_metadata: dict[str, list[str]],
                                 types_with_duplicate_metadata: dict[str, dict[str, list[str]]]) -> str:
  """
  Get a formatted message for missing metadata
  Args:
    types_with_duplicate_metadata (dict[str, dict[str, list[str]]]): Type groups with duplicate metadata
    types_with_null_name_metadata (dict[str, str]): Type groups with missing metadata names
    types_with_missing_metadata (dict[str, dict[str, list[str]]]): Type groups with missing metadata

  Returns (str): Html formatted message

  """
  message = ""
  if (not types_with_missing_metadata
      and not types_with_null_name_metadata
      and not types_with_duplicate_metadata):
    return message
  message += "<html>"
  message = get_missing_required_metadata_formatted_message(message, types_with_missing_metadata)
  message = get_duplicate_metadata_formatted_message(message, types_with_duplicate_metadata)
  message = get_empty_metadata_name_formatted_message(message, types_with_null_name_metadata)
  message += "</html>"
  return message


def get_empty_metadata_name_formatted_message(message: str,
                                              types_with_null_name_metadata: dict[str, list[str]]) -> str:
  """
  Get html formatted message for missing metadata.
  Args:
    message (str): Html formatted message
    types_with_null_name_metadata (dict[str, list[str]]): Type groups mapping with missing name.

  Returns: Html formatted message for missing metadata name.

  """
  if types_with_null_name_metadata:
    message += "<b>Missing metadata names:</b><ul>"
    for type_name, groups_list in types_with_null_name_metadata.items():
      for group in groups_list:
        message += (f"<li>Type: <i style=\"color:Crimson\">{type_name}</i>&nbsp;&nbsp;"
                    f"Metadata Group: <i style=\"color:Crimson\">{group}</i></li>")
    message += "</ul>"
  return message


def get_missing_required_metadata_formatted_message(message: str,
                                                    types_with_missing_metadata: dict[
                                                      str, dict[str, list[str]]]) -> str:
  """
  Get html formatted message for missing required metadata.
  Args:
    message (str): Html formatted message
    types_with_missing_metadata (dict[str, dict[str, list[str]]]): Type groups mapping with missing required metadata

  Returns: Html formatted message for missing required metadata.

  """
  if types_with_missing_metadata:
    message += "<b>Missing required metadata: </b><ul>"
    for type_name, groups in types_with_missing_metadata.items():
      for group, metadata in groups.items():
        for metadata_name in metadata:
          message += (f"<li>Type: <i style=\"color:Crimson\">{type_name}</i>&nbsp;&nbsp;"
                      f"Metadata Group: <i style=\"color:Crimson\">{group}</i>&nbsp;&nbsp;"
                      f"Metadata Name: <i style=\"color:Crimson\">{metadata_name}</i></li>")
    message += "</ul>"
  return message


def get_duplicate_metadata_formatted_message(message: str,
                                             types_with_duplicate_metadata: dict[str, dict[str, list[str]]]) -> str:
  """
  Get html formatted message for duplicate metadata.
  Args:
    message (str): Html formatted message
    types_with_duplicate_metadata (dict[str, dict[str, list[str]]]): Type groups mapping with duplicate metadata

  Returns: Html formatted message for duplicate metadata.

  """
  if types_with_duplicate_metadata:
    message += "<b>Duplicate metadata found: </b><ul>"
    for type_name, duplicate in types_with_duplicate_metadata.items():
      for metadata_name, groups in duplicate.items():
        for group in groups:
          message += (f"<li>Type: <i style=\"color:Crimson\">{type_name}</i>&nbsp;&nbsp;"
                      f"Metadata Group: <i style=\"color:Crimson\">{group}</i>&nbsp;&nbsp;"
                      f"Metadata Name: <i style=\"color:Crimson\">{metadata_name}</i></li>")
    message += "</ul>"
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
  if selected_type == 'x0':
    return False
  structural_types = list(filter(is_structural_level, existing_types))
  return (False if selected_type not in structural_types else
          max(structural_types) == selected_type)
