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
from pasta_eln.dataverse.utils import adjust_type_name


class EditMetadataDialog(Ui_EditMetadataDialog):
  """
  Represents the edit metadata dialog.

  This class provides methods to handle the UI and save the changes in the edit metadata dialog.

  Returns:
      Any: The new instance of the EditMetadataDialog class.

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

    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.primitive_compound_frame: PrimitiveCompoundFrame | None = None
    self.controlled_vocab_frame: ControlledVocabFrame | None = None
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)

    # Database API instance
    self.db_api = DatabaseAPI()
    self.config_model: ConfigModel = self.db_api.get_model(self.db_api.config_doc_id,
                                                           ConfigModel)  # type: ignore[assignment]

    # Initialize metadata
    self.metadata = self.config_model.metadata
    self.metadata_types = self.get_metadata_types()
    self.minimal_metadata = [
      {"name": "subject", "displayName": "Subject"},
      {"name": "author", "displayName": "Author"},
      {"name": "datasetContact", "displayName": "Dataset contact"},
      {"name": "dsDescription", "displayName": "Ds Description"}
    ]

    # Connect slots
    self.metadataBlockComboBox.currentTextChanged.connect(self.change_metadata_block)
    self.typesComboBox.currentTextChanged.connect(self.change_metadata_type)
    self.minimalFullComboBox.currentTextChanged[str].connect(self.toggle_minimal_full)
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_ui)
    self.licenseNameLineEdit.textChanged[str].connect(
      lambda name: self.config_model.metadata['datasetVersion']['license'].update({"name": name}))
    self.licenseURLLineEdit.textChanged[str].connect(
      lambda uri: self.config_model.metadata['datasetVersion']['license'].update({"uri": uri}))

    # Initialize UI elements
    self.load_ui()

  def get_metadata_types(self) -> dict[str, list[dict[str, str]]]:
    """Get the metadata types mapping.

    Retrieves the metadata types mapping from the loaded metadata model.
    The mapping is a dictionary where the keys are the display names of the metadata blocks,
    and the values are lists of dictionaries containing the name and display name of each field type.

    Returns:
        dict[str, list[dict[str, str]]]: The metadata types mapping.

    """
    self.logger.info("Loading metadata types mapping...")
    metadata_types_mapping: dict[str, list[dict[str, str]]] = {}
    if not self.metadata:
      self.logger.error("Failed to load metadata model!")
      return metadata_types_mapping
    for _, metablock in self.metadata['datasetVersion']['metadataBlocks'].items():
      if metablock['displayName'] not in metadata_types_mapping:
        metadata_types_mapping[metablock['displayName']] = []
      for field in metablock['fields']:
        if field['typeName'] not in metadata_types_mapping[metablock['displayName']]:
          metadata_types_mapping[metablock['displayName']].append(
            {
              'name': field['typeName'],
              'displayName': adjust_type_name(field['typeName'])
            }
          )
    return metadata_types_mapping

  def change_metadata_type(self) -> None:
    """
    Change the metadata type.

    Updates the UI elements based on the selected new_metadata_type.
    Clears the contents of UI elements and adds the appropriate UI elements based on the selected metadata type.

    """
    # Save the current modifications
    if self.primitive_compound_frame:
      self.primitive_compound_frame.save_modifications()
      self.primitive_compound_frame.instance.close()
    if self.controlled_vocab_frame:
      self.controlled_vocab_frame.save_modifications()
      self.controlled_vocab_frame.instance.close()
    # Clear the contents of UI elements
    for widget_pos in reversed(range(self.metadataScrollVerticalLayout.count())):
      self.metadataScrollVerticalLayout.itemAt(widget_pos).widget().setParent(None)
    if not self.metadata:
      self.logger.error("Failed to load metadata model!")
      return
    if new_metadata_type := self.typesComboBox.currentData(QtCore.Qt.ItemDataRole.UserRole):
      self.logger.info(f"Loading {new_metadata_type} metadata type...")
      dataset = self.metadata.get('datasetVersion', {})
      metadata_blocks = dataset.get('metadataBlocks', {})
      for _, metablock in metadata_blocks.items():
        for field in metablock['fields']:
          if field['typeName'] == new_metadata_type:
            self.logger.info(f"Loading {field['typeName']} metadata type of class: {field['typeClass']}...")
            match field['typeClass']:
              case "primitive" | "compound":
                self.primitive_compound_frame = PrimitiveCompoundFrame(field)
                self.metadataScrollVerticalLayout.addWidget(self.primitive_compound_frame.instance)
              case "controlledVocabulary":
                self.controlled_vocab_frame = ControlledVocabFrame(field)
                self.metadataScrollVerticalLayout.addWidget(self.controlled_vocab_frame.instance)

  def change_metadata_block(self, new_metadata_block: str | None = None) -> None:
    """
    Change the metadata block.

    Updates the typesComboBox based on the selected new_metadata_block.
    Clears the typesComboBox and adds the metadata types from the new_metadata_block.

    Args:
        new_metadata_block (str | None): The selected new metadata block.

    """
    if new_metadata_block:
      self.typesComboBox.clear()
      block = self.metadata_types.get(new_metadata_block, [])
      for meta_type in block:
        self.typesComboBox.addItem(meta_type['displayName'], userData=meta_type['name'])

  def toggle_minimal_full(self, selection: str) -> None:
    """
    Toggle between the minimal and full view of the metadata.

    Toggles the visibility of UI elements based on the selected selection.
    If the selection is "Minimal", hides the metadataBlockComboBox and clears the typesComboBox.
    If the selection is "Full", shows the metadataBlockComboBox and populates it with the metadata types.

    Args:
        selection (str): The selected view option ("Minimal" or "Full").

    """
    self.logger.info(f"Toggled to {selection} view...")
    match selection:
      case "Minimal":
        self.metadataBlockComboBox.hide()
        self.typesComboBox.clear()
        for meta_type in self.minimal_metadata:
          self.typesComboBox.addItem(meta_type['displayName'],
                                     userData=meta_type['name'])
      case "Full":
        self.metadataBlockComboBox.show()
        self.metadataBlockComboBox.clear()
        self.metadataBlockComboBox.addItems(self.metadata_types.keys())

  def load_ui(self) -> None:
    """
    Load the UI for the EditMetadataDialog.

    This method initializes the UI elements for the EditMetadataDialog.
    It adds items to combo boxes, sets text in line edits, and configures the UI based on the metadata.

    """
    self.logger.info("Loading UI...")
    self.metadataBlockComboBox.addItems(self.metadata_types.keys())
    self.minimalFullComboBox.addItems(["Full", "Minimal"])
    dataset_version = self.config_model.metadata.get('datasetVersion', {})
    dataset_license = dataset_version.get('license', {})
    self.licenseNameLineEdit.setText(dataset_license.get('name', ''))
    self.licenseURLLineEdit.setText(dataset_license.get('uri', ''))

  def save_ui(self) -> None:
    """
    Save the UI changes.

    Saves the changes made in the UI to the metadata.
    Updates the metadata in the config model and updates the model document in the database.

    """
    self.logger.info("Saving Config Model...")
    if self.controlled_vocab_frame:
      self.controlled_vocab_frame.save_modifications()
    if self.primitive_compound_frame:
      self.primitive_compound_frame.save_modifications()
    self.config_model.metadata = self.metadata
    self.db_api.update_model_document(self.config_model)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = EditMetadataDialog()
  ui.instance.show()
  sys.exit(app.exec())
