"""Icon names for the data hierarchy."""
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: icon_names_singleton.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

import qtawesome as qta

from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class SingletonMeta(type):
  """
  A metaclass that implements the Singleton design pattern.

  Explanation:
      This metaclass ensures that a class has only one instance and provides a global point of access to it.
      When a class is created using this metaclass, it checks if an instance already exists; if not, it creates one.

  Returns:
      The single instance of the class.
  """
  _instances = {}

  def __call__(cls, *args, **kwargs):
    """
    Creates or retrieves the singleton instance of the class.

    Explanation:
        This method is called when an instance of the class is requested.
        It checks if an instance already exists; if not, it creates a new instance and stores it for future requests.

    Args:
        *args: Variable length argument list for the class constructor.
        **kwargs: Arbitrary keyword arguments for the class constructor.

    Returns:
        The single instance of the class.
    """
    if cls not in cls._instances:
      instance = super().__call__(*args, **kwargs)
      cls._instances[cls] = instance
    return cls._instances[cls]


class QTAIconsSingleton(metaclass=SingletonMeta):
  """
  Singleton class for managing QTA icons.

  Explanation:
      This class ensures that there is only one instance of QTAIconsSingleton throughout the application.
      It initializes and manages icon names and font collections for use in the UI.

  Attributes:
      logger (logging.Logger): Logger for the class.
      _icon_names (dict[str, list[str]]): Dictionary to store icon names categorized by font collections.
      _font_collections (list[str]): List of font collections used for icons.
      _icons_initialized (bool): Flag indicating whether the icons have been initialized.

  Methods:
      set_icon_names(): Initializes the icon names based on the available font collections.
      font_collections: Property to get or set the font collections.
      icon_names: Property to get or set the icon names.
  """

  def __init__(self) -> None:
    """
    Initializes the QTAIconsSingleton instance.

    Explanation:
        This method sets up the logger for the class and initializes the icon names and font collections.
        It also calls the method to set the icon names, ensuring that the instance is ready for use.
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self._icon_names: dict[str, list[str]] = {}
    self._font_collections = ['fa', 'fa5', 'fa5s', 'fa5b', 'ei', 'mdi', 'mdi6', 'ph', 'ri', 'msc']
    self._icons_initialized = False
    self.set_icon_names()

  def set_icon_names(self) -> None:
    """
    Initializes the icon names based on the available font collections.

    Explanation:
        This method sets up the icon names for each font collection by retrieving the font maps from the qta resource.
        If the icons have already been initialized, a warning is logged, and the method exits early.
        The method populates the _icon_names dictionary with the available icons for each font collection.
    """
    self._icon_names = {fc: [] for fc in self.font_collections}
    if self._icons_initialized:
      self.logger.warning("Icons already initialized!")
      return
    qta._instance()
    font_maps = qta._resource['iconic'].charmap
    if font_maps is None or not font_maps:
      self.logger.warning("font_maps could not be found!")
      return
    for fc in self._font_collections:
      self._icon_names[fc].append("No value")
      for iconName in font_maps[fc]:
        icon_name = f'{fc}.{iconName}'
        self._icon_names[fc].append(icon_name)
    self._icons_initialized = True

  @property
  def font_collections(self) -> list[str]:
    """
    Retrieves the list of font collections used for icons.

    Explanation:
        This property returns the internal list of font collections that are available for use in the icon management system.
        It provides access to the font collections without allowing modification of the internal state.

    Returns:
        list[str]: The list of font collections.
    """
    return self._font_collections

  @font_collections.setter
  def font_collections(self, font_collections: list[str]) -> None:
    """
    Sets the list of font collections used for icons.

    Explanation:
        This setter method allows the user to update the internal list of font collections.
        It ensures that the provided value is a list; if not, it raises an IncorrectParameterError.

    Args:
        font_collections (list[str]): The new list of font collections to set.

    Raises:
        IncorrectParameterError: If the provided font_collections is not a list.
    """
    if isinstance(font_collections, list):
      self._font_collections = font_collections
    else:
      raise IncorrectParameterError(f"Expected list type for font_collections but got {type(font_collections)}")

  @property
  def icon_names(self) -> dict[str, list[str]]:
    """
    Retrieves the dictionary of icon names categorized by font collections.

    Explanation:
        This property checks if the icons have been initialized; if not, it calls the method to set the icon names.
        It returns the internal dictionary containing the icon names for each font collection.

    Returns:
        dict[str, list[str]]: A dictionary where the keys are font collection names and the values are lists of icon names.
    """
    if not self._icons_initialized:
      self.set_icon_names()
    return self._icon_names

  @icon_names.setter
  def icon_names(self, icon_names: dict[str, list[str]]) -> None:
    """
    Sets the dictionary of icon names categorized by font collections.

    Explanation:
        This setter method allows the user to update the internal dictionary of icon names.
        It ensures that the provided value is a dictionary; if not, it raises an IncorrectParameterError.

    Args:
        icon_names (dict[str, list[str]]): The new dictionary of icon names to set.

    Raises:
        IncorrectParameterError: If the provided icon_names is not a dictionary.
    """
    if isinstance(icon_names, dict):
      self._icon_names = icon_names
    else:
      raise IncorrectParameterError(f"Expected list type for icon_names but got {type(icon_names)}")
