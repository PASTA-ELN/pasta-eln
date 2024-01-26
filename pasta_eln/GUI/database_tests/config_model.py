#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any

from pasta_eln.GUI.database_tests.base_model import BaseModel
from pasta_eln.GUI.database_tests.incorrect_parameter_error import IncorrectParameterError


class ConfigModel(BaseModel):

  def __init__(self,
               _id: str = None,
               _rev: str = None,
               _upload_items: dict[str, Any] = None,
               _parallel_uploads_count: int = None,
               _dataverse_login_info: dict[str, Any] = None,
               _metadata: dict[str, Any] = None):
    super().__init__(_id, _rev)
    if isinstance(_upload_items, dict | None):
      self._upload_items: dict[str, Any] = _upload_items
    else:
      raise IncorrectParameterError(f"Expected dictionary for upload_items but got {type(_upload_items)}")
    if isinstance(_parallel_uploads_count, int | None):
      self._parallel_uploads_count: int = _parallel_uploads_count
    else:
      raise IncorrectParameterError(
        f"Expected integer for parallel_uploads_count but got {type(_parallel_uploads_count)}")
    if isinstance(_dataverse_login_info, dict | None):
      self._dataverse_login_info: dict[str, Any] = _dataverse_login_info
    else:
      raise IncorrectParameterError(
        f"Expected dictionary for dataverse_login_info but got {type(_dataverse_login_info)}")
    if isinstance(_metadata, dict | None):
      self._metadata: dict[str, Any] = _metadata
    else:
      raise IncorrectParameterError(f"Expected dictionary for metadata but got {type(_metadata)}")

  @property
  def upload_items(self):
    return self._upload_items

  @upload_items.setter
  def upload_items(self, value: dict[str, Any]):
    self._upload_items = value

  @upload_items.deleter
  def upload_items(self):
    del self._upload_items

  @property
  def parallel_uploads_count(self):
    return self._parallel_uploads_count

  @parallel_uploads_count.setter
  def parallel_uploads_count(self, value: int):
    self._parallel_uploads_count = value

  @parallel_uploads_count.deleter
  def parallel_uploads_count(self):
    del self._parallel_uploads_count

  @property
  def dataverse_login_info(self):
    return self._dataverse_login_info

  @dataverse_login_info.setter
  def dataverse_login_info(self, value: dict[str, Any]):
    self._dataverse_login_info = value

  @dataverse_login_info.deleter
  def dataverse_login_info(self):
    del self._dataverse_login_info

  @property
  def metadata(self):
    return self._metadata

  @metadata.setter
  def metadata(self, value: dict[str, Any]):
    self._metadata = value

  @metadata.deleter
  def metadata(self):
    del self._metadata
