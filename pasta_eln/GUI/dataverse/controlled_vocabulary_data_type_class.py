""" Represents the controlled vocabulary data type class. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: controlled_vocabulary_data_type_class.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6.QtWidgets import QComboBox, QHBoxLayout

from pasta_eln.GUI.dataverse.data_type_class_base import DataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.utility_functions import add_clear_button, add_delete_button


class ControlledVocabularyDataTypeClass(DataTypeClass):
  """
  Represents the controlled vocabulary data type class.
  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the ControlledVocabularyDataTypeClass class.

    Explanation:
        This method creates a new instance of the ControlledVocabularyDataTypeClass class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the ControlledVocabularyDataTypeClass class.

    """
    return super(ControlledVocabularyDataTypeClass, cls).__new__(cls)

  def __init__(self, context: DataTypeClassContext) -> None:
    """
    Initializes a new instance of the ControlledVocabularyDataTypeClass class.

    Explanation:
        This method initializes a new instance of the ControlledVocabularyDataTypeClass class.
    Args:
      context (DataTypeClassContext): The context of the data type class.
    """
    super().__init__(context)
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

  def add_new_entry(self) -> None:
    """
    Adds a new entry to the controlled vocabulary.

    Explanation:
        This method adds a new entry to the controlled vocabulary.
    """
    value_template = self.context.meta_field.get('valueTemplate')
    if self.context.meta_field.get('multiple'):
      self.add_new_vocab_entry(value_template, value_template[0] if value_template else None)
    else:
      self.add_new_vocab_entry(
        ["No Value", value_template] if value_template else ["No Value"],
        value_template or "No Value"
      )

  def populate_entry(self) -> None:
    """
    Populates the entry with the current value of the controlled vocabulary.

    Explanation:
        This method populates the entry with the current value of the controlled vocabulary.
    """
    value_block = self.context.meta_field.get('value')
    value_template = self.context.meta_field.get("valueTemplate")
    if self.context.meta_field.get('multiple'):
      if value_block:
        for value in value_block:
          self.add_new_vocab_entry(value_template, value)
      else:
        self.add_new_vocab_entry(value_template, None)
    else:
      self.add_new_vocab_entry(
        ["No Value", value_template] if value_template else ["No Value"],
        value_block or "No Value"
      )

  def save_modifications(self) -> None:
    """
    Saves the modifications to the controlled vocabulary.

    Explanation:
        This method saves the modifications to the controlled vocabulary.
    """
    if self.context.meta_field.get('multiple'):
      self.save_multiple_entries()
      self.logger.info("Saved multiple entry modifications successfully, value: %s", self.context.meta_field)
    elif layout := self.context.main_vertical_layout.findChild(QHBoxLayout,
                                                               "vocabHorizontalLayout"):
      if not isinstance(layout, QHBoxLayout):
        self.logger.error("vocabHorizontalLayout not found!")
        return
      self.save_single_entry(layout)
      self.logger.info("Saved single entry modification successfully, value: %s", self.context.meta_field)
    else:
      self.logger.warning("Failed to save modifications, no layout found.")

  def save_single_entry(self, layout: QHBoxLayout) -> None:
    """
    Saves the single entry to the controlled vocabulary.

    Explanation:
        This method saves the single entry to the controlled vocabulary.
    Args:
      layout (QHBoxLayout): The layout of the single entry.
    """
    if combo_box := layout.itemAt(0).widget():
      if not isinstance(combo_box, QComboBox):
        self.logger.error("Combo box not found!")
        return
      current_text = combo_box.currentText()
      self.context.meta_field['value'] = current_text if current_text and current_text != 'No Value' else None
    else:
      self.context.meta_field['value'] = None
      self.logger.error("Combo box not found!")

  def save_multiple_entries(self) -> None:
    """
    Saves the multiple entries to the controlled vocabulary.

    Explanation:
        This method saves the multiple entries to the controlled vocabulary.
    """
    value = self.context.meta_field.get('value')
    if not isinstance(value, list):
      self.logger.error("Value is not a list")
      return
    value.clear()
    for layout_pos in reversed(range(self.context.main_vertical_layout.count())):
      if vocab_horizontal_layout := self.context.main_vertical_layout.itemAt(layout_pos).layout():
        combo_box = vocab_horizontal_layout.itemAt(0)
        if combo_box is not None:
          combo_boxW = combo_box.widget()
        if not isinstance(combo_boxW, QComboBox):
          continue
        text = combo_boxW.currentText()
        if text and text != 'No Value':
          value.append(text)
    self.context.meta_field['value'] = list(set(value))

  def add_new_vocab_entry(self,
                          controlled_vocabulary: list[str] | None = None,
                          value: str | None = None) -> None:
    """
    Adds a new vocabulary entry to the controlled vocabulary frame.

    Args:
        controlled_vocabulary (list[str] | None): The list of controlled vocabulary options.
        value (str | None): The initial value for the vocabulary entry.

    Explanation:
        This method adds a new vocabulary entry to the controlled vocabulary frame.
        It creates a new layout with a combo box and a delete button, and adds it to the main vertical layout.
        The combo box is populated with the controlled vocabulary options, and the initial value is set if provided.
        The delete button is connected to the delete_layout_and_contents function to handle deletion of the entry.
    """
    new_vocab_entry_layout = QHBoxLayout()
    new_vocab_entry_layout.setObjectName("vocabHorizontalLayout")
    combo_box = QComboBox(parent=self.context.parent_frame)
    combo_box.setObjectName("vocabComboBox")
    combo_box.setToolTip("Select the controlled vocabulary.")
    combo_box.addItems(controlled_vocabulary or [])
    combo_box.setCurrentText(value or "")
    new_vocab_entry_layout.addWidget(combo_box)
    add_clear_button(self.context.parent_frame, new_vocab_entry_layout)
    add_delete_button(self.context.parent_frame, new_vocab_entry_layout)
    self.context.main_vertical_layout.addLayout(new_vocab_entry_layout)
