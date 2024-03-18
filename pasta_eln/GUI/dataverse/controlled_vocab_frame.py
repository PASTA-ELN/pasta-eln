""" Represents the controlled vocabulary frame. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: controlled_vocab_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QPushButton, QSizePolicy

from pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base import Ui_PrimitiveCompoundControlledFrameBase
from pasta_eln.dataverse.utils import delete_layout_and_contents


class ControlledVocabFrame(Ui_PrimitiveCompoundControlledFrameBase):
  """
  Represents a controlled vocabulary frame.

  Explanation:
      This class represents a controlled vocabulary frame.
      It provides methods for adding new vocabulary entries, saving modifications, and handling button callbacks.

  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates and returns a new instance of the ControlledVocabFrame class.

    Returns:
        Any: A new instance of the ControlledVocabFrame class.

    Explanation:
        This method creates and returns a new instance of the ControlledVocabFrame class.
        It overrides the __new__ method of the superclass to ensure proper instantiation.
    """
    return super(ControlledVocabFrame, cls).__new__(cls)

  def __init__(self, meta_field: dict[str, Any]) -> None:
    """
    Initializes a new instance of the ControlledVocabFrame class.

    Args:
        meta_field (dict[str, Any]): The meta field data.

    Explanation:
        This method initializes a new instance of the ControlledVocabFrame class.
        It sets up the logger, creates a QFrame instance, and connects the add button callback.
        It then loads the UI based on the meta_field data.

    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QFrame()
    super().setupUi(self.instance)
    self.meta_field = meta_field
    self.addPushButton.clicked.connect(self.add_button_callback)
    self.load_ui()

  def load_ui(self) -> None:
    """
    Loads the UI for the controlled vocabulary frame.

    Explanation:
        This method loads the UI for the controlled vocabulary frame.
        It adds new vocabulary entries based on the meta_field values.
        If the meta_field has 'multiple' set to True, it adds multiple entries.
        If the meta_field has 'multiple' set to False, it adds a single entry.

    Args:
        self: The instance of the class.
    """
    self.logger.info("Loading controlled vocabulary frame ui..")
    if self.meta_field.get('multiple'):
      if self.meta_field.get('value'):
        for value in self.meta_field.get('value'):
          self.add_new_vocab_entry(self.meta_field.get("valueTemplate"), value)
      else:
        self.add_new_vocab_entry(self.meta_field.get("valueTemplate"), None)
    else:
      self.add_new_vocab_entry(
        [self.meta_field.get("valueTemplate")],
        self.meta_field.get('value'))

  def add_button_callback(self) -> None:
    """
    Handles the button callback for adding a new vocabulary entry.

    Explanation:
        This method is called when the add button is clicked.
        It adds a new vocabulary entry based on the meta_field values.

    Args:
        self: The instance of the class.
    """
    self.logger.info("Adding new vocabulary entry, value: %s", self.meta_field)
    value_template = self.meta_field.get('valueTemplate')
    if self.meta_field.get('multiple'):
      self.add_new_vocab_entry(value_template, value_template[0]
      if value_template and len(value_template) > 0 else None)
    else:
      self.add_new_vocab_entry([value_template]
                               if value_template and len(value_template) > 0
                               else [], value_template)

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
    combo_box = QComboBox(parent=self.instance)
    combo_box.setObjectName("vocabComboBox")
    combo_box.setToolTip("Select the controlled vocabulary.")
    combo_box.addItems(controlled_vocabulary)
    combo_box.setCurrentText(value)
    new_vocab_entry_layout.addWidget(combo_box)
    delete_push_button = QPushButton(parent=self.instance)
    delete_push_button.setText("Delete")
    delete_push_button.setToolTip("Delete this particular vocabulary entry.")
    size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)
    size_policy.setHeightForWidth(delete_push_button.sizePolicy().hasHeightForWidth())
    delete_push_button.setSizePolicy(size_policy)
    delete_push_button.setMinimumSize(QSize(100, 0))
    delete_push_button.setObjectName("deletePushButton")
    new_vocab_entry_layout.addWidget(delete_push_button)
    delete_push_button.clicked.connect(lambda _: delete_layout_and_contents(new_vocab_entry_layout))
    self.mainVerticalLayout.addLayout(new_vocab_entry_layout)

  def save_modifications(self):
    """
    Saves the modifications made in the controlled vocabulary.

    Explanation:
        This method saves the modifications made in the controlled vocabulary.
        If the 'multiple' flag is True, it clears the 'value' list and retrieves the current text from each combo box.
        If the 'multiple' flag is False, it retrieves the current text from the single combo box.

    Args:
        self: The instance of the class.
    """
    if self.meta_field['multiple']:
      self.meta_field['value'].clear()
      for layout_pos in reversed(range(self.mainVerticalLayout.count())):
        if vocab_horizontal_layout := self.mainVerticalLayout.itemAt(layout_pos).layout():
          combo_box = vocab_horizontal_layout.itemAt(0).widget()
          if text := combo_box.currentText():
            self.meta_field.get('value').append(text)
      self.meta_field['value'] = list(set(self.meta_field.get('value')))
    elif layout := self.mainVerticalLayout.findChild(QHBoxLayout,
                                                     "vocabHorizontalLayout"):
      if combo_box := layout.itemAt(0).widget():
        self.meta_field['value'] = combo_box.currentText()
    else:
      self.logger.warning("Failed to save modifications, no layout found.")
    self.logger.info("Saved modifications successfully, value: %s", self.meta_field)
