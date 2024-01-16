#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_edit_full_metadata.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from json import load
from os import getcwd
from os.path import dirname, join, realpath
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog

from pasta_eln.GUI.dataverse_ui.dataverse_controlled_vocab_frame import ControlledVocabFrame
from pasta_eln.GUI.dataverse_ui.dataverse_edit_metadata_dialog_base import Ui_EditMetadataDialog
from pasta_eln.GUI.dataverse_ui.dataverse_primitive_compound_frame import PrimitiveCompoundFrame


class EditMetadataDialog(Ui_EditMetadataDialog):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the create type dialog
    """
    return super(EditMetadataDialog, cls).__new__(cls)

  def __init__(self) -> None:
    """
    Initializes the creation type dialog
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.primitive_compound_frame = None
    self.controlled_vocab_frame = None
    self.instance = QDialog()
    super().setupUi(self.instance)
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, "..//..//dataverse//dataset-create-new-all-default-fields.json"),
              encoding="utf-8") as config_file:
      self.metadata = load(config_file)
    self.metadata_types = self.get_metadata_types()
    self.metadataBlockComboBox.currentTextChanged.connect(self.change_metadata_block)
    self.typesComboBox.currentTextChanged.connect(self.change_metadata_type)
    self.metadataBlockComboBox.addItems(self.metadata_types.keys())
    self.typesComboBox.addItems(self.metadata_types[self.metadataBlockComboBox.currentText()])
    self.minimalFullComboBox.addItems(["Minimal", "Full"])
    self.minimalFullComboBox.currentTextChanged.connect(self.toggle_minimal_full)
    self.minimalFullComboBox.setCurrentText("Full")

  def get_metadata_types(self):
    metadata_types_mapping = {}
    for _, metablock in self.metadata['datasetVersion']['metadataBlocks'].items():
      if metablock['displayName'] not in metadata_types_mapping:
        metadata_types_mapping[metablock['displayName']] = []
      for field in metablock['fields']:
        if field['typeName'] not in metadata_types_mapping[metablock['displayName']]:
          metadata_types_mapping[metablock['displayName']].append(field['typeName'])
    return metadata_types_mapping

  def change_metadata_type(self, new_metadata_type: str):
    # Clear the contents of UI elements
    for widget_pos in reversed(range(self.metadataScrollVerticalLayout.count())):
      self.metadataScrollVerticalLayout.itemAt(widget_pos).widget().setParent(None)
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

  def change_metadata_block(self, new_metadata_block: str = None):
    if new_metadata_block:
      self.typesComboBox.clear()
      self.typesComboBox.addItems(self.metadata_types[new_metadata_block])

  def toggle_minimal_full(self, selection: str):
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


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = EditMetadataDialog()
  ui.instance.show()
  sys.exit(app.exec())
