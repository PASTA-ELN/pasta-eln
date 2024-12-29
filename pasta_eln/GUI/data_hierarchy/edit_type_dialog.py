""" A dialog for editing an existing data type within the application. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: edit_type_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any, Callable

import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox

from pasta_eln.GUI.data_hierarchy.type_dialog import TypeDialog
from pasta_eln.GUI.data_hierarchy.utility_functions import generate_data_hierarchy_type, show_message


class EditTypeDialog(TypeDialog):
  """
  A dialog for editing an existing data type within the application.

  This class extends the TypeDialog to provide functionality for modifying existing data types.
  It initializes the dialog with specific UI elements and behavior tailored for editing, including disabling certain fields and setting tooltips.

  Args:
      accepted_callback (Callable[[], None]): A callback function to be executed when the action is accepted.
      rejected_callback (Callable[[], None]): A callback function to be executed when the action is rejected.

  Attributes:
      selected_data_hierarchy_type (dict[str, Any]): The currently selected data hierarchy type.
      selected_data_hierarchy_type_name (str): The name of the currently selected data hierarchy type.
  """

  def __init__(self,
               accepted_callback: Callable[[], None],
               rejected_callback: Callable[[], None]):
    """
    Initializes the dialog for editing an existing data type.

    This constructor sets up the dialog by initializing the parent class and configuring the user interface elements.
    It disables the type title field to prevent modifications and sets tooltips to guide the user on how to interact with the dialog.

    Args:
        self: The instance of the class.
        accepted_callback (Callable[[], None]): A callback function to be executed when the action is accepted.
        rejected_callback (Callable[[], None]): A callback function to be executed when the action is rejected.
    """
    super().__init__(accepted_callback, rejected_callback)
    self.selected_data_hierarchy_type: dict[str, Any] = {}
    self.selected_data_hierarchy_type_name: str = ''
    self.instance.setWindowTitle('Edit existing type')
    self.typeLineEdit.setDisabled(True)
    self.typeLineEdit.setToolTip('Changing type title disabled for edits!')
    self.typeDisplayedTitleLineEdit.setToolTip(self.typeDisplayedTitleLineEdit.toolTip().replace('Enter', 'Modify'))
    self.iriLineEdit.setToolTip(self.iriLineEdit.toolTip().replace('Enter', 'Modify'))
    self.shortcutLineEdit.setToolTip(self.shortcutLineEdit.toolTip().replace('Enter', 'Modify'))
    self.iconComboBox.currentIndexChanged[int].connect(self.set_icon)
    self.typeLineEdit.textChanged[str].connect(self.type_changed)

  def show(self) -> None:
    """
    Displays the dialog for editing the selected data type.

    This method initializes the dialog's user interface elements with the current values of the selected data hierarchy type.
    It sets the text fields and combo boxes to reflect the properties of the selected type, allowing the user to view and modify the data.
    """
    super().show()
    self.typeLineEdit.setText(self.selected_data_hierarchy_type_name)
    if not self.selected_data_hierarchy_type:
      self.logger.warning('Invalid data type: {%s}', self.selected_data_hierarchy_type)
      return
    self.iriLineEdit.setText(self.selected_data_hierarchy_type.get('IRI') or '')
    self.typeDisplayedTitleLineEdit.setText(self.selected_data_hierarchy_type.get('title') or '')
    self.shortcutLineEdit.setText(self.selected_data_hierarchy_type.get('shortcut') or '')
    icon = self.selected_data_hierarchy_type.get('icon') or ''
    self.iconFontCollectionComboBox.setCurrentText(icon.split('.')[0] if icon else '')
    self.iconComboBox.setCurrentText(self.selected_data_hierarchy_type.get('icon') or 'No value')

  def accepted_callback(self) -> None:
    """
    Handles the acceptance of updates to the selected data type.

    This method validates the type information and checks if the selected data hierarchy type exists.
    If the type information is valid and the type exists, it logs the update, generates the updated type,
    and closes the dialog. If the type does not exist, it displays a warning message to the user.
    """
    if not self.validate_type_info():
      return
    if not self.selected_data_hierarchy_type:
      show_message(
        f"Error update scenario: Type (datatype: {self.type_info.datatype} "
        f"displayed title: {self.type_info.title}) does not exists!!....",
        QMessageBox.Icon.Warning)
    else:
      self.logger.info('User updated the existing type: Datatype: {%s}, Displayed Title: {%s}',
                       self.type_info.datatype,
                       self.type_info.title)
      updated_type = generate_data_hierarchy_type(self.type_info)
      self.selected_data_hierarchy_type.update(updated_type)
      self.instance.close()
      self.accepted_callback_parent()

  def set_icon(self, new_index: int) -> None:
    """
    Sets the icon for the specified index in the icon combo box.

    This method updates the icon at the given index if the index is valid and the current icon name is not "No value".
    If the index is negative, it logs a warning and does not perform any updates.

    Args:
        self: The instance of the class.
        new_index (int): The index at which to set the icon.
    """
    if new_index < 0:
      self.logger.warning('Invalid index: {%s}', new_index)
      return
    new_icon_name = self.iconComboBox.currentText()
    if new_icon_name and new_icon_name != 'No value':
      self.iconComboBox.setItemIcon(new_index, qta.icon(new_icon_name))

  def type_changed(self, new_data_type: str) -> None:
    """
    Updates the state of the dialog based on the selected data type.

    This method disables or enables certain UI components depending on whether the provided data type is structural.
    If the data type is empty or None, it logs a warning and does not change the state of the components.

    Args:
        self: The instance of the class.
        new_data_type (str): The new data type selected by the user.
    """
    if not new_data_type:
      self.logger.warning('Invalid data type: {%s}', new_data_type)
      return
    disable_if_structural = new_data_type in {'x0', 'x1'}
    self.shortcutLineEdit.setDisabled(disable_if_structural)
    self.iconComboBox.setDisabled(disable_if_structural)
    self.iconFontCollectionComboBox.setDisabled(disable_if_structural)

  def set_selected_data_hierarchy_type(self, data_hierarchy_type: dict[str, Any]) -> None:
    """
    Updates the selected data hierarchy type for the instance.

    This method assigns the provided dictionary to the instance's selected data hierarchy type,
    allowing the instance to keep track of the currently selected type for further operations.

    Args:
        self: The instance of the class.
        data_hierarchy_type (dict[str, Any]): A dictionary representing the selected data hierarchy type.
    """
    self.selected_data_hierarchy_type = data_hierarchy_type

  def set_selected_data_hierarchy_type_name(self, datatype: str) -> None:
    """
    Sets the name of the selected data hierarchy type.

    This method updates the internal state of the instance by assigning the provided data type name
    to the selected data hierarchy type name attribute. It allows the instance to keep track of the
    currently selected type name for further operations.

    Args:
        self: The instance of the class.
        datatype (str): The name of the selected data hierarchy type.
    """
    self.selected_data_hierarchy_type_name = datatype


if __name__ == '__main__':
  import sys

  app = QtWidgets.QApplication(sys.argv)
  ui = EditTypeDialog(lambda: None, lambda: None)
  ui.show()
  sys.exit(app.exec())
