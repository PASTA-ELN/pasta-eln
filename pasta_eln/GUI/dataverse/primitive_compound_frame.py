""" Adds a new compound entry. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: primitive_compound_frame.py
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


class PrimitiveCompoundFrame(Ui_PrimitiveCompoundControlledFrameBase, MetadataFrame):
  """
  Adds a new compound entry.

  Explanation:
      This method adds a new compound entry to the UI.
      It creates a new layout for the entry and adds the appropriate UI elements based on the types dictionary.

  """

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the PrimitiveCompoundFrame class.

    Explanation:
        This method creates a new instance of the PrimitiveCompoundFrame class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the PrimitiveCompoundFrame class.
    """
    return super(PrimitiveCompoundFrame, cls).__new__(cls)

  def __init__(self, meta_field: dict[str, Any]) -> None:
    """
    Initializes the PrimitiveCompoundFrame.

    Explanation:
        This method initializes the PrimitiveCompoundFrame class.
        It sets up the UI and initializes the types dictionary.

    Args:
        meta_field (dict[str, Any]): The dictionary containing the metadata field information.
    """
    self.logger: logging.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance: QFrame = QFrame()
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
    Loads the UI based on the meta_field information.

    Args:
        self: The instance of the class.

    Explanation:
        This method loads the UI based on the meta_field information.
        It handles different cases based on the 'typeClass' value in the meta_field dictionary.
        - For 'primitive' type, it disables the addPushButton if 'multiple' is False and populates the primitive entry.
        - For 'compound' type, it handles the cases of 'multiple' being True or False.
          - If 'multiple' is True and the 'value' is empty, it creates an empty entry and populates the compound entry.
          - If 'multiple' is True and the 'value' is not empty, it populates the compound entry for each compound in the 'value'.
          - If 'multiple' is False and the 'value' is not empty, it populates the compound entry with the 'value'.
          - If 'multiple' is False and the 'value' is empty, it creates an empty entry and populates the compound entry.
        - For any other 'typeClass' value, it logs an error for unknown typeClass.

    """
    self.logger.info("Loading UI for %s", self.meta_field)
    self.data_type.populate_entry()

  def add_button_click_handler(self) -> None:
    """
        Adds a new entry based on the meta_field information.

        Explanation:
            This method adds a new entry based on the meta_field information.
            It handles different cases based on the 'typeClass' value in the meta_field dictionary.
            - For 'primitive' type, it populates the primitive horizontal layout with the specified values.
            - For 'compound' type, it creates a new compound horizontal layout and populates it with the specified values.
            - For any other 'typeClass' value, it logs an error for unknown typeClass.

    """
    self.logger.info("Adding new entry of type %s, name: %s",
                     self.meta_field.get('typeClass', ''),
                     self.meta_field.get('typeName', ''))
    if not self.meta_field.get('multiple'):
      self.logger.error("Add operation not supported for non-multiple entries")
      return
    self.data_type.add_new_entry()

  def save_modifications(self) -> None:
    """
    Saves the changes made in UI elements to the meta_field.

    Args:
        self: The instance of the class.

    Explanation:
        This method saves the changes made to the meta_field.
        It handles different cases based on the 'typeClass' value in the meta_field dictionary.
        - For 'primitive' type, it updates the 'value' attribute of the meta_field.
        - For 'compound' type, it updates the 'value' attribute of the meta_field based on the 'valueTemplate'.
        - For any other 'typeClass' value, it logs an error for unsupported typeClass.
    """
    self.logger.info("Saving changes to meta_field for type, name: %s, class: %s",
                     self.meta_field.get('typeName'),
                     self.meta_field.get('typeClass'))
    self.data_type.save_modifications()
