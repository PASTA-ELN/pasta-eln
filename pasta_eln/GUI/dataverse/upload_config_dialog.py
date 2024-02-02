#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QCheckBox, QDialog

from pasta_eln.GUI.dataverse.upload_config_dialog_base import Ui_UploadConfigDialog
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI


class UploadConfigDialog(Ui_UploadConfigDialog, QObject):
  config_reloaded = QtCore.Signal()
  def __new__(cls, *_: Any, **__: Any) -> Any:
    return super(UploadConfigDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the creation type dialog
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.numParallelComboBox.addItems(map(str, range(2, 9)))
    self.numParallelComboBox.setCurrentIndex(2)
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.config_model: ConfigModel = None
    self.data_hierarchy_types: list[str] = []
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(lambda: self.save_ui())
    self.set_data_hierarchy_types()
    self.load_ui()

  def load_ui(self):
    self.config_model = self.db_api.get_model("-dataverseConfig-", ConfigModel)
    for widget_pos in reversed(range(self.projectItemsVerticalLayout.count())):
      self.projectItemsVerticalLayout.itemAt(widget_pos).widget().setParent(None)
    for data_type in self.data_hierarchy_types:
      self.projectItemsVerticalLayout.addWidget(QCheckBox(text=data_type,
                                                          parent=self.instance,
                                                          checkState=QtCore.Qt.Checked
                                                          if self.config_model.project_upload_items.get(data_type,
                                                                                                        False)
                                                          else QtCore.Qt.Unchecked))
    self.numParallelComboBox.setCurrentText(str(self.config_model.parallel_uploads_count))

  def set_data_hierarchy_types(self):
    for data_type in self.db_api.get_data_hierarchy():
      if data_type not in ("x0", "x1", "x2"):
        type_capitalized = data_type.capitalize()
        if type_capitalized and type_capitalized not in self.data_hierarchy_types:
          self.data_hierarchy_types.append(type_capitalized)
    self.data_hierarchy_types.append("Unidentified")

  def save_ui(self):
    self.config_model.parallel_uploads_count = int(self.numParallelComboBox.currentText())
    items = {}
    for widget_pos in reversed(range(self.projectItemsVerticalLayout.count())):
      check_box = self.projectItemsVerticalLayout.itemAt(widget_pos).widget()
      items[check_box.text()] = check_box.checkState() == QtCore.Qt.Checked
    self.config_model.project_upload_items = items
    self.db_api.update_model_document(self.config_model)
    self.config_reloaded.emit()


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)
  ui = UploadConfigDialog()
  ui.instance.show()
  sys.exit(app.exec())
