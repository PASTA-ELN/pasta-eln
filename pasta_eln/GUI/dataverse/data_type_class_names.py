""" Data type class names. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_type_class_names.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from enum import Enum


class DataTypeClassName(Enum):
  """
  An enumeration representing different data type class names.

  Explanation:
      This enumeration defines the names of different data type classes such as primitive, compound, and controlled vocabulary.

  """
  PRIMITIVE = "primitive"
  COMPOUND = "compound"
  CONTROLLED_VOCAB = "controlledVocabulary"

  def __str__(self) -> str:
    """
    Returns the string representation of the data type class name.

    Explanation:
        This method returns the string value of the data type class name.

    Returns:
        str: The string representation of the data type class name.
    """
    return self.value
