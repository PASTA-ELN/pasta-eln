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
from PySide6.QtWidgets import QFrame
from pasta_eln.GUI.dataverse.data_type_class_base import DataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.data_type_class_factory import DataTypeClassFactory
from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName
from pasta_eln.GUI.dataverse.metadata_frame_base import MetadataFrame
from pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base import Ui_PrimitiveCompoundControlledFrameBase


class ControlledVocabFrame(Ui_PrimitiveCompoundControlledFrameBase, MetadataFrame):
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
    return super().__new__(cls)

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
    super().__init__(self.instance)
    self.meta_field: dict[str, Any] = meta_field
    self.data_type_class_factory: DataTypeClassFactory = DataTypeClassFactory(
      DataTypeClassContext(self.mainVerticalLayout, self.addPushButton, self.instance, meta_field)
    )
    self.data_type: DataTypeClass = self.data_type_class_factory.make_data_type_class(
      DataTypeClassName(meta_field['typeClass'])
    )
    self.addPushButton.clicked.connect(self.add_button_click_handler)
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
    self.logger.info('Loading controlled vocabulary frame ui..')
    self.data_type.populate_entry()

  def add_button_click_handler(self) -> None:
    """
    Handles the button callback for adding a new vocabulary entry.

    Explanation:
        This method is called when the add button is clicked.
        It adds a new vocabulary entry based on the meta_field values.

    Args:
        self: The instance of the class.
    """
    self.logger.info('Adding new vocabulary entry, value: %s', self.meta_field)
    self.data_type.add_new_entry()

  def save_modifications(self) -> None:
    """
    Saves the modifications made in the controlled vocabulary.

    Explanation:
        This method saves the modifications made in the controlled vocabulary.
        If the 'multiple' flag is True, it clears the 'value' list and retrieves the current text from each combo box.
        If the 'multiple' flag is False, it retrieves the current text from the single combo box.

    Args:
        self: The instance of the class.
    """
    self.data_type.save_modifications()
