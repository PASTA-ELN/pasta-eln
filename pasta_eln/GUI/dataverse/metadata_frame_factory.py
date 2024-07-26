#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: metadata_frame_factory.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any

from pasta_eln.GUI.dataverse.controlled_vocab_frame import ControlledVocabFrame
from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName
from pasta_eln.GUI.dataverse.metadata_frame_base import MetadataFrame
from pasta_eln.GUI.dataverse.primitive_compound_frame import PrimitiveCompoundFrame


def make_primitive_compound_frame(metadata_field: dict[str, Any]) -> MetadataFrame:
  return PrimitiveCompoundFrame(metadata_field)


def make_controlled_vocab_frame(metadata_field: dict[str, Any]) -> MetadataFrame:
  return ControlledVocabFrame(metadata_field)


class MetadataFrameFactory(object):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the MetadataFrameFactory class.

    Explanation:
        This method creates a new instance of the MetadataFrameFactory class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the MetadataFrameFactory class.

    """
    return super(MetadataFrameFactory, cls).__new__(cls)

  def __init__(self) -> None:
    self.factory_map: dict[DataTypeClassName, Any] = {
      DataTypeClassName.PRIMITIVE: make_primitive_compound_frame,
      DataTypeClassName.COMPOUND: make_primitive_compound_frame,
      DataTypeClassName.CONTROLLED_VOCAB: make_controlled_vocab_frame
    }

  def make_metadata_frame(self, class_name: DataTypeClassName, metadata_field: dict[str, Any]) -> MetadataFrame:
    if class_name in self.factory_map:
      return self.factory_map[class_name](metadata_field)
    else:
      raise ValueError(f"Invalid data type class name: {class_name}")
