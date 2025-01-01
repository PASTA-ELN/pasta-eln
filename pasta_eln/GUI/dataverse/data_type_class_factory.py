""" Data type class factory. """
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


class DataTypeClassFactory:
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
    return super().__new__(cls)

  def __init__(self, context: DataTypeClassContext) -> None:
    """
    Initializes a new instance of the DataTypeClassFactory class.

    Explanation:
        This method initializes a new instance of the DataTypeClassFactory class.
    Args:
      context (DataTypeClassContext): The context of the data type class.
    """

    self.context: DataTypeClassContext = context
    self.factory_map: dict[DataTypeClassName, Any] = {
      DataTypeClassName.PRIMITIVE: self.make_primitive_data_type_class,
      DataTypeClassName.COMPOUND: self.make_compound_data_type_class,
      DataTypeClassName.CONTROLLED_VOCAB: self.make_controlled_vocab_data_type_class
    }

  def make_data_type_class(self, class_name: DataTypeClassName) -> DataTypeClass:
    """
    Creates an instance of a specific data type class based on the provided class name.

    Explanation:
        This method dynamically creates and returns an instance of a specific data type class based on the given class name.

    Args:
        class_name (DataTypeClassName): The name of the data type class to instantiate.

    Returns:
        DataTypeClass: An instance of the specified data type class.

    Raises:
        ValueError: If the provided data type class name is invalid.
    """
    if class_name in self.factory_map:
      return self.factory_map[class_name]()
    else:
      raise ValueError(f"Invalid data type class name: {class_name}")

  def make_primitive_data_type_class(self) -> DataTypeClass:
    """
    Creates an instance of a primitive data type class.

    Explanation:
        This method creates and returns an instance of a primitive data type class based on the context.

    Returns:
        DataTypeClass: An instance of a primitive data type class.
    """
    return PrimitiveDataTypeClass(self.context)

  def make_compound_data_type_class(self) -> DataTypeClass:
    """
    Creates an instance of a compound data type class.

    Explanation:
        This method creates and returns an instance of a compound data type class based on the context.

    Returns:
        DataTypeClass: An instance of a compound data type class.
    """
    return CompoundDataTypeClass(self.context)

  def make_controlled_vocab_data_type_class(self) -> DataTypeClass:
    """
    Creates an instance of a controlled vocabulary data type class.

    Explanation:
        This method creates and returns an instance of a controlled vocabulary data type class based on the context.

    Returns:
        DataTypeClass: An instance of a controlled vocabulary data type class.
    """
    return ControlledVocabularyDataTypeClass(self.context)
