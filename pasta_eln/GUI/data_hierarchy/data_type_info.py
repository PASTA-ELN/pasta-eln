""" Represents data type information. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_type_info.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Any, Generator

from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError


class DataTypeInfo:
  """
  Represents metadata information for a data type.

  Explanation:
      This class encapsulates various attributes related to a data type, including its datatype, title, IRI, icon, and shortcut.
      It provides properties to access and modify these attributes while ensuring type safety.
      It provides properties to access and modify these attributes while ensuring type safety.

  Attributes:
      datatype (str | None): The type of the data.
      title (str | None): The title of the data type.
      iri (str | None): The Internationalized Resource Identifier for the data type.
      icon (str | None): The icon associated with the data type.
      shortcut (str | None): The shortcut for the data type.

  Methods:
      __iter__(): Iterates over the attributes of the object and yields key-value pairs.
  """

  def __init__(self) -> None:
    """
    Initializes a new instance of the DataTypeInfo class.

    Explanation:
        This constructor sets up the initial state of the DataTypeInfo instance by initializing its attributes.
        The attributes include datatype, title, IRI, icon, and shortcut, all set to their default values.
    """
    self._datatype: str | None = ""
    self._title: str | None = ""
    self._iri: str | None = ""
    self._icon: str | None = ""
    self._shortcut: str | None = ""

  @property
  def datatype(self) -> str | None:
    """
    Retrieves the data type of the information.

    Explanation:
        This property provides access to the internal attribute that stores the data type.
        It allows users to retrieve the current data type without modifying it.

    Returns:
        str: The current data type.
    """
    return self._datatype

  @datatype.setter
  def datatype(self, datatype: str | None) -> None:
    """
    Sets the data type of the information.

    Explanation:
        This setter method allows the user to update the internal data type attribute.
        It ensures that the provided value is a string; if not, it raises an IncorrectParameterError.

    Args:
        datatype (str): The new data type to set.

    Raises:
        IncorrectParameterError: If the provided datatype is not a string.
    """
    if isinstance(datatype, str):
      self._datatype = datatype
    else:
      raise IncorrectParameterError(f"Expected string type for datatype but got {type(datatype)}")

  @property
  def title(self) -> str | None:
    """
    Retrieves the title of the data type.

    Explanation:
        This property provides access to the internal attribute that stores the title of the data type.
        It allows users to retrieve the current title without modifying it.

    Returns:
        str | None: The current title of the data type, or None if not set.
    """
    return self._title

  @title.setter
  def title(self, title: str | None) -> None:
    """
    Sets the title of the data type.

    Explanation:
        This setter method allows the user to update the internal title attribute of the data type.
        It ensures that the provided value is either a string or None; if not, it raises an IncorrectParameterError.

    Args:
        title (str | None): The new title to set for the data type.

    Raises:
        IncorrectParameterError: If the provided title is not a string or None.
    """
    if isinstance(title, str | None):
      self._title = title
    else:
      raise IncorrectParameterError(f"Expected string type for displayed title but got {type(title)}")

  @property
  def iri(self) -> str | None:
    """
    Retrieves the Internationalized Resource Identifier (IRI) of the data type.

    Explanation:
        This property provides access to the internal attribute that stores the IRI of the data type.
        It allows users to retrieve the current IRI without modifying it.

    Returns:
        str | None: The current IRI of the data type, or None if not set.
    """
    return self._iri

  @iri.setter
  def iri(self, iri: str | None) -> None:
    """
    Sets the Internationalized Resource Identifier (IRI) of the data type.

    Explanation:
        This setter method allows the user to update the internal IRI attribute of the data type.
        It ensures that the provided value is either a string or None; if not, it raises an IncorrectParameterError.

    Args:
        iri (str | None): The new IRI to set for the data type.

    Raises:
        IncorrectParameterError: If the provided iri is not a string or None.
    """
    if isinstance(iri, str | None):
      self._iri = iri
    else:
      raise IncorrectParameterError(f"Expected string type for iri but got {type(iri)}")

  @property
  def icon(self) -> str | None:
    """
    Retrieves the icon associated with the data type.

    Explanation:
        This property provides access to the internal attribute that stores the icon of the data type.
        It allows users to retrieve the current icon without modifying it.

    Returns:
        str | None: The current icon of the data type, or None if not set.
    """
    return self._icon

  @icon.setter
  def icon(self, icon: str | None) -> None:
    """
    Sets the icon associated with the data type.

    Explanation:
        This setter method allows the user to update the internal icon attribute of the data type.
        It ensures that the provided value is either a string or None; if not, it raises an IncorrectParameterError.

    Args:
        icon (str | None): The new icon to set for the data type.

    Raises:
        IncorrectParameterError: If the provided icon is not a string or None.
    """
    if isinstance(icon, str | None):
      self._icon = icon
    else:
      raise IncorrectParameterError(f"Expected string type for icon but got {type(icon)}")

  @property
  def shortcut(self) -> str | None:
    """
    Retrieves the shortcut associated with the data type.

    Explanation:
        This property provides access to the internal attribute that stores the shortcut for the data type.
        It allows users to retrieve the current shortcut without modifying it.

    Returns:
        str | None: The current shortcut of the data type, or None if not set.
    """
    return self._shortcut

  @shortcut.setter
  def shortcut(self, shortcut: str | None) -> None:
    """
    Sets the shortcut associated with the data type.

    Explanation:
        This setter method allows the user to update the internal shortcut attribute of the data type.
        It ensures that the provided value is either a string or None; if not, it raises an IncorrectParameterError.

    Args:
        shortcut (str | None): The new shortcut to set for the data type.

    Raises:
        IncorrectParameterError: If the provided shortcut is not a string or None.
    """
    if isinstance(shortcut, str | None):
      self._shortcut = shortcut
    else:
      raise IncorrectParameterError(f"Expected string type for shortcut but got {type(shortcut)}")

  def __iter__(self) -> Generator[tuple[str, Any], None, None]:
    """
    Iterates over the attributes of the object and yields key-value pairs.

    Yields:
        tuple[str, Any]: A tuple containing the attribute name and its corresponding value.

    """
    for key in self.__dict__:
      yield key[1:], getattr(self, key)
