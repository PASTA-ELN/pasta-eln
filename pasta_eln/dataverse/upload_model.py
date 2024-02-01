#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pasta_eln.dataverse.base_model import BaseModel
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class UploadModel(BaseModel):
  """
  Represents an upload model object.

  This class inherits from the BaseModel class and provides additional properties and methods for managing upload-related information.

  Args:
      _id (str | None): The ID of the object. Defaults to an empty string.
      _rev (str | None): The revision of the object. Defaults to an empty string.
      data_type (str | None): The data type of the upload. Defaults to an empty string.
      project_name (str | None): The name of the project. Defaults to an empty string.
      status (str | None): The status of the upload. Defaults to an empty string.
      finished_date_time (str | None): The date and time when the upload finished. Defaults to an empty string.
      log (str): The log associated with the upload. Defaults to an empty string.
      dataverse_url (str | None): The URL of the Dataverse. Defaults to an empty string.

  Raises:
      IncorrectParameterError: If any of the parameters are not of type str or None.

  Attributes:
      data_type (str | None): The data type of the upload.
      project_name (str | None): The name of the project.
      status (str | None): The status of the upload.
      finished_date_time (str | None): The date and time when the upload finished.
      log (str): The log associated with the upload.
      dataverse_url (str | None): The URL of the Dataverse.

  """

  def __init__(self,
               _id: str | None = None,
               _rev: str | None = None,
               data_type: str | None = None,
               project_name: str | None = None,
               status: str | None = None,
               finished_date_time: str | None = None,
               log: str = "",
               dataverse_url: str | None = None):
    """
    Initializes an upload model object.

    Args:
        _id (str | None): The ID of the object. Defaults to None.
        _rev (str | None): The revision of the object. Defaults to None.
        data_type (str | None): The data type of the upload. Defaults to None.
        project_name (str | None): The name of the project. Defaults to None.
        status (str | None): The status of the upload. Defaults to None.
        finished_date_time (str | None): The date and time when the upload finished. Defaults to None.
        log (str): The log associated with the upload. Defaults to empty string.
        dataverse_url (str | None): The URL of the Dataverse. Defaults to None.

    Raises:
        IncorrectParameterError: If any of the parameters are not of type str or None.

    """

    super().__init__(_id, _rev)
    if isinstance(data_type, str | None):
      self._data_type: str | None = 'dataverse_upload' if data_type is None else data_type
    else:
      raise IncorrectParameterError(f"Expected string type for data_type but got {type(data_type)}")
    if isinstance(project_name, str | None):
      self._project_name: str | None = project_name
    else:
      raise IncorrectParameterError(f"Expected string type for project_name but got {type(project_name)}")
    if isinstance(status, str | None):
      self._status: str | None = status
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(status)}")
    if isinstance(finished_date_time, str | None):
      self._finished_date_time: str | None = finished_date_time
    else:
      raise IncorrectParameterError(f"Expected string type for finished_date_time but got {type(finished_date_time)}")
    if isinstance(log, str):
      self._log: str = log
    else:
      raise IncorrectParameterError(f"Expected string type for log but got {type(log)}")
    if isinstance(dataverse_url, str | None):
      self._dataverse_url: str | None = dataverse_url
    else:
      raise IncorrectParameterError(f"Expected string type for dataverse_url but got {type(dataverse_url)}")

  @property
  def data_type(self) -> str | None:
    """
    Returns the data type of the upload.

    Returns:
        str | None: The data type of the upload.

    """
    return self._data_type

  @data_type.setter
  def data_type(self, value: str | None) -> None:
    """
    Sets the data type of the upload.

    Args:
        value (str | None): The data type value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str | None):
      self._data_type = value
    else:
      raise IncorrectParameterError(f"Expected string type for data_type but got {type(value)}")

  @data_type.deleter
  def data_type(self) -> None:
    """
    Deletes the data type of the upload.

    Returns:
        None

    """
    del self._data_type

  @property
  def project_name(self) -> str | None:
    """
    Returns the project name associated with the upload.

    Returns:
        str | None: The project name.

    """
    return self._project_name

  @project_name.setter
  def project_name(self, value: str | None) -> None:
    """
    Sets the project name associated with the upload.

    Args:
        value (str | None): The project name value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str | None):
      self._project_name = value
    else:
      raise IncorrectParameterError(f"Expected string type for project_name but got {type(value)}")

  @project_name.deleter
  def project_name(self) -> None:
    del self._project_name

  @property
  def status(self) -> str | None:
    """
    Returns the status of the upload.

    Returns:
        str | None: The status of the upload.

    """
    return self._status

  @status.setter
  def status(self, value: str | None) -> None:
    """
    Sets the status of the upload.

    Args:
        value (str | None): The status value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str | None):
      self._status = value
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(value)}")

  @status.deleter
  def status(self) -> None:
    """
    Deletes the status of the upload.

    Returns:
        None

    """
    del self._status

  @property
  def finished_date_time(self) -> str | None:
    """
    Returns the finished date and time of the upload.

    Returns:
        str | None: The finished date and time of the upload.

    """
    return self._finished_date_time

  @finished_date_time.setter
  def finished_date_time(self, value: str | None) -> None:
    """
    Sets the finished date and time of the upload.

    Args:
        value (str | None): The finished date and time value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str | None):
      self._finished_date_time = value
    else:
      raise IncorrectParameterError(f"Expected string type for finished_date_time but got {type(value)}")

  @finished_date_time.deleter
  def finished_date_time(self) -> None:
    """
    Deletes the finished date and time of the upload.

    Returns:
        None

    """
    del self._finished_date_time

  @property
  def log(self) -> str:
    """
    Returns the log of the upload.

    Returns:
        str: The log of the upload.

    """
    return self._log

  @log.setter
  def log(self, value: str) -> None:
    """
    Appends a log message to the existing log associated with the upload.

    Args:
        value (str): The log message to be appended.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str):
      self._log += f"{value}\n"
    else:
      raise IncorrectParameterError(f"Expected string type for log but got {type(value)}")

  @log.deleter
  def log(self) -> None:
    """
    Deletes the log of the upload.

    Returns:
        None

    """
    del self._log

  @property
  def dataverse_url(self) -> str | None:
    """
    Returns the URL of the Dataverse.

    Returns:
        str | None: The URL of the Dataverse.

    """
    return self._dataverse_url

  @dataverse_url.setter
  def dataverse_url(self, value: str | None) -> None:
    """
    Sets the URL of the Dataverse.

    Args:
        value (str | None): The URL value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str | None):
      self._dataverse_url = value
    else:
      raise IncorrectParameterError(f"Expected string type for dataverse_url but got {type(value)}")

  @dataverse_url.deleter
  def dataverse_url(self) -> None:
    """
    Deletes the URL of the Dataverse.

    Returns:
        None

    """
    del self._dataverse_url
