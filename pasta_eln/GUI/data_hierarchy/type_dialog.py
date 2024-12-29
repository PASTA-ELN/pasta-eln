""" Type dialog for the data hierarchy. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: create_type_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Any, Callable

import qtawesome as qta
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QLineEdit, QMessageBox

from pasta_eln.GUI.data_hierarchy.data_type_info import DataTypeInfo
from pasta_eln.GUI.data_hierarchy.data_type_info_validator import DataTypeInfoValidator
from pasta_eln.GUI.data_hierarchy.lookup_iri_action import LookupIriAction
from pasta_eln.GUI.data_hierarchy.qtaicons_factory import QTAIconsFactory
from pasta_eln.GUI.data_hierarchy.type_dialog_base import Ui_TypeDialogBase
from pasta_eln.GUI.data_hierarchy.utility_functions import show_message


class TypeDialog(Ui_TypeDialogBase):
  """
  Represents a dialog for creating or modifying a data type.

  Explanation:
      This class initializes a dialog that allows users to input and modify various attributes of a data type,
      including its title, IRI, shortcut, and icon. It connects UI elements to their respective callback functions
      and manages the interaction between the user and the underlying data model.

  Args:
      accepted_callback (Callable[[], None]): Callback function to be called when the dialog is accepted.
      rejected_callback (Callable[[], None]): Callback function to be called when the dialog is rejected.

  Attributes:
      logger (logging.Logger): Logger for the class.
      accepted_callback_parent (Callable[[], None]): Parent callback for accepted action.
      rejected_callback_parent (Callable[[], None]): Parent callback for rejected action.
      type_info (DataTypeInfo): DataTypeInfo instance to hold the data type information.
      instance (QDialog): The dialog instance.
      qta_icons (QTAIconsFactory): Singleton instance for managing icons.

  Methods:
      setup_slots(): Connects UI elements to their respective callback functions.
      set_data_type(datatype: str): Sets the data type in the type_info.
      set_type_title(title: str): Sets the title in the type_info.
      set_type_iri(iri: str): Sets the IRI in the type_info.
      set_type_shortcut(shortcut: str): Sets the shortcut in the type_info.
      set_type_icon(icon: str): Sets the icon in the type_info.
      set_iri_lookup_action(lookup_term: str): Sets the IRI lookup action for the IRI line edit.
      icon_font_collection_changed(font_collection: str): Updates the icon combo box based on the selected font collection.
      populate_icons(font_collection: str): Populates the icon combo box with icons from the specified font collection.
      show(): Displays the dialog.
      clear_ui(): Clears the dialog UI.
      validate_type_info(): Validates the data type information.
      title_modified(new_title: str): Updates the IRI lookup action based on the modified title.
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Create a new instance of the TypeDialog class.
    """
    return super(TypeDialog, cls).__new__(cls)

  def __init__(self,
               accepted_callback: Callable[[], None],
               rejected_callback: Callable[[], None]) -> None:
    """
    Initializes the create type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.accepted_callback_parent = accepted_callback
    self.rejected_callback_parent = rejected_callback
    self.type_info: DataTypeInfo = DataTypeInfo()
    self.instance = QDialog()
    super().setupUi(self.instance)

    self.qta_icons = QTAIconsFactory.get_instance()
    self.iconFontCollectionComboBox.addItems(self.qta_icons.font_collections)
    self.populate_icons(self.qta_icons.font_collections[0])

    self.setup_slots()

    # Restricts the title input to allow anything except x or space
    # as the first character which is reserved for structural level
    self.typeLineEdit.setValidator(QRegularExpressionValidator(QRegularExpression('(?=^[^Ax])(?=[^ ]*)')))
    self.iconComboBox.completer().setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
    self.set_iri_lookup_action('')

  def accepted_callback(self) -> None:
    """
    Callback function to be executed when the dialog is accepted.

    Explanation:
        This method serves as a placeholder for actions that should be taken when the user confirms their input
        in the dialog. Currently, it does not perform any operations but can be extended in the future.
    """
    return

  def rejected_callback(self) -> None:
    """
    Callback function to be executed when the dialog is rejected.

    Explanation:
        This method serves as a placeholder for actions that should be taken when the user cancels their input
        in the dialog. Currently, it does not perform any operations but can be extended in the future.
    """
    return

  def setup_slots(self) -> None:
    """
    Connects UI elements to their respective callback functions.

    Explanation:
        This method sets up the signal-slot connections for various UI components in the dialog.
        It ensures that changes in the UI elements trigger the appropriate methods to handle those changes.
    """
    self.iconFontCollectionComboBox.currentTextChanged[str].connect(self.icon_font_collection_changed)
    self.typeDisplayedTitleLineEdit.textChanged[str].connect(self.title_modified)
    self.typeDisplayedTitleLineEdit.textChanged[str].connect(self.set_type_title)
    self.typeLineEdit.textChanged[str].connect(self.set_data_type)
    self.iriLineEdit.textChanged[str].connect(self.set_type_iri)
    self.shortcutLineEdit.textChanged[str].connect(self.set_type_shortcut)
    self.iconComboBox.currentTextChanged[str].connect(self.set_type_icon)
    self.buttonBox.rejected.connect(self.rejected_callback)
    self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accepted_callback)
    self.buttonBox.accepted.disconnect()

  def set_data_type(self, datatype: str) -> None:
    """
    Sets the data type for the type information.

    Explanation:
        This method updates the internal data type attribute of the type_info object.
        It allows the user to specify the data type associated with the current context.

    Args:
        datatype (str): The new data type to set.
    """
    self.type_info.datatype = datatype

  def set_type_title(self, title: str) -> None:
    """
    Sets the title for the type information.

    Explanation:
        This method updates the internal title attribute of the type_info object.
        It allows the user to specify the title associated with the current data type context.

    Args:
        title (str): The new title to set.
    """
    self.type_info.title = title

  def set_type_iri(self, iri: str) -> None:
    """
    Sets the IRI (Internationalized Resource Identifier) for the type information.

    Explanation:
        This method updates the internal IRI attribute of the type_info object.
        It allows the user to specify the IRI associated with the current data type context.

    Args:
        iri (str): The new IRI to set.
    """
    self.type_info.iri = iri

  def set_type_shortcut(self, shortcut: str) -> None:
    """
    Sets the shortcut for the type information.

    Explanation:
        This method updates the internal shortcut attribute of the type_info object.
        It allows the user to specify the shortcut associated with the current data type context.

    Args:
        shortcut (str): The new shortcut to set.
    """
    self.type_info.shortcut = shortcut

  def set_type_icon(self, icon: str) -> None:
    """
    Sets the icon for the type information.

    Explanation:
        This method updates the internal icon attribute of the type_info object.
        It allows the user to specify the icon associated with the current data type context.

    Args:
        icon (str): The new icon to set.
    """
    self.type_info.icon = icon

  def set_iri_lookup_action(self,
                            lookup_term: str) -> None:
    """
    Sets the IRI lookup action for the IRI line edit
    Args:
      lookup_term (str): Default lookup term to be used by the lookup service

    Returns: Nothing

    """
    for act in self.iriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        act.deleteLater()
    self.iriLineEdit.addAction(
      LookupIriAction(parent_line_edit=self.iriLineEdit, lookup_term=lookup_term),
      QLineEdit.ActionPosition.TrailingPosition)

  def icon_font_collection_changed(self, font_collection: str) -> None:
    """
    Updates the icon combo box based on the selected font collection.

    Explanation:
        This method is triggered when the font collection changes.
        It clears the current items in the icon combo box and populates it with icons from the newly selected font collection.

    Args:
        font_collection (str): The name of the font collection that has been selected.
    """
    self.iconComboBox.clear()
    self.populate_icons(font_collection)

  def populate_icons(self, font_collection: str) -> None:
    """
    Populates the icon combo box with icons from the specified font collection.

    Explanation:
        This method checks if the provided font collection is valid.
        If valid, it adds the icons associated with that collection to the icon combo box; otherwise, it logs a warning.

    Args:
        font_collection (str): The name of the font collection from which to populate icons.
    """
    if not font_collection or font_collection not in self.qta_icons.icon_names:
      self.logger.warning('Invalid font collection!')
      return
    self.iconComboBox.addItem(self.qta_icons.icon_names[font_collection][0])
    for item in self.qta_icons.icon_names[font_collection][1:]:
      self.iconComboBox.addItem(qta.icon(item), item)

  def show(self) -> None:
    """
    Displays the dialog

    Returns: None

    """
    self.instance.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    self.instance.show()

  def clear_ui(self) -> None:
    """
    Clear the Dialog UI

    Returns: Nothing

    """
    self.typeLineEdit.clear()
    self.typeDisplayedTitleLineEdit.clear()
    self.iriLineEdit.clear()
    self.shortcutLineEdit.clear()
    self.iconFontCollectionComboBox.setCurrentIndex(0)
    self.iconComboBox.setCurrentIndex(0)

  def validate_type_info(self) -> bool:
    """
    Validates the type information stored in the type_info attribute.

    Explanation:
        This method checks the validity of the data type information using the DataTypeInfoValidator.
        If the validation fails, it displays an error message and logs the error, returning False; otherwise, it returns True.

    Returns:
        bool: True if the type information is valid, False otherwise.
    """
    valid_type = True
    try:
      DataTypeInfoValidator.validate(self.type_info)
    except (TypeError, ValueError) as e:
      show_message(str(e), QMessageBox.Icon.Warning)
      valid_type = False
      self.logger.error(str(e))
    return valid_type

  def title_modified(self, new_title: str) -> None:
    """
    Updates the IRI lookup action based on the modified title.

    Explanation:
        This method is called when the title is modified.
        If the new title is not empty, it sets the IRI lookup action using the new title.

    Args:
        new_title (str): The new title that has been set.
    """
    if new_title:
      self.set_iri_lookup_action(new_title)

  def set_selected_data_hierarchy_type(self, data_hierarchy_type: dict[str, Any]) -> None:
    """
    Sets the selected data hierarchy type for the instance.

    This method is intended to update the internal state of the instance by assigning the provided
    dictionary representing the selected data hierarchy type. It allows the instance to manage and
    utilize the specified type in its operations.

    Args:
        self: The instance of the class.
        data_hierarchy_type (dict[str, Any]): A dictionary representing the selected data hierarchy type.
    """
    return

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
    return

  def set_data_hierarchy_types(self, data_hierarchy_types: dict[str, Any]) -> None:
    """
    Sets the data hierarchy types for the instance.

    This method updates the internal state of the instance by assigning the provided dictionary
    of data hierarchy types. It allows the instance to manage and utilize the specified types
    in its operations.

    Args:
        self: The instance of the class.
        data_hierarchy_types (dict[str, Any]): A dictionary containing data hierarchy types to be set.
    """
    return
