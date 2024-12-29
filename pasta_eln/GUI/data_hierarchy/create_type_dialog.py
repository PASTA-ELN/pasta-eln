"""A dialog for creating a new data type within the application."""
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: create_type_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any, Callable

from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox

from pasta_eln.GUI.data_hierarchy.generic_exception import GenericException
from pasta_eln.GUI.data_hierarchy.type_dialog import TypeDialog
from pasta_eln.GUI.data_hierarchy.utility_functions import generate_data_hierarchy_type, show_message


class CreateTypeDialog(TypeDialog):
  """
  A dialog for creating a new data type within the application.

  This class extends the TypeDialog to provide functionality for adding new data types.
  It initializes the dialog with specific UI elements and behavior tailored for creating new types.

  Args:
      accepted_callback (Callable[[], None]): A callback function to be executed when the action is accepted.
      rejected_callback (Callable[[], None]): A callback function to be executed when the action is rejected.
  """

  def __init__(self,
               accepted_callback: Callable[[], None],
               rejected_callback: Callable[[], None]):
    """
    Initializes a new instance of the class with specified callback functions.

    This constructor sets up the instance by initializing the parent class and configuring the logger.
    It also initializes an empty dictionary for data hierarchy types and sets the window title for the dialog.

    Args:
        accepted_callback (Callable[[], None]): A callback function to be executed when the action is accepted.
        rejected_callback (Callable[[], None]): A callback function to be executed when the action is rejected.
    """
    super().__init__(accepted_callback, rejected_callback)
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.data_hierarchy_types: dict[str, Any] = {}
    self.instance.setWindowTitle('Create new type')

  def accepted_callback(self) -> None:
    """
    Handles the acceptance of a new data type by validating input and updating the data hierarchy.

    This method checks if the type information is valid and whether the data type already exists in the hierarchy.
    If the type is valid and does not exist, it logs the creation of the new type, updates the data hierarchy,
    and closes the dialog. If the type already exists, it shows a warning message. If the data hierarchy types
    are null, it logs an error and raises an exception.

    Raises:
        GenericException: If the data hierarchy types are null.
    """
    if not self.validate_type_info():
      return
    if self.data_hierarchy_types is None:
      self.logger.error('Null data_hierarchy_types, erroneous app state')
      raise GenericException('Null data_hierarchy_types, erroneous app state', {})
    if self.type_info.datatype in self.data_hierarchy_types:
      self.logger.error(
        'Type (datatype: {%s} displayed title: {%s}) cannot be added since it exists in DB already....',
        self.type_info.datatype,
        self.type_info.title
      )
      show_message(
        f"Type (datatype: {self.type_info.datatype} displayed title: {self.type_info.title}) cannot be added since it exists in DB already....",
        QMessageBox.Icon.Warning)
    else:
      self.logger.info('User created a new type and added '
                       'to the data_hierarchy document: Datatype: {%s}, Displayed Title: {%s}',
                       self.type_info.datatype,
                       self.type_info.title)
      if isinstance(self.type_info.datatype, str):
        self.data_hierarchy_types[self.type_info.datatype] = generate_data_hierarchy_type(self.type_info)
      self.instance.close()
      self.accepted_callback_parent()

  def rejected_callback(self) -> None:
    """
     Calls the parent rejection callback method.

     This method is intended to handle the rejection of a dialog or action by invoking
     the corresponding parent method that manages the rejection behavior. It does not
     perform any additional logic or checks.
     """
    self.rejected_callback_parent()

  def set_data_hierarchy_types(self, data_hierarchy_types: dict[str, Any]) -> None:
    """
    Sets the data hierarchy types for the instance.

    This method updates the internal state of the instance by assigning the provided dictionary of data hierarchy types.
    It allows the instance to manage and utilize the specified types in its operations.

    Args:
        self: The instance of the class.
        data_hierarchy_types (dict[str, Any]): A dictionary containing data hierarchy types to be set.
    """
    self.data_hierarchy_types = data_hierarchy_types


if __name__ == '__main__':
  import sys

  app = QtWidgets.QApplication(sys.argv)
  ui = CreateTypeDialog(lambda: None, lambda: None)
  ui.show()
  sys.exit(app.exec())
