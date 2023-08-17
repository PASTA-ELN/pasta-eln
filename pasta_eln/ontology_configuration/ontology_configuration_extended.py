#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import sys
from typing import Union

import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets

from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QLineEdit

from pasta_eln.ontology_configuration.ontology_configuration import Ui_OntologyConfigurationBaseForm
from pasta_eln.ontology_configuration.ontology_tableview_datamodel import OntologyTableViewModel


class ExampleDelegate(QStyledItemDelegate):

  def paint(self, painter: PySide6.QtGui.QPainter, option: PySide6.QtWidgets.QStyleOptionViewItem,
            index: Union[PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex]) -> None:
    super().paint(painter, option, index)

  def createEditor(self, parent: PySide6.QtWidgets.QWidget, option: PySide6.QtWidgets.QStyleOptionViewItem,
                   index: Union[
                     PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex]) -> PySide6.QtWidgets.QWidget:
    return super().createEditor(parent, option, index)

  # def createEditor(self, parent, option, index):
  #   line_edit = QLineEdit(parent)
  #   line_edit.setMaxLength(3)
  #   return line_edit


class OntologyConfigurationForm(Ui_OntologyConfigurationBaseForm):
  def __init__(self, logger, db_instance):
    """

    Args:
      db_instance: Couch DB Instance passed by the parent
    """
    self.data_model = OntologyTableViewModel()
    self.structures = None
    self.table_model = PySide6.QtGui.QStandardItemModel(6, 6)
    self.delegate = ExampleDelegate()
    self.db = db_instance
    self.logger = logger

    print("")

  def structure_combo_box_changed(self, value):
    print("value: " + value)
    self.data_model.update(self.structures.get(value).get('prop'))

  def setup_slots(self):
    self.loadPushButton.clicked.connect(self.load_ontology_data)
    self.typeComboBox.currentTextChanged.connect(self.structure_combo_box_changed)

  def load_ontology_data(self):
    """
      Load button click event handler
    # Args:

    Returns:

    """
    header = self.structuralPropsTableView.horizontalHeader()
    header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    ontology_data = self.db['-ontology-']
    self.structures = dict([(data, ontology_data[data])
                            for data in ontology_data
                            if type(ontology_data[data]) is dict])
    self.typeComboBox.clear()
    self.typeComboBox.addItems(self.structures.keys())
    self.typeComboBox.setCurrentIndex(0)
    self.data_model.update(self.structures.get(self.typeComboBox.currentText()).get('prop'))
    # self.structuralPropsTableView.setItemDelegateForColumn(0, self.delegate)
    # self.structuralPropsTableView.setItemDelegate(self.delegate)
    self.structuralPropsTableView.setModel(self.data_model)
    # self.structuralPropsTableView.setModel(self.table_model)

    # for structure_key in structures:
    #   self.headerLabel.setText(str(ontology_data[structure_key]['label']))
    #   self.structuralPropsTableView.setModel(data_model)
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
