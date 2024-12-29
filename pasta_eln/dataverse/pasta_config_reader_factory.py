""" PastaConfigReaderFactory is a singleton class responsible for managing the configuration of the application. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: pasta_config_reader_factory.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from json import load
from os.path import exists, join
from pathlib import Path
from threading import Lock
from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import QFileSystemWatcher

from pasta_eln.dataverse.config_error import ConfigError


class PastaConfigReaderFactory:
  """
  PastaConfigReaderFactory is a singleton class responsible for managing the configuration of the application.

  This class provides methods to read, update, and delete the configuration,
  as well as to monitor changes to the configuration file. It ensures that only one instance of the
  class exists and handles thread safety for configuration access.

  Attributes:
      _instance (Any): The singleton instance of the class.
      logger (Logger): Logger for logging configuration actions.
      config_file_name (str): The path to the configuration file.
      config (dict[str, Any]): The current configuration dictionary.
      mutex (Lock): A mutex for thread-safe access to the configuration.
      fs_watcher (QFileSystemWatcher): A file system watcher to monitor changes to the configuration file.

  Methods:
      get_instance: Retrieve the singleton instance of the class.
      __init__: Initialize the PastaConfigReaderFactory instance.
      read_pasta_config: Read the configuration file and update the internal configuration.
      config_file_changed: Handle changes to the configuration file.
      config: Property to get, set, and delete the current configuration.
  Note:
      This class is a singleton. It ensures that only one instance of the class exists.
      Make sure to use the get_instance() method to retrieve the singleton instance.
      Make sure that this class is initialized only after the instantiation of QApplication.instance() in-order to
        ensure that the file system watcher is properly set up and the signal-slot connections works as expected.
  """

  _instance: Any = None

  @classmethod
  def get_instance(cls) -> Any:
    """
    Retrieve the singleton instance of the class.

    This method ensures that only one instance of the class is created and returned. If an instance does not already exist, it creates a new one; otherwise, it returns the existing instance.

    Returns:
        Any: The singleton instance of the class PastaConfigReaderFactory.
    """
    if (not hasattr(cls, '_instance')
        or not getattr(cls, '_instance')):
      cls._instance = cls()
    return cls._instance

  def __init__(self) -> None:
    """
    Initialize the PastaConfigReaderFactory instance.

    This constructor sets up the logging, initializes the configuration file path, and prepares the file system
    watcher to monitor changes to the configuration file. It also reads the initial configuration and sets up a
    mutex for thread safety.
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.config_file_name = join(Path.home(), '.pastaELN_v3.json')
    self.config: dict[str, Any] = {}
    self.mutex: Lock = Lock()
    self.fs_watcher = QFileSystemWatcher()
    self.fs_watcher.addPath(self.config_file_name)
    if exists(self.config_file_name):
      self.fs_watcher.fileChanged.connect(self.config_file_changed)
    self.read_pasta_config()

  def read_pasta_config(self) -> None:
    """
    Read the configuration file and update the internal configuration.

    This method logs the action of reading the configuration file and attempts to load its contents into the internal configuration dictionary.
    If the configuration file does not exist, it raises a ConfigError to indicate an issue with the installation.

    Raises:
        ConfigError: If the configuration file does not exist.
    """
    self.logger.info('Reading config file: %s', self.config_file_name)
    with self.mutex:
      if not exists(self.config_file_name):
        raise ConfigError('Config file not found, Corrupt installation!')
      with open(self.config_file_name, 'r', encoding='utf-8') as confFile:
        self.config = load(confFile)

  @QtCore.Slot()                                              # type: ignore[arg-type]
  def config_file_changed(self, config_file_path: str) -> None:
    """
    Handle changes to the configuration file.

    This method is triggered when the configuration file changes. It reads the updated configuration and refreshes the file system watcher to ensure it continues to monitor the correct file path.

    Args:
        config_file_path (str): The path to the configuration file that has changed.
    """

    self.read_pasta_config()
    if exists(config_file_path):
      self.fs_watcher.removePath(config_file_path)
      self.fs_watcher.addPath(config_file_path)

  @property
  def config(self) -> dict[str, Any] | None:
    """
    Get the current configuration.

    This property retrieves the current configuration stored in the instance. It ensures thread safety by using a
    mutex and returns the configuration dictionary if it exists; otherwise, it returns None.

    Returns:
        dict[str, Any] | None: The current configuration dictionary or None if not set.
    """

    with self.mutex:
      return self._config if hasattr(self, '_config') else None

  @config.setter
  def config(self, value: dict[str, Any] | None) -> None:
    """
    Set the configuration.

    This property allows the configuration to be updated with a new value. It accepts a dictionary representing the configuration or None to clear the existing configuration.

    Args:
        value (dict[str, Any] | None): The new configuration value to set.
    """

    self._config = value

  @config.deleter
  def config(self) -> None:
    """
    Delete the configuration.

    This property allows for the removal of the current configuration. It clears the stored configuration value, effectively resetting it to None.
    """

    del self._config
