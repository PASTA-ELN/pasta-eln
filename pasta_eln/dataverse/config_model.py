#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any

from pasta_eln.dataverse.base_model import BaseModel
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class ConfigModel(BaseModel):
  """
  Represents a configuration model object.

  This class inherits from the BaseModel class and provides additional properties and methods for managing configuration-related information.

  Args:
      _id (str): The ID of the configuration. Defaults to None.
      _rev (str): The revision of the configuration. Defaults to None.
      project_upload_items (dict[str, Any]): A dictionary containing upload items of the PASTA project to be uploaded to Dataverse. Defaults to None.
      parallel_uploads_count (int): The number of parallel uploads configured. Defaults to None.
      dataverse_login_info (dict[str, Any]): A dictionary containing Dataverse login information. Defaults to None.
      metadata (dict[str, Any]): A dictionary containing metadata for the dataset in Dataverse. Defaults to None.

  Raises:
      IncorrectParameterError: If any of the arguments have an invalid type.

  Attributes:
      project_upload_items (dict[str, Any]): The upload items of the PASTA project.
      parallel_uploads_count (int): The number of parallel uploads configured.
      dataverse_login_info (dict[str, Any]): The Dataverse login information.
      metadata (dict[str, Any]): The metadata for the dataset in Dataverse.

  """

  def __init__(self,
               _id: str = "",
               _rev: str = "",
               project_upload_items: dict[str, Any] = {},
               parallel_uploads_count: int = 0,
               dataverse_login_info: dict[str, Any] = {},
               metadata: dict[str, Any] = {}):
    """
    Initializes a config model object.

    Args:
        _id (str): The ID of the object. Defaults to an empty string.
        _rev (str): The revision of the object. Defaults to an empty string.
        project_upload_items (dict[str, Any]): A dictionary containing upload items of the project. Defaults to an empty dictionary.
        parallel_uploads_count (int): The number of parallel uploads configured. Defaults to 0.
        dataverse_login_info (dict[str, Any]): A dictionary containing Dataverse login information. Defaults to an empty dictionary.
        metadata (dict[str, Any]): A dictionary containing metadata for the dataset in Dataverse. Defaults to an empty dictionary.

    Raises:
        IncorrectParameterError: If any of the parameters have an invalid type.

    """
    super().__init__(_id, _rev)
    if isinstance(project_upload_items, dict | None):
      self._project_upload_items: dict[str, Any] = project_upload_items
    else:
      raise IncorrectParameterError(f"Expected dictionary for upload_items but got {type(project_upload_items)}")
    if isinstance(parallel_uploads_count, int | None):
      self._parallel_uploads_count: int = parallel_uploads_count
    else:
      raise IncorrectParameterError(
        f"Expected integer for parallel_uploads_count but got {type(parallel_uploads_count)}")
    if isinstance(dataverse_login_info, dict | None):
      self._dataverse_login_info: dict[str, Any] = dataverse_login_info
    else:
      raise IncorrectParameterError(
        f"Expected dictionary for dataverse_login_info but got {type(dataverse_login_info)}")
    if isinstance(metadata, dict | None):
      self._metadata: dict[str, Any] = metadata
    else:
      raise IncorrectParameterError(f"Expected dictionary for metadata but got {type(metadata)}")

  @property
  def project_upload_items(self) -> dict[str, Any]:
    """
    Returns the upload items of the project.

    Returns:
        dict[str, Any]: A dictionary containing the upload items of the project.

    """
    return self._project_upload_items

  @project_upload_items.setter
  def project_upload_items(self, value: dict[str, Any]) -> None:
    """
    Sets the upload items of the project.

    Args:
        value (dict[str, Any]): The upload items to set. Defaults to None.

    Raises:
        IncorrectParameterError: If the value is not of type dict or None.

    Returns:
        None

    """
    if isinstance(value, dict):
      self._project_upload_items = value
    else:
      raise IncorrectParameterError(f"Expected dictionary for upload_items but got {type(value)}")

  @project_upload_items.deleter
  def project_upload_items(self) -> None:
    """
    Deletes the upload items of the project.

    """
    del self._project_upload_items

  @property
  def parallel_uploads_count(self) -> int:
    """
    Returns the number of parallel uploads.

    Returns:
        int: The number of parallel uploads.

    """
    return self._parallel_uploads_count

  @parallel_uploads_count.setter
  def parallel_uploads_count(self, value: int) -> None:
    """
    Sets the number of parallel uploads.

    Args:
        value (int): The number of parallel uploads to set.

    Raises:
        IncorrectParameterError: If the value is not of type int.

    Returns:
        None

    """
    if isinstance(value, int):
      self._parallel_uploads_count = value
    else:
      raise IncorrectParameterError(f"Expected integer for parallel_uploads_count but got {type(value)}")

  @parallel_uploads_count.deleter
  def parallel_uploads_count(self) -> None:
    """
    Deletes the number of parallel uploads.

    """
    del self._parallel_uploads_count

  @property
  def dataverse_login_info(self) -> dict[str, Any]:
    """
    Returns the dataverse login information.

    Returns:
        dict[str, Any]: The dataverse login information.

    """
    return self._dataverse_login_info

  @dataverse_login_info.setter
  def dataverse_login_info(self, value: dict[str, Any]) -> None:
    """
    Sets the dataverse login information.

    Args:
        value (dict[str, Any]): The dataverse login information to set.

    Raises:
        IncorrectParameterError: If the value is not of type dict.

    Returns:
        None

    """
    if isinstance(value, dict):
      self._dataverse_login_info = value
    else:
      raise IncorrectParameterError(f"Expected dictionary for dataverse_login_info but got {type(value)}")

  @dataverse_login_info.deleter
  def dataverse_login_info(self) -> None:
    """
    Deletes the dataverse login information.

    """
    del self._dataverse_login_info

  @property
  def metadata(self) -> dict[str, Any]:
    """
    Returns the metadata.

    Returns:
        dict[str, Any]: The metadata.

    """
    return self._metadata

  @metadata.setter
  def metadata(self, value: dict[str, Any]) -> None:
    """
    Sets the metadata.

    Args:
        value (dict[str, Any]): The metadata to set.

    Raises:
        IncorrectParameterError: If the value is not of type dict.

    Returns:
        None

    """
    if isinstance(value, dict):
      self._metadata = value
    else:
      raise IncorrectParameterError(f"Expected dictionary for metadata but got {type(value)}")

  @metadata.deleter
  def metadata(self) -> None:
    """
    Deletes the metadata.

    """
    del self._metadata
