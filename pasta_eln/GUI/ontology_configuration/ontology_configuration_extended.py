""" OntologyConfigurationForm which is extended from the Ui_OntologyConfigurationBaseForm """
import copy
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
import sys
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication
from cloudant.document import Document

from .create_type_dialog_extended import CreateTypeDialog
from .ontology_attachments_tableview_data_model import OntologyAttachmentsTableViewModel
from .ontology_config_generic_exception import OntologyConfigGenericException
from .ontology_config_key_not_found_exception import \
  OntologyConfigKeyNotFoundException
from .ontology_configuration import Ui_OntologyConfigurationBaseForm
from .ontology_configuration_constants import PROPS_TABLE_DELETE_COLUMN_INDEX, PROPS_TABLE_REORDER_COLUMN_INDEX, \
  PROPS_TABLE_REQUIRED_COLUMN_INDEX, ATTACHMENT_TABLE_DELETE_COLUMN_INDEX, ATTACHMENT_TABLE_REORDER_COLUMN_INDEX
from .ontology_document_null_exception import OntologyDocumentNullException
from .ontology_props_tableview_data_model import OntologyPropsTableViewModel
from .delete_column_delegate import DeleteColumnDelegate
from .reorder_column_delegate import ReorderColumnDelegate
from .required_column_delegate import RequiredColumnDelegate
from .utility_functions import adjust_ontology_data_to_v3, show_message, \
  get_next_possible_structural_level_label, get_types_for_display, adapt_type, generate_empty_type, \
  generate_required_properties, check_ontology_types, get_missing_props_message


