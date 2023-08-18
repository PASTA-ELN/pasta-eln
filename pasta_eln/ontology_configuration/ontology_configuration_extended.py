#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import sys
from typing import Union, Any

import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QLineEdit, QRadioButton

from pasta_eln.ontology_configuration.delete_column_delegate import DeleteColumnDelegate
from pasta_eln.ontology_configuration.ontology_configuration import Ui_OntologyConfigurationBaseForm
from pasta_eln.ontology_configuration.ontology_tableview_datamodel import OntologyTableViewModel
from pasta_eln.ontology_configuration.reorder_column_delegate import ReorderColumnDelegate
from pasta_eln.ontology_configuration.required_column_delegate import RequiredColumnDelegate


class OntologyConfigurationForm(Ui_OntologyConfigurationBaseForm):
  def __init__(self, logger, db_instance):
    """

    Args:
      db_instance: Couch DB Instance passed by the parent
    """
    self.data_model = OntologyTableViewModel()
    self.structures = None
    self.table_model = PySide6.QtGui.QStandardItemModel(6, 6)
    self.required_column_delegate = RequiredColumnDelegate()
    self.delete_column_delegate = DeleteColumnDelegate()
    self.delete_column_delegate.delete_clicked_signal.connect(self.data_model.delete_data)
    self.reorder_column_delegate = ReorderColumnDelegate()
    self.reorder_column_delegate.re_order_signal.connect(self.data_model.re_order_data)
    self.db = db_instance
    self.logger = logger

    print("")

  def structure_combo_box_changed(self, value):
    print("value: " + value)
    if value:
      self.data_model.update(self.structures.get(value).get('prop'))
      self.typeLabelLineEdit.setText(self.structures.get(value).get('label'))

  def setup_slots(self):
    self.loadOntologyPushButton.clicked.connect(self.load_ontology_data)
    self.typeComboBox.currentTextChanged.connect(self.structure_combo_box_changed)
    self.addPropsRowPushButton.clicked.connect(self.data_model.add_data_row)

  def load_ontology_data(self):
    """
      Load button click event handler
    # Args:

    Returns:

    """
    header = self.typePropsTableView.horizontalHeader()
    header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    ontology_data = self.db['-ontology-']
    self.structures = dict([(data, ontology_data[data])
                            for data in ontology_data
                            if type(ontology_data[data]) is dict])
    self.typeComboBox.clear()
    self.typeComboBox.addItems(self.structures.keys())
    self.typeComboBox.setCurrentIndex(0)
    self.typeComboBox.adjustSize()
    self.data_model.update(self.structures.get(self.typeComboBox.currentText()).get('prop'))
    self.typePropsTableView.setItemDelegateForColumn(4, self.required_column_delegate)
    self.typePropsTableView.setItemDelegateForColumn(6, self.delete_column_delegate)
    self.typePropsTableView.setItemDelegateForColumn(7, self.reorder_column_delegate)
    # self.typePropsTableView.setItemDelegate(self.delegate)
    self.typePropsTableView.setModel(self.data_model)
    # self.typePropsTableView.setModel(self.table_model)

    # for structure_key in structures:
    #   self.headerLabel.setText(str(ontology_data[structure_key]['label']))
    #   self.typePropsTableView.setModel(data_model)
    #   data_model.update(ontology_data)

    print("Clicked!!")


def get_db(db_name: str):
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
  base_form_widget = QtWidgets.QWidget()
  ontology_form: OntologyConfigurationForm = OntologyConfigurationForm(logger, db_instance)
  ontology_form.setupUi(base_form_widget)
  ontology_form.setup_slots()
  return application, base_form_widget, ontology_form


if __name__ == "__main__":
  db = get_db("research")
  app, base_form, ui_form = get_gui(None, db)
  base_form.show()
  sys.exit(app.exec())
