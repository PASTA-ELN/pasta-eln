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

  def __init__(self,
               _id: str = None,
               _rev: str = None,
               project_upload_items: dict[str, Any] = None,
               parallel_uploads_count: int = None,
               dataverse_login_info: dict[str, Any] = None,
               metadata: dict[str, Any] = None):
    """
    Initializes a ConfigModel object.

    Args:
        _id: The ID of the config.
        _rev: The revision of the config.
        project_upload_items: A dictionary containing upload items of the PASTA project to be uploaded to dataverse.
        parallel_uploads_count: The number of parallel uploads configured.
        dataverse_login_info: A dictionary containing dataverse login information.
        metadata: A dictionary containing metadata for the dataset in dataverse.

    Raises:
        IncorrectParameterError: If any of the arguments have an invalid type.

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
  def project_upload_items(self):
    """
    Gets the upload items.

    Returns:
        The upload items.

    """
    return self._project_upload_items

  @project_upload_items.setter
  def project_upload_items(self, value: dict[str, Any]):
    """
    Sets the upload items.

    Args:
        value: The upload items to set.

    """
    self._project_upload_items = value

  @project_upload_items.deleter
  def project_upload_items(self):
    """
    Deletes the upload items.

    """
    del self._project_upload_items

  @property
  def parallel_uploads_count(self):
    """
    Gets the number of parallel uploads.

    Returns:
        The number of parallel uploads.

    """
    return self._parallel_uploads_count

  @parallel_uploads_count.setter
  def parallel_uploads_count(self, value: int):
    """
    Sets the number of parallel uploads.

    Args:
        value: The number of parallel uploads to set.

    """
    self._parallel_uploads_count = value

  @parallel_uploads_count.deleter
  def parallel_uploads_count(self):
    """
    Deletes the number of parallel uploads.

    """
    del self._parallel_uploads_count

  @property
  def dataverse_login_info(self):
    """
    Gets the dataverse login information.

    Returns:
        The dataverse login information.

    """
    return self._dataverse_login_info

  @dataverse_login_info.setter
  def dataverse_login_info(self, value: dict[str, Any]):
    """
    Sets the dataverse login information.

    Args:
        value: The dataverse login information to set.

    """
    self._dataverse_login_info = value

  @dataverse_login_info.deleter
  def dataverse_login_info(self):
    """
    Deletes the dataverse login information.

    """
    del self._dataverse_login_info

  @property
  def metadata(self):
    """
    Gets the metadata.

    Returns:
        The metadata.

    """
    return self._metadata

  @metadata.setter
  def metadata(self, value: dict[str, Any]):
    """
    Sets the metadata.

    Args:
        value: The metadata to set.

    """
    self._metadata = value

  @metadata.deleter
  def metadata(self):
    """
    Deletes the metadata.

    """
    del self._metadata
