""" Represents a base model object. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: base_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from collections.abc import Generator
from typing import Any

from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class BaseModel:
  """
  Represents a base model object.

  Explanation:
      This class serves as a base for other model classes and provides common attributes and methods.

  """

  def __init__(self,
               _id: int | str | None = None):
    """
    Initializes a base model object.

    Args:
        _id (int| str | None): The ID of the object. Defaults to None.

    Raises:
        IncorrectParameterError: If the _id or _rev parameter is not of type str.

    """
    super().__init__()
    if isinstance(_id, int | str | None):
      self._id: int | str | None = _id
    else:
      raise IncorrectParameterError(f"Expected int | str | None type for id but got {type(_id)}")

  def __iter__(self) -> Generator[tuple[str, Any], None, None]:
    """
    Iterates over the attributes of the object and yields key-value pairs.

    Yields:
        tuple[str, Any]: A tuple containing the attribute name and its corresponding value.

    """
    for key in self.__dict__:
      yield key[1:], getattr(self, key)

  @property
  def id(self) -> int | str | None:
    """
    Returns the ID of the object.

    Returns:
        int | str | None: The ID of the object.

    """

    return self._id

  @id.setter
  def id(self, value: int | str | None) -> None:
    """
    Sets the ID of the object.

    Args:
        value (int | str | None): The ID value to be set.

    """
    self._id = value

  @id.deleter
  def id(self) -> None:
    """
    Deletes the ID of the object.

    """
    del self._id
