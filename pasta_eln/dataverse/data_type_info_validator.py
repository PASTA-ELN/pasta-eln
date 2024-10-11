""" Provides methods to validate the properties of DataTypeInfo instances. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_type_info_validator.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pasta_eln.dataverse.data_type_info import DataTypeInfo


class DataTypeInfoValidator:
  """
  Validator for DataTypeInfo instances.

  This class provides methods to validate the properties of DataTypeInfo objects. It ensures that
  the required fields are present and correctly formatted, raising exceptions when validation fails.

  Methods:
      validate(data_type_info): Validates the provided DataTypeInfo instance.

  """

  @staticmethod
  def validate(data_type_info: DataTypeInfo) -> None:
    """
    Validate the provided DataTypeInfo instance to ensure it meets required criteria.

    This static method checks if the input is an instance of DataTypeInfo and verifies that
    both the datatype and title properties are set. If any of these conditions are not met,
    appropriate exceptions are raised to indicate the specific validation failure.

    Args:
        data_type_info (DataTypeInfo): The DataTypeInfo instance to validate.

    Raises:
        TypeError: If data_type_info is not an instance of DataTypeInfo.
        ValueError: If the datatype or title properties are missing.
    """
    if not isinstance(data_type_info, DataTypeInfo):
      raise TypeError(f"Expected DataTypeInfo type for data_type_info but got {type(data_type_info)}!")
    if not data_type_info.datatype:
      raise ValueError("Data type property is required!")
    if not data_type_info.title:
      raise ValueError("Displayed title property is required!")
