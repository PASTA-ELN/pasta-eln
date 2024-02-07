""" Represents the edit metadata dialog. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_edit_full_metadata.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog

from pasta_eln.GUI.dataverse.controlled_vocab_frame import ControlledVocabFrame
from pasta_eln.GUI.dataverse.edit_metadata_dialog_base import Ui_EditMetadataDialog
from pasta_eln.GUI.dataverse.primitive_compound_frame import PrimitiveCompoundFrame
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI


class EditMetadataDialog(Ui_EditMetadataDialog):
  """
  Represents the edit metadata dialog.

  Explanation:
      This class represents the edit metadata dialog and provides methods to handle the UI and save the changes.

  Args:
      None

  Returns:
      None
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the EditMetadataDialog class.

    Explanation:
        This method creates a new instance of the EditMetadataDialog class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the EditMetadataDialog class.
    """
    return super(EditMetadataDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes a new instance of the EditMetadataDialog class.

    Explanation:
        This method initializes a new instance of the EditMetadataDialog class.

    Args:
        None

    Returns:
        None
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.primitive_compound_frame: PrimitiveCompoundFrame | None = None
    self.controlled_vocab_frame: ControlledVocabFrame | None = None
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.config_model: ConfigModel = self.db_api.get_model(self.db_api.config_doc_id,
                                                           ConfigModel)  # type: ignore[assignment]
    self.metadata = self.config_model.metadata
    self.metadata_types = self.get_metadata_types()
    self.metadataBlockComboBox.currentTextChanged.connect(self.change_metadata_block)
    self.typesComboBox.currentTextChanged.connect(self.change_metadata_type)
    self.metadataBlockComboBox.addItems(self.metadata_types.keys())
    self.typesComboBox.addItems(self.metadata_types[self.metadataBlockComboBox.currentText()])
    self.minimalFullComboBox.addItems(["Minimal", "Full"])
    self.minimalFullComboBox.currentTextChanged.connect(self.toggle_minimal_full)
    self.minimalFullComboBox.setCurrentText("Full")
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_ui)

  def get_metadata_types(self) -> dict[str, list[str]]:
    """
    Retrieves the metadata types mapping.

    Explanation:
        This method retrieves the mapping of metadata block display names to their corresponding field type names.

    Args:
        None

    Returns:
        dict[str, list[str]]: The mapping of metadata block display names to their corresponding field type names.
    """
    metadata_types_mapping: dict[str, list[str]] = {}
    if not self.metadata:
      self.logger.error("Failed to load metadata model!")
      return metadata_types_mapping
    for _, metablock in self.metadata['datasetVersion']['metadataBlocks'].items():
      if metablock['displayName'] not in metadata_types_mapping:
        metadata_types_mapping[metablock['displayName']] = []
      for field in metablock['fields']:
        if field['typeName'] not in metadata_types_mapping[metablock['displayName']]:
          metadata_types_mapping[metablock['displayName']].append(field['typeName'])
    return metadata_types_mapping

  def change_metadata_type(self, new_metadata_type: str) -> None:
    """
    Changes the metadata type.

    Explanation:
        This method changes the metadata type based on the selected new_metadata_type.
        It clears the contents of UI elements and adds the appropriate UI elements based on the metadata type.

    Args:
        new_metadata_type (str): The selected new metadata type.

    """
    # Clear the contents of UI elements
    for widget_pos in reversed(range(self.metadataScrollVerticalLayout.count())):
      self.metadataScrollVerticalLayout.itemAt(widget_pos).widget().setParent(None)
    if not self.metadata:
      self.logger.error("Failed to load metadata model!")
      return
    for _, metablock in self.metadata['datasetVersion']['metadataBlocks'].items():
      for field in metablock['fields']:
        if field['typeName'] == new_metadata_type:
          match field['typeClass']:
            case "primitive":
              self.primitive_compound_frame = PrimitiveCompoundFrame({field['typeName']: field})
              self.metadataScrollVerticalLayout.addWidget(self.primitive_compound_frame.instance)
              break
            case "compound":
              self.primitive_compound_frame = PrimitiveCompoundFrame(field['value'][0])
              self.metadataScrollVerticalLayout.addWidget(self.primitive_compound_frame.instance)
              break
            case "controlledVocabulary":
              self.controlled_vocab_frame = ControlledVocabFrame(field['value'])
              self.metadataScrollVerticalLayout.addWidget(self.controlled_vocab_frame.instance)
              break

  def change_metadata_block(self, new_metadata_block: str | None = None) -> None:
    """
    Changes the metadata block.

    Explanation:
        This method changes the metadata block based on the selected new_metadata_block.
        It clears the contents of the typesComboBox and adds the appropriate metadata types based on the new metadata block.

    Args:
        new_metadata_block (str | None): The selected new metadata block.

    """
    if new_metadata_block:
      self.typesComboBox.clear()
      self.typesComboBox.addItems(self.metadata_types[new_metadata_block])

  def toggle_minimal_full(self, selection: str) -> None:
    """
    Toggles between the minimal and full view of the metadata.

    Explanation:
        This method toggles between the minimal and full view of the metadata based on the selected selection.
        It hides or shows the metadata block combo box and updates the types combo box accordingly.

    Args:
        selection (str): The selected view option ("Minimal" or "Full").

    """
    match selection:
      case "Minimal":
        self.metadataBlockComboBox.hide()
        self.typesComboBox.clear()
        self.typesComboBox.addItems(["subject", "author", "datasetContact", "dsDescription"])
      case "Full":
        self.metadataBlockComboBox.show()
        self.metadataBlockComboBox.clear()
        self.metadataBlockComboBox.addItems(self.metadata_types.keys())
        self.typesComboBox.clear()
        self.typesComboBox.addItems(self.metadata_types[self.metadataBlockComboBox.currentText()])

  def load_ui(self) -> None:
    """
    Loads the UI for the EditMetadataDialog.
    To be implemented.

    Explanation:
        This method loads the UI for the EditMetadataDialog.

    Args:
        None

    """
    self.logger.info("Loading UI...")

  def save_ui(self) -> None:
    """
    Saves the UI changes.

    Explanation:
        This method saves the changes made in the UI to the metadata.
        It updates the metadata in the config model and updates the model document in the database.

    Args:
        None

    """
    self.config_model.metadata = self.metadata
    self.db_api.update_model_document(self.config_model)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = EditMetadataDialog()
  ui.instance.show()
  sys.exit(app.exec())
