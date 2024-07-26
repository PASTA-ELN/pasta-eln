""" Represents the data type class. """

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_type_class_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from abc import abstractmethod
from typing import Any

from pasta_eln.GUI.dataverse.data_type_class_context import DataTypeClassContext


class DataTypeClass(object):

  def __init__(self, context: DataTypeClassContext) -> None:
    self.context: DataTypeClassContext = context

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Creates a new instance of the DataTypeClass class.

    Explanation:
        This method creates a new instance of the DataTypeClass class.

    Args:
        *_: Variable length argument list.
        **__: Arbitrary keyword arguments.

    Returns:
        Any: The new instance of the DataTypeClass class.

    """
    return super(DataTypeClass, cls).__new__(cls)

  @abstractmethod
  def add_new_entry(self) -> None:
    """
    Saves the modifications made to the data type class.

    Explanation:
        This method saves the modifications made to the data type class.

    """
    return

  @abstractmethod
  def populate_entry(self) -> None:
    """
    Saves the modifications made to the data type class.

    Explanation:
        This method saves the modifications made to the data type class.

    """
    return

  @abstractmethod
  def save_modifications(self) -> None:
    """
    Saves the modifications made to the data type class.

    Explanation:
        This method saves the modifications made to the data type class.

    """
    return
