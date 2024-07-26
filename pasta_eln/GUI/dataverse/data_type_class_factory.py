#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_type_class_factory.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any

from pasta_eln.GUI.dataverse.compound_data_type_class import CompoundDataTypeClass
from pasta_eln.GUI.dataverse.controlled_vocabulary_data_type_class import ControlledVocabularyDataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_base import DataTypeClass
from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext
from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName
from pasta_eln.GUI.dataverse.primitive_data_type_class import PrimitiveDataTypeClass


class DataTypeClassFactory(object):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the DataTypeClassFactory class.

    Explanation:
        This method creates a new instance of the DataTypeClassFactory class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the DataTypeClassFactory class.

    """
    return super(DataTypeClassFactory, cls).__new__(cls)

  def __init__(self, context: DataTypeClassContext) -> None:
    self.context: DataTypeClassContext = context
    self.factory_map: dict[DataTypeClassName, Any] = {
      DataTypeClassName.PRIMITIVE: self.make_primitive_data_type_class,
      DataTypeClassName.COMPOUND: self.make_compound_data_type_class,
      DataTypeClassName.CONTROLLED_VOCAB: self.make_controlled_vocab_data_type_class
    }

  def make_data_type_class(self, class_name: DataTypeClassName) -> DataTypeClass:
    if class_name in self.factory_map:
      return self.factory_map[class_name]()
    else:
      raise ValueError(f"Invalid data type class name: {class_name}")

  def make_primitive_data_type_class(self) -> DataTypeClass:
    return PrimitiveDataTypeClass(self.context)

  def make_compound_data_type_class(self) -> DataTypeClass:
    return CompoundDataTypeClass(self.context)

  def make_controlled_vocab_data_type_class(self) -> DataTypeClass:
    return ControlledVocabularyDataTypeClass(self.context)
