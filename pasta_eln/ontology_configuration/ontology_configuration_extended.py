#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_configuration_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication
import sys

from pasta_eln.ontology_configuration.ontology_configuration import Ui_OntologyConfigurationBaseForm





class OntologyConfigurationForm(Ui_OntologyConfigurationBaseForm):
  def __init__(self, logger, db_instance):
    """

    Args:
      db_instance: Couch DB Instance passed by the parent
    """
    self.db = db_instance
    self.logger = logger

    print("")

  def setup_slots(self):
    self.loadPushButton.clicked.connect(self.load_ontology_data)

  def load_ontology_data(self):
    """
      Load button click event handler
    Args:

    Returns:

    """
    import uuid
    ontology_data = self.db['-ontology-']
    self.headerLabel.setText(str(uuid.uuid4()))
    for structure_key in filter(lambda d: type(ontology_data[d]) is dict, ontology_data):
      self.headerLabel.setText(str(ontology_data[structure_key]['label']))

    print("Clicked!!")


def get_db(db_name:str):
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
      db_instance = client.create_database(db_name)  #tests and initial creation of example data set requires this
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
