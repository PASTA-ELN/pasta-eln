""" Represents an upload model object. """
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
      data_type (str | None): The data type of the upload. Defaults to an empty string.
      project_name (str | None): The name of the project. Defaults to an empty string.
      status (str | None): The status of the upload. Defaults to an empty string.
      finished_date_time (str | None): The date and time when the upload finished. Defaults to an empty string.
      log (str): The log associated with the upload. Defaults to an empty string.
      dataverse_url (str | None): The URL of the Dataverse. Defaults to an empty string.

  Raises:
      IncorrectParameterError: If any of the parameters are not of type str or None.

  Attributes:
      _data_type (str | None): The data type of the upload.
      _project_name (str | None): The name of the project.
      _project_doc_id (str | None): The document ID of the project.
      _status (str | None): The status of the upload.
      _created_date_time (str | None): The date and time when the upload created.
      _finished_date_time (str | None): The date and time when the upload finished.
      _log (str | None): The log associated with the upload.
      _dataverse_url (str | None): The URL of the Dataverse.

  """

  def __init__(self,
               _id: int | None = None,
               data_type: str | None = None,
               project_name: str | None = None,
               project_doc_id: str | None = None,
               status: str | None = None,
               created_date_time: str | None = None,
               finished_date_time: str | None = None,
               log: str | None = "",
               dataverse_url: str | None = None):
    """
    Initializes an upload model object.

    Args:
        _id (str | None): The ID of the object. Defaults to None.
        data_type (str | None): The data type of the upload. Defaults to None.
        project_name (str | None): The name of the project. Defaults to None.
        project_doc_id (str | None): The document ID of the project. Defaults to None.
        status (str | None): The status of the upload. Defaults to None.
        created_date_time (str | None): The date and time when the upload created. Defaults to None.
        finished_date_time (str | None): The date and time when the upload finished. Defaults to None.
        log (str | None): The log associated with the upload. Defaults to empty string.
        dataverse_url (str | None): The URL of the Dataverse. Defaults to None.

    Raises:
        IncorrectParameterError: If any of the parameters are not of type str or None.

    """

    super().__init__(_id)
    if isinstance(data_type, str | None):
      self._data_type: str | None = 'dataverse_upload' if data_type is None else data_type
    else:
      raise IncorrectParameterError(f"Expected string type for data_type but got {type(data_type)}")
    if isinstance(project_name, str | None):
      self._project_name: str | None = project_name
    else:
      raise IncorrectParameterError(f"Expected string type for project_name but got {type(project_name)}")
    if isinstance(project_doc_id, str | None):
      self._project_doc_id: str | None = project_doc_id
    else:
      raise IncorrectParameterError(f"Expected string type for project_doc_id but got {type(project_doc_id)}")
    if isinstance(status, str | None):
      self._status: str | None = status
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(status)}")
    if isinstance(finished_date_time, str | None):
      self._finished_date_time: str | None = finished_date_time
    else:
      raise IncorrectParameterError(f"Expected string type for finished_date_time but got {type(finished_date_time)}")
    if isinstance(created_date_time, str | None):
      self._created_date_time: str | None = created_date_time
    else:
      raise IncorrectParameterError(f"Expected string type for created_date_time but got {type(created_date_time)}")
    if isinstance(log, str | None):
      self._log: str | None = f"{log}\n" if log and not log.endswith('\n') else log
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

    """
    if isinstance(value, str | None):
      self._data_type = value
    else:
      raise IncorrectParameterError(f"Expected string type for data_type but got {type(value)}")

  @data_type.deleter
  def data_type(self) -> None:
    """
    Deletes the data type of the upload.

    """
    del self._data_type

  @property
  def project_doc_id(self) -> str | None:
    """
    Returns the project document ID associated with the upload.

    Returns:
        str | None: The project doc ID.

    """
    return self._project_doc_id

  @project_doc_id.setter
  def project_doc_id(self, value: str | None) -> None:
    """
    Sets the project document ID associated with the upload.

    Args:
        value (str | None): The project doc ID value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._project_doc_id = value
    else:
      raise IncorrectParameterError(f"Expected string type for project_doc_id but got {type(value)}")

  @project_doc_id.deleter
  def project_doc_id(self) -> None:
    """
    Deletes the project_doc_id attribute.

    Explanation:
        This method deletes the project_doc_id attribute.

    Args:
        self: The instance of the class.

    """
    del self._project_doc_id

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

    """
    if isinstance(value, str | None):
      self._project_name = value
    else:
      raise IncorrectParameterError(f"Expected string type for project_name but got {type(value)}")

  @project_name.deleter
  def project_name(self) -> None:
    """
    Deletes the project_name attribute.

    Explanation:
        This method deletes the project_name attribute.

    Args:
        self: The instance of the class.

    """
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

    """
    if isinstance(value, str | None):
      self._status = value
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(value)}")

  @status.deleter
  def status(self) -> None:
    """
    Deletes the status of the upload.

    """
    del self._status

  @property
  def created_date_time(self) -> str | None:
    """
    Returns the created date and time of the upload.

    Returns:
        str | None: The created date and time of the upload.

    """
    return self._created_date_time

  @created_date_time.setter
  def created_date_time(self, value: str | None) -> None:
    """
    Sets the created date and time of the upload.

    Args:
        value (str | None): The created date and time value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._created_date_time = value
    else:
      raise IncorrectParameterError(f"Expected string type for created_date_time but got {type(value)}")

  @created_date_time.deleter
  def created_date_time(self) -> None:
    """
    Deletes the created date and time of the upload.

    """
    del self._created_date_time

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

    """
    if isinstance(value, str | None):
      self._finished_date_time = value
    else:
      raise IncorrectParameterError(f"Expected string type for finished_date_time but got {type(value)}")

  @finished_date_time.deleter
  def finished_date_time(self) -> None:
    """
    Deletes the finished date and time of the upload.

    """
    del self._finished_date_time

  @property
  def log(self) -> str | None:
    """
    Returns the log of the upload.

    Returns:
        str: The log of the upload.

    """
    return self._log

  @log.setter
  def log(self, value: str | None) -> None:
    """
    Appends a log message to the existing log associated with the upload.

    Args:
        value (str | None): The log message to be appended.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if not isinstance(value, str | None):
      raise IncorrectParameterError(f"Expected string type for log but got {type(value)}")
    if value != "" and self._log is not None:
      self._log += value if isinstance(value, str) and value.endswith('\n') else f"{value}\n"

  @log.deleter
  def log(self) -> None:
    """
    Deletes the log of the upload.

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

    """
    if isinstance(value, str | None):
      self._dataverse_url = value
    else:
      raise IncorrectParameterError(f"Expected string type for dataverse_url but got {type(value)}")

  @dataverse_url.deleter
  def dataverse_url(self) -> None:
    """
    Deletes the URL of the Dataverse.

    """
    del self._dataverse_url
