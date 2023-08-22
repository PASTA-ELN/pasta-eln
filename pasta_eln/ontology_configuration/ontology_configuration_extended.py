#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import sys

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QMessageBox
from cloudant.database import CouchDatabase
from cloudant.document import Document

from pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog_extended import CreateTypeDialog
from pasta_eln.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.ontology_configuration.ontology_configuration import Ui_OntologyConfigurationBaseForm
from pasta_eln.ontology_configuration.ontology_props_tableview_datamodel import OntologyTableViewModel
from pasta_eln.ontology_configuration.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.ontology_configuration.required_column_delegate import RequiredColumnDelegate
from pasta_eln.ontology_configuration.utility_functions import adjust_ontology_data_to_v3, show_message


class OntologyConfigurationForm(Ui_OntologyConfigurationBaseForm):
  def __init__(self, logger, db_instance: CouchDatabase):
    """

    Args:
      db_instance (CouchDatabase): Couch DB Instance passed by the parent
    """
    self.instance = QtWidgets.QDialog()
    ui = super()
    ui.setupUi(self.instance)
    self.selected_struct_properties = None
    self.data_model = OntologyTableViewModel()
    self.structures = None
    self.required_column_delegate = RequiredColumnDelegate()
    self.delete_column_delegate = DeleteColumnDelegate()
    self.reorder_column_delegate = ReorderColumnDelegate()
    self.db: CouchDatabase = db_instance
    self.ontology_data: Document = self.db['-ontology-']
    adjust_ontology_data_to_v3(self.ontology_data)
    self.logger = logger
    self.create_type_dialog = CreateTypeDialog(self.create_type_accepted_callback, self.create_type_rejected_callback)
    self.setup_slots()

  def structure_combo_box_changed(self, value):
    self.clear_inputs()
    if value and self.structures:
      self.selected_struct_properties = self.structures.get(value).get('prop')
      self.typeLabelLineEdit.setText(self.structures.get(value).get('label'))
      self.propsCategoryComboBox.clear()
      self.propsCategoryComboBox.addItems(self.selected_struct_properties.keys())
      self.propsCategoryComboBox.setCurrentIndex(0)

  def category_combo_box_changed(self, value):
    if value and self.selected_struct_properties:
      self.data_model.update(self.selected_struct_properties.get(value))

  def add_new_prop_category(self):
    """
    Click event handler for adding new property category
    Args: None


    Returns: None

    """
    new_category = self.addPropsCategoryLineEdit.text()
    if new_category is not None:
      self.selected_struct_properties[new_category] = []
      self.propsCategoryComboBox.clear()
      self.propsCategoryComboBox.addItems(self.selected_struct_properties.keys())
      self.propsCategoryComboBox.setCurrentIndex(len(self.selected_struct_properties.keys()) - 1)

  def delete_selected_prop_category(self):
    """Delete the selected property category

    Args: None


    Returns: None

    """
    selected_category = self.propsCategoryComboBox.currentText()
    if selected_category and selected_category in self.selected_struct_properties:
      self.selected_struct_properties.pop(selected_category)
      self.propsCategoryComboBox.clear()
      self.propsCategoryComboBox.addItems(self.selected_struct_properties.keys())
      self.propsCategoryComboBox.setCurrentIndex(len(self.selected_struct_properties.keys()) - 1)

  def update_structure_label(self, modified_type_label: str):
    """Value changed callback for the type label line edit

    Args:
        modified_type_label: str

    Returns:
        None
    """
    if modified_type_label:
      self.structures.get(self.typeComboBox.currentText())["label"] = modified_type_label

  def delete_selected_type(self):
    """Delete the selected structure type

    Args: None


    Returns: None

    """
    selected_type = self.typeComboBox.currentText()
    if (selected_type and selected_type in self.structures
        and selected_type in self.ontology_data):
      self.structures.pop(selected_type)
      self.ontology_data.pop(selected_type)
      self.typeComboBox.clear()
      self.typeComboBox.addItems(self.structures.keys())
      self.typeComboBox.setCurrentIndex(0)

  def create_type_accepted_callback(self):
    """Callback for the OK button of CreateTypeDialog

    Args:
        data

    Returns:

    """
    title = self.create_type_dialog.titleLineEdit.text()
    label = self.create_type_dialog.labelLineEdit.text()
    self.create_type_dialog.clear_ui()
    self.create_new_type(title, label)

  def create_type_rejected_callback(self):
    """Callback for the cancel button of CreateTypeDialog

    Args:
        data

    Returns:
        None
    """
    self.create_type_dialog.clear_ui()

  def show_create_type_dialog(self, next_structure_title: str):
    """Opens a dialog which allows the user to enter the details to create a new type

    Args:
        next_structure_title: str

    Returns:
        None
    """
    if self.structures:
      structural_title = self.get_next_possible_structural_level_label()
      self.create_type_dialog.set_structural_level_title(structural_title)
      self.create_type_dialog.show()
    else:
      show_message("Load the ontology data first...")

  def setup_slots(self):
    # Slots for the buttons
    self.loadOntologyPushButton.clicked.connect(self.load_ontology_data)
    self.typeComboBox.currentTextChanged.connect(self.structure_combo_box_changed)
    self.propsCategoryComboBox.currentTextChanged.connect(self.category_combo_box_changed)
    self.addPropsRowPushButton.clicked.connect(self.data_model.add_data_row)
    self.saveOntologyPushButton.clicked.connect(self.save_ontology)
    self.addPropsCategoryPushButton.clicked.connect(self.add_new_prop_category)
    self.deletePropsCategoryPushButton.clicked.connect(self.delete_selected_prop_category)
    self.typeLabelLineEdit.textChanged[str].connect(self.update_structure_label)
    self.typeDeletePushButton.clicked.connect(self.delete_selected_type)
    self.addTypePushButton.clicked.connect(self.show_create_type_dialog)

    # Slots for the delegates
    self.delete_column_delegate.delete_clicked_signal.connect(self.data_model.delete_data)
    self.reorder_column_delegate.re_order_signal.connect(self.data_model.re_order_data)

  def load_ontology_data(self):
    """
      Load button click event handler
    # Args:

    Returns:

    """
    header = self.typePropsTableView.horizontalHeader()
    header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    self.structures = dict([(data, self.ontology_data[data])
                            for data in self.ontology_data
                            if type(self.ontology_data[data]) is dict])

    self.typeComboBox.clear()
    self.typeComboBox.addItems(self.structures.keys())
    self.typeComboBox.setCurrentIndex(0)

    self.typePropsTableView.setItemDelegateForColumn(4, self.required_column_delegate)
    self.typePropsTableView.setItemDelegateForColumn(6, self.delete_column_delegate)
    self.typePropsTableView.setItemDelegateForColumn(7, self.reorder_column_delegate)
    self.typePropsTableView.setModel(self.data_model)

  def save_ontology(self):
    """
    Save the modified ontology data in database
    """
    self.ontology_data.save()

  def clear_inputs(self):
    self.addPropsCategoryLineEdit.clear()

  def get_next_possible_structural_level_label(self):
    if self.structures:
      from re import compile
      regexp = compile(r'^[Xx][0-9]+$')
      labels = [label for label in self.structures.keys() if regexp.match(label)]
      new_level = max([int(label
                           .replace('x', '')
                           .replace('X', '')) for label in labels])
      return f"x{new_level + 1}"
    return None

  def create_new_type(self, title: str, label: str):
    """
    Add a new type to the loaded list
    Args:
      title (str):
      label (str):

    Returns:

    """
    if title in self.ontology_data:
      show_message(f"Type (title: {title} label: {label}) cannot be added since it exists in DB already....")
    else:
      empty_type = {
        "link": "",
        "label": label,
        "prop": {
          "default": []
        },
        "attachments": []
      }
      self.ontology_data[title] = empty_type
      self.structures[title] = empty_type
      self.typeComboBox.clear()
      self.typeComboBox.addItems(self.structures.keys())
      self.typeComboBox.setCurrentIndex(len(self.structures) - 1)
      show_message(f"Type (title: {title} label: {label}) has been added....")


def get_db(db_name: str) -> CouchDatabase:
  """Gets the database instance

  Args:
      db_name:str

  Returns:
      Couch Database Instance
  """
  try:
    from cloudant import CouchDB
    client = CouchDB("admin", "SbFUXgmHaGpN", url='http://127.0.0.1:5984', connect=True)
  except Exception:
    print('**ERROR dit01: Could not connect with username+password to local server')
    return
  if db_name in client.all_dbs():
    db_instance = client[db_name]
  else:
    db_instance = client.create_database(db_name)  # tests and initial creation of example data set requires this
  return db_instance


def get_gui(logger, db_instance):
  """

  Args:


  Returns:

  """
  if not QApplication.instance():
    application = QApplication(sys.argv)
  else:
    application = QApplication.instance()
  ontology_form: OntologyConfigurationForm = OntologyConfigurationForm(logger, db_instance)
  return application, ontology_form.instance, ontology_form


if __name__ == "__main__":
  db = get_db("research")
  app, base_form, ui_form = get_gui(None, db)
  base_form.show()
  sys.exit(app.exec())
