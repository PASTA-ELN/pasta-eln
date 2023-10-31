""" DataHierarchyConfiguration which is extended from the Ui_DataHierarchyConfigurationBase """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: data_hierarchy_configuration.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import copy
import logging
import sys
import webbrowser
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QApplication, QLineEdit, QMessageBox
from cloudant.document import Document

from .create_type_dialog import CreateTypeDialog
from .attachments_tableview_data_model import AttachmentsTableViewModel
from .generic_exception import GenericException
from .key_not_found_exception import \
  KeyNotFoundException
from .data_hierarchy_configuration_base import Ui_DataHierarchyConfigurationBase
from .constants import ATTACHMENT_TABLE_DELETE_COLUMN_INDEX, \
  ATTACHMENT_TABLE_REORDER_COLUMN_INDEX, DATA_HIERARCHY_HELP_PAGE_URL, METADATA_TABLE_DELETE_COLUMN_INDEX, \
  METADATA_TABLE_IRI_COLUMN_INDEX, METADATA_TABLE_REORDER_COLUMN_INDEX, METADATA_TABLE_REQUIRED_COLUMN_INDEX
from .document_null_exception import DocumentNullException
from .metadata_tableview_data_model import MetadataTableViewModel
from .reorder_column_delegate import ReorderColumnDelegate
from .mandatory_column_delegate import MandatoryColumnDelegate
from .delete_column_delegate import DeleteColumnDelegate
from .iri_column_delegate import IriColumnDelegate
from .lookup_iri_action import LookupIriAction
from .utility_functions import adapt_type, adjust_data_hierarchy_data_to_v3, can_delete_type, check_data_hierarchy_types, \
  generate_empty_type, \
  generate_mandatory_metadata, get_missing_metadata_message, get_next_possible_structural_level_title, \
  get_types_for_display, show_message
from ...database import Database


