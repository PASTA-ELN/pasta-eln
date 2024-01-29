#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pasta_eln.GUI.database_tests.base_model import BaseModel
from pasta_eln.GUI.database_tests.incorrect_parameter_error import IncorrectParameterError


class UploadModel(BaseModel):

  def __init__(self,
               _id: str = None,
               _rev: str = None,
               _data_type: str = None,
               _project_name: str = None,
               _status: str = None,
               _finished_date_time: str = None,
               _log: str = "",
               _dataverse_url: str = None):
    super().__init__(_id, _rev)
    if isinstance(_data_type, str | None):
      self.data_type: str = 'dataverse_upload' if _data_type is None else _data_type
    else:
      raise IncorrectParameterError(f"Expected string type for data_type but got {type(_data_type)}")
    if isinstance(_project_name, str | None):
      self._project_name: str = _project_name
    else:
      raise IncorrectParameterError(f"Expected string type for project_name but got {type(_project_name)}")
    if isinstance(_status, str | None):
      self._status: str = _status
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(_status)}")
    if isinstance(_finished_date_time, str | None):
      self._finished_date_time: str = _finished_date_time
    else:
      raise IncorrectParameterError(f"Expected string type for finished_date_time but got {type(_finished_date_time)}")
    if isinstance(_log, str | None):
      self._log: str = _log
    else:
      raise IncorrectParameterError(f"Expected string type for log but got {type(_log)}")
    if isinstance(_dataverse_url, str | None):
      self._dataverse_url: str = _dataverse_url
    else:
      raise IncorrectParameterError(f"Expected string type for dataverse_url but got {type(_dataverse_url)}")

  @property
  def id(self):
    return self._id

  @id.setter
  def id(self, value):
    self._id = value

  @id.deleter
  def id(self):
    del self._id

  @property
  def rev(self):
    return self._rev

  @rev.setter
  def rev(self, value):
    self._rev = value

  @rev.deleter
  def rev(self):
    del self._rev

  @property
  def data_type(self):
    return self._data_type

  @data_type.setter
  def data_type(self, value):
    self._data_type = value

  @data_type.deleter
  def data_type(self):
    del self._data_type

  @property
  def project_name(self):
    return self._project_name

  @project_name.setter
  def project_name(self, value):
    self._project_name = value

  @project_name.deleter
  def project_name(self):
    del self._project_name

  @property
  def status(self):
    return self._status

  @status.setter
  def status(self, value):
    self._status = value

  @status.deleter
  def status(self):
    del self._status

  @property
  def finished_date_time(self):
    return self._finished_date_time

  @finished_date_time.setter
  def finished_date_time(self, value):
    self._finished_date_time = value

  @finished_date_time.deleter
  def finished_date_time(self):
    del self._finished_date_time

  @property
  def log(self):
    return self._log

  @log.setter
  def log(self, value):
    self._log += f"{value}\n"

  @log.deleter
  def log(self):
    del self._log

  @property
  def dataverse_url(self):
    return self._dataverse_url

  @dataverse_url.setter
  def dataverse_url(self, value):
    self._dataverse_url = value

  @dataverse_url.deleter
  def dataverse_url(self):
    del self._dataverse_url