class OntologyConfigurationForm(Ui_OntologyConfigurationBaseForm):
  """ OntologyConfigurationForm class which is extended from the Ui_OntologyConfigurationBaseForm
  and contains the UI elements and related logic"""

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the OntologyConfigurationForm
    """
    return super(OntologyConfigurationForm, cls).__new__(cls)

  def __init__(self,
               ontology_document: Document) -> None:
    """
    Constructs the ontology data editor

    Args:
      ontology_document (Document): Ontology data document from couch DB instance passed by the parent.

    Raises:
      OntologyDocumentNullException: Raised when passed in argument @ontology_document is null.
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    self.ontology_loaded: bool = False
    self.ontology_types: Any = {}
    self.selected_type_properties: dict[str, list[dict[str, Any]]] | Any = {}

    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    super().setupUi(self.instance)

    # Gets the ontology data from db and adjust the data to the latest version
    if not ontology_document:
      raise OntologyDocumentNullException("Null document passed for ontology data", {})

    self.ontology_document: Document = ontology_document

    # Instantiates property & attachment table models along with the column delegates
    self.props_table_data_model = OntologyPropsTableViewModel()
    self.attachments_table_data_model = OntologyAttachmentsTableViewModel()

    self.required_column_delegate_props_table = RequiredColumnDelegate()
    self.delete_column_delegate_props_table = DeleteColumnDelegate()
    self.reorder_column_delegate_props_table = ReorderColumnDelegate()
    self.delete_column_delegate_attach_table = DeleteColumnDelegate()
    self.reorder_column_delegate_attach_table = ReorderColumnDelegate()

    self.typePropsTableView.setItemDelegateForColumn(PROPS_TABLE_REQUIRED_COLUMN_INDEX,
                                                     self.required_column_delegate_props_table)
    self.typePropsTableView.setItemDelegateForColumn(PROPS_TABLE_DELETE_COLUMN_INDEX,
                                                     self.delete_column_delegate_props_table)
    self.typePropsTableView.setItemDelegateForColumn(PROPS_TABLE_REORDER_COLUMN_INDEX,
                                                     self.reorder_column_delegate_props_table)
    self.typePropsTableView.setModel(self.props_table_data_model)

    for column_index, width in self.props_table_data_model.column_widths.items():
      self.typePropsTableView.setColumnWidth(column_index, width)

    self.typeAttachmentsTableView.setItemDelegateForColumn(
      ATTACHMENT_TABLE_DELETE_COLUMN_INDEX,
      self.delete_column_delegate_attach_table)
    self.typeAttachmentsTableView.setItemDelegateForColumn(
      ATTACHMENT_TABLE_REORDER_COLUMN_INDEX,
      self.reorder_column_delegate_attach_table)
    self.typeAttachmentsTableView.setModel(self.attachments_table_data_model)

    for column_index, width in self.attachments_table_data_model.column_widths.items():
      self.typeAttachmentsTableView.setColumnWidth(column_index, width)

    # Create the dialog for new type creation
    self.create_type_dialog = CreateTypeDialog(self.create_type_accepted_callback, self.create_type_rejected_callback)

    # Set up the slots for the UI items
    self.setup_slots()

    self.load_ontology_data()

  def type_combo_box_changed(self,
                             new_type_selected: Any) -> None:
    """
    Combobox value changed callback for the selected type
    Args:
      new_type_selected (Any): Newly set value for the combobox.

    Returns: Nothing

    Raises:
      OntologyConfigKeyNotFoundException: Raised when passed in argument @new_type_selected is not found in ontology_types

    """
    self.logger.info("New type selected in UI: {%s}", new_type_selected)
    self.clear_ui()
    new_type_selected = adapt_type(new_type_selected)
    if new_type_selected and self.ontology_types:
      if new_type_selected not in self.ontology_types:
        raise OntologyConfigKeyNotFoundException(f"Key {new_type_selected} "
                                                 f"not found in ontology_types", {})
      selected_type = self.ontology_types.get(new_type_selected)
      # Get the properties for the selected type and store the list in selected_type_properties
      self.selected_type_properties = selected_type.get('prop')

      # Type label is set in a line edit
      self.typeLabelLineEdit.setText(selected_type.get('label'))

      # Type IRI is set in a line edit
      self.typeIriLineEdit.setText(selected_type.get('IRI'))

      # Gets the attachment data from selected type and set it in table view
      self.attachments_table_data_model.update(selected_type.get('attachments'))

      # Reset the props category combo-box
      self.propsCategoryComboBox.addItems(list(self.selected_type_properties.keys())
                                          if self.selected_type_properties else [])
      self.propsCategoryComboBox.setCurrentIndex(0)

  def category_combo_box_changed(self,
                                 new_selected_prop_category: Any) -> None:
    """
    Combobox value changed callback for the selected type property categories
    Args:
      new_selected_prop_category (Any): Newly set value for the combobox.

    Returns: Nothing
    """
    self.logger.info("New property category selected in UI: {%s}", new_selected_prop_category)
    if new_selected_prop_category and self.selected_type_properties:
      # Update the property table as per the selected property category from combobox
      self.props_table_data_model.update(self.selected_type_properties.get(new_selected_prop_category))

  def add_new_prop_category(self) -> None:
    """
    Click event handler for adding new property category
    Returns: Nothing
    """
    new_category = self.addPropsCategoryLineEdit.text()
    if not new_category:
      show_message("Enter non-null/valid category name!!.....")
      return None
    if not self.ontology_loaded or self.ontology_types is None:
      show_message("Load the ontology data first....")
      return None
    if new_category in self.selected_type_properties.keys():
      show_message("Category already exists....")
      return None
    # Add the new category to the property list and refresh the category combo box
    self.logger.info("User added new category: {%s}", new_category)
    self.selected_type_properties[new_category] = generate_required_properties()
    self.propsCategoryComboBox.clear()
    self.propsCategoryComboBox.addItems(list(self.selected_type_properties.keys()))
    self.propsCategoryComboBox.setCurrentIndex(len(self.selected_type_properties.keys()) - 1)
    return None

  def delete_selected_prop_category(self) -> None:
    """
    Click event handler for deleting the selected property category
    Returns: Nothing
    """
    selected_category = self.propsCategoryComboBox.currentText()
    if self.selected_type_properties is None:
      show_message("Load the ontology data first....")
      return None
    if selected_category and selected_category in self.selected_type_properties.keys():
      self.logger.info("User deleted the selected category: {%s}", selected_category)
      self.selected_type_properties.pop(selected_category)
      self.propsCategoryComboBox.clear()
      self.typePropsTableView.model().update([])
      self.propsCategoryComboBox.addItems(list(self.selected_type_properties.keys()))
      self.propsCategoryComboBox.setCurrentIndex(len(self.selected_type_properties.keys()) - 1)
    return None

  def update_type_label(self,
                        modified_type_label: str) -> None:
    """
    Value changed callback for the type label line edit

    Args:
        modified_type_label (str): Modified ontology type label

    Returns: Nothing
    """
    current_type = self.typeComboBox.currentText()
    current_type = adapt_type(current_type)
    if modified_type_label is not None and current_type in self.ontology_types:
      self.ontology_types.get(current_type)["label"] = modified_type_label

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
    if modified_iri is not None and current_type in self.ontology_types:
      self.ontology_types.get(current_type)["IRI"] = modified_iri

  def delete_selected_type(self) -> None:
    """
    Delete the selected type from the type selection combo-box and also from the loaded ontology_types

    Returns: Nothing
    """
    selected_type = self.typeComboBox.currentText()
    selected_type = adapt_type(selected_type)
    if not self.ontology_loaded:
      show_message("Load the ontology data first....")
      return
    if self.ontology_types is None or self.ontology_document is None:
      show_message("Load the ontology data first....")
      return
    if (selected_type and selected_type in self.ontology_types
        and selected_type in self.ontology_document):
      self.logger.info("User deleted the selected type: {%s}", selected_type)
      self.ontology_types.pop(selected_type)
      self.typeComboBox.clear()
      self.typeComboBox.addItems(get_types_for_display(self.ontology_types.keys()))
      self.typeComboBox.setCurrentIndex(0)

  def clear_ui(self) -> None:
    """
    Clear the UI elements including the tables.
    Invoked when the type combobox selection changes
    Returns: None

    """
    # Disable the signals for the line edits before clearing in order to avoid clearing the respective
    # iri and labels for the selected type from ontology document
    self.typeLabelLineEdit.textChanged[str].disconnect()
    self.typeIriLineEdit.textChanged[str].disconnect()
    self.typeLabelLineEdit.clear()
    self.typeIriLineEdit.clear()
    self.typeLabelLineEdit.textChanged[str].connect(self.update_type_label)
    self.typeIriLineEdit.textChanged[str].connect(self.update_type_iri)

    self.propsCategoryComboBox.clear()
    self.addPropsCategoryLineEdit.clear()
    self.typePropsTableView.model().update([])
    self.typeAttachmentsTableView.model().update([])

  def create_type_accepted_callback(self) -> None:
    """
    Callback for the OK button of CreateTypeDialog to create a new type in the ontology data set

    Returns: Nothing
    """
    title = self.create_type_dialog.next_struct_level \
      if self.create_type_dialog.structuralLevelCheckBox.isChecked() \
      else self.create_type_dialog.titleLineEdit.text()
    label = self.create_type_dialog.labelLineEdit.text()
    self.create_type_dialog.clear_ui()
    self.create_new_type(title, label)

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
    if self.ontology_types is not None and self.ontology_loaded:
      structural_title = get_next_possible_structural_level_label(self.ontology_types.keys())
      self.create_type_dialog.set_structural_level_title(structural_title)
      self.create_type_dialog.show()
    else:
      show_message("Load the ontology data first...")

  def setup_slots(self) -> None:
    """
    Set up the slots for the UI elements of Ontology editor
    Returns: Nothing
    """
    self.logger.info("Setting up slots for the editor..")
    # Slots for the buttons
    self.addPropsRowPushButton.clicked.connect(self.props_table_data_model.add_data_row)
    self.addAttachmentPushButton.clicked.connect(self.attachments_table_data_model.add_data_row)
    self.saveOntologyPushButton.clicked.connect(self.save_ontology)
    self.addPropsCategoryPushButton.clicked.connect(self.add_new_prop_category)
    self.deletePropsCategoryPushButton.clicked.connect(self.delete_selected_prop_category)
    self.deleteTypePushButton.clicked.connect(self.delete_selected_type)
    self.addTypePushButton.clicked.connect(self.show_create_type_dialog)
    self.cancelPushButton.clicked.connect(self.instance.close)

    # Slots for the combo-boxes
    self.typeComboBox.currentTextChanged.connect(self.type_combo_box_changed)
    self.propsCategoryComboBox.currentTextChanged.connect(self.category_combo_box_changed)

    # Slots for line edits
    self.typeLabelLineEdit.textChanged[str].connect(self.update_type_label)
    self.typeIriLineEdit.textChanged[str].connect(self.update_type_iri)

    # Slots for the delegates
    self.delete_column_delegate_props_table.delete_clicked_signal.connect(self.props_table_data_model.delete_data)
    self.reorder_column_delegate_props_table.re_order_signal.connect(self.props_table_data_model.re_order_data)

    self.delete_column_delegate_attach_table.delete_clicked_signal.connect(
      self.attachments_table_data_model.delete_data)
    self.reorder_column_delegate_attach_table.re_order_signal.connect(self.attachments_table_data_model.re_order_data)

  def load_ontology_data(self) -> None:
    """
    Load button click event handler which loads the data in the UI
    Returns:

    """
    self.logger.info("User loaded the ontology data in UI")
    if self.ontology_document is None:
      raise OntologyConfigGenericException("Null ontology_document, erroneous app state", {})
    # Load the ontology types from the db document
    for data in self.ontology_document:
      if isinstance(self.ontology_document[data], dict):
        self.ontology_types[data] = copy.deepcopy(self.ontology_document[data])
    adjust_ontology_data_to_v3(self.ontology_types)
    self.ontology_loaded = True

    # Set the types in the type selector combo-box
    self.typeComboBox.clear()
    self.typeComboBox.addItems(get_types_for_display(self.ontology_types.keys()))
    self.typeComboBox.setCurrentIndex(0)

  def save_ontology(self) -> None:
    """
    Save the modified ontology document data in database
    """
    self.logger.info("User clicked the save button..")
    if missing_properties := check_ontology_types(self.ontology_types):
      message = get_missing_props_message(missing_properties)
      show_message(message)
      self.logger.warning(message)
      return
    # Clear all the data from the ontology_document
    for data in list(self.ontology_document.keys()):
      if isinstance(self.ontology_document[data], dict):
        del self.ontology_document[data]
    # Copy all the modifications
    for type_name, type_structure in self.ontology_types.items():
      self.ontology_document[type_name] = type_structure
    # Save the modified document
    self.ontology_document.save()
    show_message("Ontology data saved successfully..")

  def create_new_type(self,
                      title: str,
                      label: str) -> None:
    """
    Add a new type to the loaded ontology_data from the db
    Args:
      title (str): The new key entry used for the ontology_data
      label (str): The new label set for the new type entry in ontology_data

    Returns:

    """
    if self.ontology_document is None or self.ontology_types is None:
      self.logger.error("Null ontology_document/ontology_types, erroneous app state")
      raise OntologyConfigGenericException("Null ontology_document/ontology_types, erroneous app state", {})
    if title in self.ontology_document:
      show_message(f"Type (title: {title} label: {label}) cannot be added since it exists in DB already....")
    else:
      if title is None:
        self.logger.warning("Enter non-null/valid title!!.....")
        show_message("Enter non-null/valid title!!.....")
        return
      self.logger.info("User created a new type and added "
                       "to the ontology document: Title: {%s}, Label: {%s}", title, label)
      empty_type = generate_empty_type(label)
      self.ontology_types[title] = empty_type
      self.typeComboBox.clear()
      self.typeComboBox.addItems(get_types_for_display(self.ontology_types.keys()))
      self.typeComboBox.setCurrentIndex(len(self.ontology_types) - 1)
      show_message(f"Type (title: {title} label: {label}) has been added....")


def get_gui(ontology_document: Document) -> tuple[
  QApplication | QApplication, QtWidgets.QDialog, OntologyConfigurationForm]:
  """
  Creates the editor UI and return it
  Args:
    ontology_document (object): Ontology document from the couch DB.
  Returns:

  """
  instance = QApplication.instance()
  application = QApplication(sys.argv) if instance is None else instance
  ontology_form: OntologyConfigurationForm = OntologyConfigurationForm(ontology_document)

  return application, ontology_form.instance, ontology_form