class DataHierarchyConfiguration(Ui_DataHierarchyConfigurationBase, QObject):
  """ DataHierarchyConfiguration class which is extended from the Ui_DataHierarchyConfigurationBase
  and contains the UI elements and related logic"""
  type_changed_signal = Signal(str)

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the DataHierarchyConfiguration
    """
    return super(DataHierarchyConfiguration, cls).__new__(cls)

  def __init__(self, database: Database) -> None:
    """
    Constructs the data hierarchy data editor

    Args:
      database (Database): Pasta ELN database instance

    Raises:
      DocumentNullException: Raised when passed in argument database has null data_hierarchy_document.
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    self.data_hierarchy_loaded: bool = False
    self.data_hierarchy_types: Any = {}
    self.selected_type_metadata: dict[str, list[dict[str, Any]]] | Any = {}

    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    super().setupUi(self.instance)

    # Gets the data_hierarchy data from db and adjust the data to the latest version
    if database is None:
      raise GenericException("Null database instance passed to the initializer", {})

    self.database: Database = database
    self.data_hierarchy_document: Document = self.database.db['-ontology-']
    if not self.data_hierarchy_document:
      raise DocumentNullException("Null data_hierarchy document in db instance", {})

    # Instantiates metadata & attachment table models along with the column delegates
    self.metadata_table_data_model = MetadataTableViewModel()
    self.attachments_table_data_model = AttachmentsTableViewModel()

    self.required_column_delegate_metadata_table = MandatoryColumnDelegate()
    self.delete_column_delegate_metadata_table = DeleteColumnDelegate()
    self.reorder_column_delegate_metadata_table = ReorderColumnDelegate()
    self.iri_column_delegate_metadata_table = IriColumnDelegate()
    self.delete_column_delegate_attach_table = DeleteColumnDelegate()
    self.reorder_column_delegate_attach_table = ReorderColumnDelegate()

    self.typeMetadataTableView.setItemDelegateForColumn(METADATA_TABLE_REQUIRED_COLUMN_INDEX,
                                                        self.required_column_delegate_metadata_table)
    self.typeMetadataTableView.setItemDelegateForColumn(METADATA_TABLE_DELETE_COLUMN_INDEX,
                                                        self.delete_column_delegate_metadata_table)
    self.typeMetadataTableView.setItemDelegateForColumn(METADATA_TABLE_REORDER_COLUMN_INDEX,
                                                        self.reorder_column_delegate_metadata_table)
    self.typeMetadataTableView.setItemDelegateForColumn(METADATA_TABLE_IRI_COLUMN_INDEX,
                                                        self.iri_column_delegate_metadata_table)
    self.typeMetadataTableView.setModel(self.metadata_table_data_model)

    for column_index, width in self.metadata_table_data_model.column_widths.items():
      self.typeMetadataTableView.setColumnWidth(column_index, width)
    # When resized, only stretch the query column of typeMetadataTableView
    self.typeMetadataTableView.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    self.typeAttachmentsTableView.setItemDelegateForColumn(
      ATTACHMENT_TABLE_DELETE_COLUMN_INDEX,
      self.delete_column_delegate_attach_table)
    self.typeAttachmentsTableView.setItemDelegateForColumn(
      ATTACHMENT_TABLE_REORDER_COLUMN_INDEX,
      self.reorder_column_delegate_attach_table)
    self.typeAttachmentsTableView.setModel(self.attachments_table_data_model)

    for column_index, width in self.attachments_table_data_model.column_widths.items():
      self.typeAttachmentsTableView.setColumnWidth(column_index, width)
    # When resized, only stretch the type column of typeAttachmentsTableView
    self.typeAttachmentsTableView.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    # Create the dialog for new type creation
    self.create_type_dialog = CreateTypeDialog(self.create_type_accepted_callback, self.create_type_rejected_callback)

    # Set up the slots for the UI items
    self.setup_slots()

    # Hide the attachment table and the add attachment button initially
    self.addAttachmentPushButton.hide()
    self.typeAttachmentsTableView.hide()

    self.load_data_hierarchy_data()

  def type_combo_box_changed(self,
                             new_type_selected: Any) -> None:
    """
    Combobox value changed callback for the selected type
    Args:
      new_type_selected (Any): Newly set value for the combobox.

    Returns: Nothing

    Raises:
      KeyNotFoundException: Raised when passed in argument @new_type_selected is not found in data_hierarchy_types

    """
    self.logger.info("New type selected in UI: {%s}", new_type_selected)
    self.clear_ui()
    new_type_selected = adapt_type(new_type_selected)
    self.type_changed_signal.emit(new_type_selected)
    if new_type_selected and self.data_hierarchy_types:
      if new_type_selected not in self.data_hierarchy_types:
        raise KeyNotFoundException(f"Key {new_type_selected} "
                                                 f"not found in data_hierarchy_types", {})
      selected_type = self.data_hierarchy_types.get(new_type_selected)
      # Get the metadata for the selected type and store the list in selected_type_metadata
      self.selected_type_metadata = selected_type.get('metadata')

      # Type displayed_title is set in a line edit
      self.typeDisplayedTitleLineEdit.setText(selected_type.get('displayedTitle'))

      # Type IRI is set in a line edit
      self.typeIriLineEdit.setText(selected_type.get('IRI'))

      # Gets the attachment data from selected type and set it in table view
      self.attachments_table_data_model.update(selected_type.get('attachments'))

      # Reset the metadata group combo-box
      self.metadataGroupComboBox.addItems(list(self.selected_type_metadata.keys())
                                          if self.selected_type_metadata else [])
      self.metadataGroupComboBox.setCurrentIndex(0)

  def set_iri_lookup_action(self,
                            lookup_term: str) -> None:
    """
    Sets the IRI lookup action for the IRI line edit
    Args:
      lookup_term (str): Default lookup term to be used by the lookup service

    Returns: Nothing

    """
    for act in self.typeIriLineEdit.actions():
      if isinstance(act, LookupIriAction):
        act.deleteLater()
    self.typeIriLineEdit.addAction(
      LookupIriAction(parent_line_edit=self.typeIriLineEdit, lookup_term=lookup_term),
      QLineEdit.TrailingPosition)

  def metadata_group_combo_box_changed(self,
                                       new_selected_metadata_group: Any) -> None:
    """
    Combobox value changed callback for the selected type metadata groups
    Args:
      new_selected_metadata_group (Any): Newly set value for the combobox.

    Returns: Nothing
    """
    self.logger.info("New metadata group selected in UI: {%s}", new_selected_metadata_group)
    if new_selected_metadata_group and self.selected_type_metadata:
      # Update the metadata table as per the selected metadata group from combobox
      self.metadata_table_data_model.update(self.selected_type_metadata.get(new_selected_metadata_group))

  def add_new_metadata_group(self) -> None:
    """
    Click event handler for adding new metadata group
    Returns: Nothing
    """
    new_group = self.addMetadataGroupLineEdit.text()
    if not new_group:
      show_message("Enter non-null/valid metadata group name!!.....", QMessageBox.Warning)
      return None
    if not self.data_hierarchy_loaded or self.data_hierarchy_types is None:
      show_message("Load the data hierarchy data first....", QMessageBox.Warning)
      return None
    if new_group in self.selected_type_metadata.keys():
      show_message("Metadata group already exists....", QMessageBox.Warning)
      return None
    # Add the new group to the metadata list and refresh the group combo box
    self.logger.info("User added new metadata group: {%s}", new_group)
    self.selected_type_metadata[new_group] = generate_mandatory_metadata()
    self.metadataGroupComboBox.clear()
    self.metadataGroupComboBox.addItems(list(self.selected_type_metadata.keys()))
    self.metadataGroupComboBox.setCurrentIndex(len(self.selected_type_metadata.keys()) - 1)
    return None

  def delete_selected_metadata_group(self) -> None:
    """
    Click event handler for deleting the selected metadata group
    Returns: Nothing
    """
    selected_group = self.metadataGroupComboBox.currentText()
    if self.selected_type_metadata is None:
      show_message("Load the data hierarchy data first....", QMessageBox.Warning)
      return None
    if selected_group and selected_group in self.selected_type_metadata.keys():
      self.logger.info("User deleted the selected metadata group: {%s}", selected_group)
      self.selected_type_metadata.pop(selected_group)
      self.metadataGroupComboBox.clear()
      self.typeMetadataTableView.model().update([])
      self.metadataGroupComboBox.addItems(list(self.selected_type_metadata.keys()))
      self.metadataGroupComboBox.setCurrentIndex(len(self.selected_type_metadata.keys()) - 1)
    return None

  def update_type_displayed_title(self,
                        modified_type_displayed_title: str) -> None:
    """
    Value changed callback for the type displayed title line edit

    Args:
        modified_type_displayed_title (str): Modified data_hierarchy type displayed title

    Returns: Nothing
    """
    current_type = self.typeComboBox.currentText()
    current_type = adapt_type(current_type)
    if modified_type_displayed_title is not None and current_type in self.data_hierarchy_types:
      self.data_hierarchy_types.get(current_type)["displayedTitle"] = modified_type_displayed_title
      self.set_iri_lookup_action(modified_type_displayed_title)

  def update_type_iri(self,
                      modified_iri: str) -> None:
    """
    Value changed callback for the IRI line edit

    Args:
        modified_iri (str): Modified IRI to be set for the selected type

    Returns: Nothing
    """
    current_type = self.typeComboBox.currentText()
    current_type = adapt_type(current_type)
    if modified_iri is not None and current_type in self.data_hierarchy_types:
      self.data_hierarchy_types.get(current_type)["IRI"] = modified_iri

  def delete_selected_type(self) -> None:
    """
    Delete the selected type from the type selection combo-box and also from the loaded data_hierarchy_types

    Returns: Nothing
    """
    selected_type = self.typeComboBox.currentText()
    selected_type = adapt_type(selected_type)
    if not self.data_hierarchy_loaded:
      show_message("Load the data hierarchy data first....", QMessageBox.Warning)
      return
    if self.data_hierarchy_types is None or self.data_hierarchy_document is None:
      show_message("Load the data hierarchy data first....", QMessageBox.Warning)
      return
    if selected_type and selected_type in self.data_hierarchy_types:
      self.logger.info("User deleted the selected type: {%s}", selected_type)
      self.data_hierarchy_types.pop(selected_type)
      self.typeComboBox.clear()
      self.typeComboBox.addItems(get_types_for_display(self.data_hierarchy_types.keys()))
      self.typeComboBox.setCurrentIndex(0)

  def clear_ui(self) -> None:
    """
    Clear the UI elements including the tables.
    Invoked when the type combobox selection changes
    Returns: None

    """
    # Disable the signals for the line edits before clearing in order to avoid clearing the respective
    # iri and displayed_titles for the selected type from data_hierarchy document
    self.typeDisplayedTitleLineEdit.textChanged[str].disconnect()
    self.typeIriLineEdit.textChanged[str].disconnect()
    self.typeDisplayedTitleLineEdit.clear()
    self.typeIriLineEdit.clear()
    self.typeDisplayedTitleLineEdit.textChanged[str].connect(self.update_type_displayed_title)
    self.typeIriLineEdit.textChanged[str].connect(self.update_type_iri)

    self.metadataGroupComboBox.clear()
    self.addMetadataGroupLineEdit.clear()
    self.typeMetadataTableView.model().update([])
    self.typeAttachmentsTableView.model().update([])

  def create_type_accepted_callback(self) -> None:
    """
    Callback for the OK button of CreateTypeDialog to create a new type in the data_hierarchy data set

    Returns: Nothing
    """
    title = self.create_type_dialog.next_struct_level \
      if self.create_type_dialog.structuralLevelCheckBox.isChecked() \
      else self.create_type_dialog.titleLineEdit.text()
    displayed_title = self.create_type_dialog.displayedTitleLineEdit.text()
    self.create_type_dialog.clear_ui()
    self.create_new_type(title, displayed_title)

  def create_type_rejected_callback(self) -> None:
    """
    Callback for the cancel button of CreateTypeDialog

    Returns: Nothing
    """
    self.create_type_dialog.clear_ui()

  def show_create_type_dialog(self) -> None:
    """
    Opens a dialog which allows the user to enter the details to create a new type (structural or normal)
    Returns: Nothing
    """
    if self.data_hierarchy_types is not None and self.data_hierarchy_loaded:
      structural_title = get_next_possible_structural_level_title(self.data_hierarchy_types.keys())
      self.create_type_dialog.set_structural_level_title(structural_title)
      self.create_type_dialog.show()
    else:
      show_message("Load the data hierarchy data first...", QMessageBox.Warning)

  def setup_slots(self) -> None:
    """
    Set up the slots for the UI elements of data hierarchy editor
    Returns: Nothing
    """
    self.logger.info("Setting up slots for the editor..")
    # Slots for the buttons
    self.addMetadataRowPushButton.clicked.connect(self.metadata_table_data_model.add_data_row)
    self.addAttachmentPushButton.clicked.connect(self.attachments_table_data_model.add_data_row)
    self.saveDataHierarchyPushButton.clicked.connect(self.save_data_hierarchy)
    self.addMetadataGroupPushButton.clicked.connect(self.add_new_metadata_group)
    self.deleteMetadataGroupPushButton.clicked.connect(self.delete_selected_metadata_group)
    self.deleteTypePushButton.clicked.connect(self.delete_selected_type)
    self.addTypePushButton.clicked.connect(self.show_create_type_dialog)
    self.cancelPushButton.clicked.connect(self.instance.close)
    self.helpPushButton.clicked.connect(lambda: webbrowser.open(DATA_HIERARCHY_HELP_PAGE_URL))
    self.attachmentsShowHidePushButton.clicked.connect(self.show_hide_attachments_table)

    # Slots for the combo-boxes
    self.typeComboBox.currentTextChanged.connect(self.type_combo_box_changed)
    self.metadataGroupComboBox.currentTextChanged.connect(self.metadata_group_combo_box_changed)

    # Slots for line edits
    self.typeDisplayedTitleLineEdit.textChanged[str].connect(self.update_type_displayed_title)
    self.typeIriLineEdit.textChanged[str].connect(self.update_type_iri)

    # Slots for the delegates
    self.delete_column_delegate_metadata_table.delete_clicked_signal.connect(self.metadata_table_data_model.delete_data)
    self.reorder_column_delegate_metadata_table.re_order_signal.connect(self.metadata_table_data_model.re_order_data)

    self.delete_column_delegate_attach_table.delete_clicked_signal.connect(
      self.attachments_table_data_model.delete_data)
    self.reorder_column_delegate_attach_table.re_order_signal.connect(self.attachments_table_data_model.re_order_data)

    self.type_changed_signal.connect(self.check_and_disable_delete_button)

  def load_data_hierarchy_data(self) -> None:
    """
    Load button click event handler which loads the data in the UI
    Returns:

    """
    self.logger.info("User loaded the data hierarchy data in UI")
    if self.data_hierarchy_document is None:
      raise GenericException("Null data_hierarchy_document, erroneous app state", {})
    # Load the data_hierarchy types from the db document
    for data in self.data_hierarchy_document:
      if isinstance(self.data_hierarchy_document[data], dict):
        self.data_hierarchy_types[data] = copy.deepcopy(self.data_hierarchy_document[data])
    adjust_data_hierarchy_data_to_v3(self.data_hierarchy_types)
    self.data_hierarchy_loaded = True

    # Set the types in the type selector combo-box
    self.typeComboBox.clear()
    self.typeComboBox.addItems(get_types_for_display(self.data_hierarchy_types.keys()))
    self.typeComboBox.setCurrentIndex(0)

  def save_data_hierarchy(self) -> None:
    """
    Save the modified data hierarchy document data in database
    """
    self.logger.info("User clicked the save button..")
    types_with_missing_metadata, types_with_null_name_metadata = check_data_hierarchy_types(self.data_hierarchy_types)
    if types_with_missing_metadata or types_with_null_name_metadata:
      message = get_missing_metadata_message(types_with_missing_metadata, types_with_null_name_metadata)
      show_message(message, QMessageBox.Warning)
      self.logger.warning(message)
      return

    result = show_message("Save will close the tool and restart the Pasta Application (Yes/No?)",
                          QMessageBox.Question,
                          QMessageBox.No | QMessageBox.Yes,
                          QMessageBox.Yes)

    if result == QMessageBox.Yes:
      # Clear all the data from the data_hierarchy_document
      for data in list(self.data_hierarchy_document.keys()):
        if isinstance(self.data_hierarchy_document[data], dict):
          del self.data_hierarchy_document[data]
      # Copy all the modifications
      for type_name, type_structure in self.data_hierarchy_types.items():
        self.data_hierarchy_document[type_name] = type_structure
      # Save the modified document
      self.data_hierarchy_document.save()
      self.database.ontology = dict(self.data_hierarchy_document)
      self.database.initDocTypeViews(16)
      self.instance.close()

  def create_new_type(self,
                      title: str,
                      displayed_title: str) -> None:
    """
    Add a new type to the loaded data_hierarchy_data from the db
    Args:
      title (str): The new key entry used for the data_hierarchy_data
      displayed_title (str): The new displayed_title set for the new type entry in data_hierarchy_data

    Returns:

    """
    if self.data_hierarchy_document is None or self.data_hierarchy_types is None:
      self.logger.error("Null data_hierarchy_document/data_hierarchy_types, erroneous app state")
      raise GenericException("Null data_hierarchy_document/data_hierarchy_types, erroneous app state", {})
    if title in self.data_hierarchy_types:
      show_message(f"Type (title: {title} displayed title: {displayed_title}) cannot be added since it exists in DB already....",
                   QMessageBox.Warning)
    else:
      if not title:
        self.logger.warning("Enter non-null/valid title!!.....")
        show_message("Enter non-null/valid title!!.....", QMessageBox.Warning)
        return
      self.logger.info("User created a new type and added "
                       "to the data_hierarchy document: Title: {%s}, Displayed Title: {%s}", title, displayed_title)
      empty_type = generate_empty_type(displayed_title)
      self.data_hierarchy_types[title] = empty_type
      self.typeComboBox.clear()
      self.typeComboBox.addItems(get_types_for_display(self.data_hierarchy_types.keys()))
      self.typeComboBox.setCurrentIndex(len(self.data_hierarchy_types) - 1)

  def show_hide_attachments_table(self) -> None:
    """
    Show/hide the attachment table and the add attachment button
    Returns: Nothing
    """
    self.typeAttachmentsTableView.setVisible(not self.typeAttachmentsTableView.isVisible())
    self.addAttachmentPushButton.setVisible(not self.addAttachmentPushButton.isVisible())

  @Slot(str)
  def check_and_disable_delete_button(self,
                                      selected_type: str) -> None:
    """
    Slot to check and disable the "delete" button for the selected type
    Args:
      selected_type (str): Selected type: typesComboBox

    Returns: Nothing

    """
    (self.deleteTypePushButton
     .setEnabled(can_delete_type(self.data_hierarchy_types.keys(),
                                 selected_type)))


def get_gui(database: Database) -> tuple[
  QApplication | QApplication, QtWidgets.QDialog, DataHierarchyConfiguration]:
  """
  Creates the editor UI and return it
  Args:
    database (Database): PASTA ELN Database instance.
  Returns:

  """
  instance = QApplication.instance()
  application = QApplication(sys.argv) if instance is None else instance
  data_hierarchy_form: DataHierarchyConfiguration = DataHierarchyConfiguration(database)

  return application, data_hierarchy_form.instance, data_hierarchy_form
