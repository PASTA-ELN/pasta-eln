""" Represents the upload configuration dialog. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any, Callable

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QCheckBox, QDialog

from pasta_eln.GUI.dataverse.upload_config_dialog_base import Ui_UploadConfigDialog
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI


class UploadConfigDialog(Ui_UploadConfigDialog, QObject):
  """
  Represents the upload configuration dialog.

  Explanation:
      This class represents the upload configuration dialog.
      It provides methods to load and save the configuration settings.

  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the UploadConfigDialog class.

    Explanation:
        This method creates a new instance of the UploadConfigDialog class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the UploadConfigDialog class.
    """
    return super(UploadConfigDialog, cls).__new__(cls)

  def __init__(self, config_reloaded_callback: Callable[[], None]) -> None:
    """
    Initializes the UploadConfigDialog.

    Explanation:
        This method initializes the UploadConfigDialog class.
        It sets up the UI and initializes the necessary attributes.
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.db_api.initialize_database()
    self.numParallelComboBox.addItems(map(str, range(2, 6)))
    self.numParallelComboBox.setCurrentIndex(2)
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.config_model: ConfigModel | None = None
    self.data_hierarchy_types: list[str] = []
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_ui)
    (self.numParallelComboBox.currentTextChanged[str]
     .connect(lambda num: setattr(self.config_model, "parallel_uploads_count", int(num))))
    self.set_data_hierarchy_types()
    self.config_reloaded_callback = config_reloaded_callback
    self.load_ui()

  def load_ui(self) -> None:
    """
    Loads the UI for the UploadConfigDialog.

    Explanation:
        This method loads the UI for the UploadConfigDialog.
        It retrieves the config model from the database and sets up the UI elements based on the model data.
    """
    self.logger.info("Loading data and initializing UI...")
    self.config_model = self.db_api.get_config_model()
    if self.config_model is None:
      self.logger.error("Failed to load config model!")
      return
    for widget_pos in reversed(range(self.projectItemsVerticalLayout.count())):
      self.projectItemsVerticalLayout.itemAt(widget_pos).widget().setParent(None)
    for data_type in self.data_hierarchy_types:
      is_set = self.config_model.project_upload_items and self.config_model.project_upload_items.get(data_type, False)
      check_box = QCheckBox(text=data_type,  # type: ignore[call-overload]
                            parent=self.instance,
                            checkState=QtCore.Qt.Checked
                            if is_set else QtCore.Qt.Unchecked)
      self.projectItemsVerticalLayout.addWidget(check_box)
      check_box.stateChanged.connect(lambda state, item_name=check_box.text().capitalize():
                                     self.check_box_changed_callback(state, item_name))
    self.numParallelComboBox.setCurrentText(str(self.config_model.parallel_uploads_count))

  def check_box_changed_callback(self,
                                 state: QtCore.Qt.CheckState,
                                 project_item_name: str) -> None:
    """
    Updates the project upload items based on the state of a checkbox.

    Args:
        self: The instance of the class.
        state (QtCore.Qt.CheckState): The state of the checkbox.
        project_item_name (str): The name of the project item.

    Explanation:
        This function updates the project upload items in the config model based on the state of a checkbox.
        If the config model and project upload items are not None, it updates the project item with the given name
        to be checked or unchecked based on the state of the checkbox.
    """
    if self.config_model and self.config_model.project_upload_items is not None:
      self.config_model.project_upload_items.update({project_item_name: state == Qt.CheckState.Checked.value})

  def set_data_hierarchy_types(self) -> None:
    """
    Sets the data hierarchy types.

    Explanation:
        This method sets the data hierarchy types based on the data hierarchy retrieved from the database.
    """
    self.logger.info("Setting data hierarchy types...")
    data_hierarchy = self.db_api.get_data_hierarchy()
    if data_hierarchy is None:
      return
    for data_type in data_hierarchy:
      if (data_type and not data_type.isspace()
          and data_type not in ("x0", "x1", "x2")):
        type_capitalized = data_type.capitalize()
        if type_capitalized not in self.data_hierarchy_types:
          self.data_hierarchy_types.append(type_capitalized)
    self.data_hierarchy_types.append("Unidentified")

  def save_ui(self) -> None:
    """
    Saves the UI settings.

    Explanation:
        This method saves the UI settings to the configuration model.
        It retrieves the current settings from the UI elements and updates the configuration model.
        It then emits the config_reloaded signal to notify other components of the updated configuration.
    """
    self.logger.info("Saving config model...")
    if self.config_model is None:
      self.logger.error("Failed to load config model!")
      return
    self.db_api.save_config_model(self.config_model)
    self.config_reloaded_callback()

  def show(self) -> None:
    """
    Shows the instance.

    Explanation:
        This method shows the instance by calling its show() method.

    Args:
        self: The instance of the class.
    """
    self.instance.show()
