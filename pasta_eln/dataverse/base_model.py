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


class BaseModel(object):
  """
  Represents a base model object.

  Explanation:
      This class serves as a base for other model classes and provides common attributes and methods.

  """

  def __init__(self,
               _id: str | None = None,
               _rev: str | None = None):
    """
    Initializes a base model object.

    Args:
        _id (str | None): The ID of the object. Defaults to None.
        _rev (str | None): The revision of the object. Defaults to None.

    Raises:
        IncorrectParameterError: If the _id or _rev parameter is not of type str.

    """
    super().__init__()
    if isinstance(_id, str | None):
      self._id: str | None = _id
    else:
      raise IncorrectParameterError(f"Expected string type for id but got {type(_id)}")
    if isinstance(_rev, str | None):
      self._rev: str | None = _rev
    else:
      raise IncorrectParameterError(f"Expected string type for rev but got {type(_rev)}")

  def __iter__(self) -> Generator[tuple[str, Any], None, None]:
    """
    Iterates over the attributes of the object and yields key-value pairs.

    Yields:
        tuple[str, Any]: A tuple containing the attribute name and its corresponding value.

    """
    for key in self.__dict__:
      if key in ['_id', '_rev']:
        yield key, getattr(self, key)
      else:
        yield key[1:], getattr(self, key)

  @property
  def id(self) -> str | None:
    """
    Returns the ID of the object.

    Returns:
        str | None: The ID of the object.

    """

    return self._id

  @id.setter
  def id(self, value: str | None) -> None:
    """
    Sets the ID of the object.

    Args:
        value (str | None): The ID value to be set.

    Returns:
        None

    """
    self._id = value

  @id.deleter
  def id(self) -> None:
    """
    Deletes the ID of the object.

    Returns:
        None

    """
    del self._id

  @property
  def rev(self) -> str | None:
    """
    Returns the revision of the object.

    Returns:
        str | None: The revision of the object.

    """
    return self._rev

  @rev.setter
  def rev(self, value: str | None) -> None:
    """
    Sets the revision of the object.

    Args:
        value (str | None): The revision value to be set.

    Returns:
        None

    """
    self._rev = value

  @rev.deleter
  def rev(self) -> None:
    """
    Deletes the revision of the object.

    Returns:
        None

    """
    del self._rev
