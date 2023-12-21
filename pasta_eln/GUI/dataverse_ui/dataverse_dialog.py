#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: dataverse_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog
from cloudant import CouchDB

from pasta_eln.GUI.dataverse_ui.dataverse_data_model import DataverseDataModel
from pasta_eln.GUI.dataverse_ui.dataverse_dialog_base import Ui_DataverseDialogBase


class DataverseDialog(Ui_DataverseDialogBase):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the create type dialog
    """
    return super(DataverseDialog, cls).__new__(cls)

  def __init__(self, db: CouchDB | None = None) -> None:
    """
    Initializes the creation type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.model = DataverseDataModel()
    self.listView.setModel(self.model)
    #test = db.
    self.model.add_data(["Project 1", "Project 2", "Project 3"] * 1000)

def get_db(db_name: str,
           db_user: str,
           db_pass: str,
           db_url: str) -> CouchDB | None:
  """
  Get the db instance for the test purpose
  Args:
    db_name (str): Database instance name in CouchDB
    db_user (str): Database user-name used for CouchDB access.
    db_pass (str): Database password used for CouchDB access.
    db_url (str): Database connection URL.
  Returns (CouchDB | None):
    Connected DB instance
  """
  try:
    client = CouchDB(user=db_user,
                     auth_token=db_pass,
                     url=db_url,
                     connect=True)
  except Exception:
    print('**ERROR dit01: Could not connect with username+password to local server')
    return
  if db_name in client.all_dbs():
    db_instance = client[db_name]
  else:
    db_instance = client.create_database(db_name)
  return db_instance

if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = DataverseDialog(get_db("research", "admin", "MJOBcBzGUWwW", 'http://127.0.0.1:5984'))
  ui.instance.show()
  sys.exit(app.exec())


