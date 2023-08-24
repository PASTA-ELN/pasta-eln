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

from pasta_eln.ontology_configuration import ontology_configuration_constants
from pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog_extended import CreateTypeDialog
from pasta_eln.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.ontology_configuration.exceptions.ontology_document_null_exception import OntologyDocumentNullException
from pasta_eln.ontology_configuration.ontology_attachments_tableview_data_model import OntologyAttachmentsTableViewModel
from pasta_eln.ontology_configuration.ontology_configuration import Ui_OntologyConfigurationBaseForm
from pasta_eln.ontology_configuration.ontology_props_tableview_data_model import OntologyPropsTableViewModel
from pasta_eln.ontology_configuration.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.ontology_configuration.required_column_delegate import RequiredColumnDelegate
from pasta_eln.ontology_configuration.utility_functions import adjust_ontology_data_to_v3, show_message, \
  get_next_possible_structural_level_label, get_db


class OntologyConfigurationForm(Ui_OntologyConfigurationBaseForm):
  def __init__(self,
               ontology_document: Document):
    """
    Constructs the ontology data editor

    Args:
      ontology_document (Document): Ontology data document from couch DB instance passed by the parent.

    Raises:
      OntologyDocumentNullException: Raised when passed in argument @ontology_document is null.
    """
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)

    self.ontology_types = None
    self.selected_type_properties = None

    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    ui = super()
    ui.setupUi(self.instance)

    # Gets the ontology data from db and adjust the data to the latest version
    if not ontology_document:
      raise OntologyDocumentNullException("Null document passed for ontology data", {})

    self.ontology_document: Document = ontology_document
    adjust_ontology_data_to_v3(self.ontology_document)

    # Instantiates property & attachment table models along with the column delegates
    self.props_table_data_model = OntologyPropsTableViewModel()
    self.attachments_table_data_model = OntologyAttachmentsTableViewModel()

    self.required_column_delegate_props_table = RequiredColumnDelegate()
    self.delete_column_delegate_props_table = DeleteColumnDelegate()
    self.reorder_column_delegate_props_table = ReorderColumnDelegate()
    self.delete_column_delegate_attach_table = DeleteColumnDelegate()
    self.reorder_column_delegate_attach_table = ReorderColumnDelegate()

    self.typePropsTableView.setItemDelegateForColumn(ontology_configuration_constants.PROPS_TABLE_REQUIRED_COLUMN_INDEX,
                                                     self.required_column_delegate_props_table)
    self.typePropsTableView.setItemDelegateForColumn(ontology_configuration_constants.PROPS_TABLE_DELETE_COLUMN_INDEX,
                                                     self.delete_column_delegate_props_table)
    self.typePropsTableView.setItemDelegateForColumn(ontology_configuration_constants.PROPS_TABLE_REORDER_COLUMN_INDEX,
                                                     self.reorder_column_delegate_props_table)
    self.typePropsTableView.setModel(self.props_table_data_model)

    self.typeAttachmentsTableView.setItemDelegateForColumn(
      ontology_configuration_constants.ATTACHMENT_TABLE_DELETE_COLUMN_INDEX,
      self.delete_column_delegate_attach_table)
    self.typeAttachmentsTableView.setItemDelegateForColumn(
      ontology_configuration_constants.ATTACHMENT_TABLE_REORDER_COLUMN_INDEX,
      self.reorder_column_delegate_attach_table)
    self.typeAttachmentsTableView.setModel(self.attachments_table_data_model)

    # Create the dialog for new type creation
    self.create_type_dialog = CreateTypeDialog(self.create_type_accepted_callback, self.create_type_rejected_callback)

    # Set up the slots for the UI items
    self.setup_slots()

  def type_combo_box_changed(self,
                             new_type_selected: Any) -> None:
    """
    Combobox value changed callback for the selected type
    Args:
      new_type_selected (Any): Newly set value for the combobox.

    Returns:
      None
    """
    self.logger.info(f"New type selected in UI: {new_type_selected}")
    self.addPropsCategoryLineEdit.clear()
    if new_type_selected and self.ontology_types:
      # Get the properties for the selected type and store the list in selected_type_properties
      self.selected_type_properties = self.ontology_types.get(new_type_selected).get('prop')

      # Type label is set in a line edit
      self.typeLabelLineEdit.setText(self.ontology_types.get(new_type_selected).get('label'))

      # Type link is set in a line edit
      self.typeLinkLineEdit.setText(self.ontology_types.get(new_type_selected).get('link'))

      # Gets the attachment data from selected type and set it in table view
      self.attachments_table_data_model.update(self.ontology_types.get(new_type_selected).get('attachments'))

      # Reset the props category combo-box
      self.propsCategoryComboBox.clear()
      self.propsCategoryComboBox.addItems(self.selected_type_properties.keys())
      self.propsCategoryComboBox.setCurrentIndex(0)

  def category_combo_box_changed(self,
                                 new_selected_prop_category: Any):
    """
    Combobox value changed callback for the selected type property categories
    Args:
      new_selected_prop_category (Any): Newly set value for the combobox.

    Returns:
      None
    """
    self.logger.info(f"New property category selected in UI: {new_selected_prop_category}")
    if new_selected_prop_category and self.selected_type_properties:
      # Update the property table as per the selected property category from combobox
      self.props_table_data_model.update(self.selected_type_properties.get(new_selected_prop_category))

  def add_new_prop_category(self):
    """
    Click event handler for adding new property category
    Returns:
      None
    """
    new_category = self.addPropsCategoryLineEdit.text()
    if not self.ontology_types:
      show_message("Load the ontology data first....")
      return
    if new_category:
      # Add the new category to the property list and refresh the category combo box
      self.logger.info(f"User added new category: {new_category}")
      self.selected_type_properties[new_category] = []
      self.propsCategoryComboBox.clear()
      self.propsCategoryComboBox.addItems(self.selected_type_properties.keys())
      self.propsCategoryComboBox.setCurrentIndex(len(self.selected_type_properties.keys()) - 1)
    else:
      show_message("Enter non-null/valid category name!!.....")

  def delete_selected_prop_category(self):
    """
    Click event handler for deleting the selected property category
    Returns:
      None
    """
    selected_category = self.propsCategoryComboBox.currentText()
    if selected_category and selected_category in self.selected_type_properties:
      self.logger.info(f"User deleted the selected category: {selected_category}")
      self.selected_type_properties.pop(selected_category)
      self.propsCategoryComboBox.clear()
      self.propsCategoryComboBox.addItems(self.selected_type_properties.keys())
      self.propsCategoryComboBox.setCurrentIndex(len(self.selected_type_properties.keys()) - 1)

  def update_structure_label(self,
                             modified_type_label: str):
    """
    Value changed callback for the type label line edit

    Args:
        modified_type_label (str): Modified ontology type label

    Returns:
        None
    """
    if modified_type_label:
      self.ontology_types.get(self.typeComboBox.currentText())["label"] = modified_type_label

  def update_type_link(self, modified_link: str):
    """
    Value changed callback for the link line edit

    Args:
        modified_link (str): Modified link to be set for the selected type

    Returns:
        None
    """
    if modified_link:
      self.ontology_types.get(self.typeComboBox.currentText())["link"] = modified_link

  def delete_selected_type(self):
    """
    Delete the selected type from the type selection combo-box and also from the loaded ontology_types

    Returns:
      None
    """
    selected_type = self.typeComboBox.currentText()
    if (selected_type and selected_type in self.ontology_types
        and selected_type in self.ontology_document):
      self.logger.info(f"User deleted the selected type: {selected_type}")
      self.ontology_types.pop(selected_type)
      self.ontology_document.pop(selected_type)
      self.typeComboBox.clear()
      self.typeComboBox.addItems(self.ontology_types.keys())
      self.typeComboBox.setCurrentIndex(0)

  def create_type_accepted_callback(self):
    """
    Callback for the OK button of CreateTypeDialog to create a new type in the ontology data set

    Returns:
      None
    """
    title = self.create_type_dialog.titleLineEdit.text()
    label = self.create_type_dialog.labelLineEdit.text()
    self.create_type_dialog.clear_ui()
    self.create_new_type(title, label)

  def create_type_rejected_callback(self):
    """
    Callback for the cancel button of CreateTypeDialog

    Returns:
        None
    """
    self.create_type_dialog.clear_ui()

  def show_create_type_dialog(self):
    """
    Opens a dialog which allows the user to enter the details to create a new type (structural or normal)
    Returns:
        None
    """
    if self.ontology_types:
      structural_title = get_next_possible_structural_level_label(self.ontology_types.keys())
      self.create_type_dialog.set_structural_level_title(structural_title)
      self.create_type_dialog.show()
    else:
      show_message("Load the ontology data first...")

  def setup_slots(self):
    """
    Set up the slots for the UI elements of Ontology editor
    Returns:
      None
    """
    self.logger.info(f"Setting up slots for the editor..")
    # Slots for the buttons
    self.loadOntologyPushButton.clicked.connect(self.load_ontology_data)
    self.addPropsRowPushButton.clicked.connect(self.props_table_data_model.add_data_row)
    self.addAttachmentPushButton.clicked.connect(self.attachments_table_data_model.add_data_row)
    self.saveOntologyPushButton.clicked.connect(self.save_ontology)
    self.addPropsCategoryPushButton.clicked.connect(self.add_new_prop_category)
    self.deletePropsCategoryPushButton.clicked.connect(self.delete_selected_prop_category)
    self.deleteTypePushButton.clicked.connect(self.delete_selected_type)
    self.addTypePushButton.clicked.connect(self.show_create_type_dialog)

    # Slots for the combo-boxes
    self.typeComboBox.currentTextChanged.connect(self.type_combo_box_changed)
    self.propsCategoryComboBox.currentTextChanged.connect(self.category_combo_box_changed)

    # Slots for line edits
    self.typeLabelLineEdit.textChanged[str].connect(self.update_structure_label)
    self.typeLinkLineEdit.textChanged[str].connect(self.update_type_link)

    # Slots for the delegates
    self.delete_column_delegate_props_table.delete_clicked_signal.connect(self.props_table_data_model.delete_data)
    self.reorder_column_delegate_props_table.re_order_signal.connect(self.props_table_data_model.re_order_data)

    self.delete_column_delegate_attach_table.delete_clicked_signal.connect(
      self.attachments_table_data_model.delete_data)
    self.reorder_column_delegate_attach_table.re_order_signal.connect(self.attachments_table_data_model.re_order_data)

  def load_ontology_data(self):
    """
    Load button click event handler which loads the data in the UI
    Returns:

    """
    self.logger.info("User loaded the ontology data in UI")
    # Load the ontology types from the db document
    self.ontology_types = dict([(data, self.ontology_document[data])
                                for data in self.ontology_document
                                if type(self.ontology_document[data]) is dict])

    # Set the types in the type selector combo-box
    self.typeComboBox.clear()
    self.typeComboBox.addItems(self.ontology_types.keys())
    self.typeComboBox.setCurrentIndex(0)

  def save_ontology(self):
    """
    Save the modified ontology document data in database
    """
    self.logger.info("User saved the ontology data document!!")
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
    if title in self.ontology_document:
      show_message(f"Type (title: {title} label: {label}) cannot be added since it exists in DB already....")
    else:
      self.logger.info(f"User created a new type and added "
                       f"it to the ontology document: Title: {title}, Label: {label}")
      empty_type = {
        "link": "",
        "label": label,
        "prop": {
          "default": []
        },
        "attachments": []
      }
      self.ontology_document[title] = empty_type
      self.ontology_types[title] = empty_type
      self.typeComboBox.clear()
      self.typeComboBox.addItems(self.ontology_types.keys())
      self.typeComboBox.setCurrentIndex(len(self.ontology_types) - 1)
      show_message(f"Type (title: {title} label: {label}) has been added....")


def get_gui(db_instance) -> tuple[QApplication | QApplication, QtWidgets.QDialog, OntologyConfigurationForm]:
  """
  Creates the editor UI and return it
  Args:


  Returns:

  """
  if not QApplication.instance():
    application = QApplication(sys.argv)
  else:
    application = QApplication.instance()
  ontology_form: OntologyConfigurationForm = OntologyConfigurationForm(db_instance['-ontology-'])

  return application, ontology_form.instance, ontology_form


if __name__ == "__main__":
  db = get_db("research", "admin", "SbFUXgmHaGpN", 'http://127.0.0.1:5984')
  app, ui_form_dialog, ui_form = get_gui(db)
  ui_form_dialog.show()
  sys.exit(app.exec())
