#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: project_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pasta_eln.dataverse.base_model import BaseModel
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class ProjectModel(BaseModel):
  """
  Represents a project model object.

  This class inherits from the BaseModel class and provides additional properties and methods for managing project-related information.

  Args:
      _id (str): The ID of the object. Defaults to None.
      _rev (str): The revision of the object. Defaults to None.
      name (str): The name of the project. Defaults to None.
      comment (str): The comment associated with the project. Defaults to None.
      user (str): The user associated with the project. Defaults to None.
      date (str): The date of the project. Defaults to None.
      status (str): The status of the project. Defaults to None.
      objective (str): The objective of the project. Defaults to None.

  Raises:
      IncorrectParameterError: If any of the parameters are not of type str or None.

  Attributes:
      id (str): The ID of the object.
      rev (str): The revision of the object.
      name (str): The name of the project.
      comment (str): The comment associated with the project.
      user (str): The user associated with the project.
      date (str): The date of the project.
      status (str): The status of the project.
      objective (str): The objective of the project.

  """

  def __init__(self,
               _id: str = "",
               _rev: str = "",
               name: str = "",
               comment: str = "",
               user: str = "",
               date: str = "",
               status: str = "",
               objective: str = ""):
    """
    Initializes a project model object.

    Args:
        _id (str): The ID of the object. Defaults to None.
        _rev (str): The revision of the object. Defaults to None.
        name (str): The name of the project. Defaults to None.
        comment (str): The comment associated with the project. Defaults to None.
        user (str): The user associated with the project. Defaults to None.
        date (str): The date of the project. Defaults to None.
        status (str): The status of the project. Defaults to None.
        objective (str): The objective of the project. Defaults to None.

    Raises:
        IncorrectParameterError: If any of the parameters are not of type str or None.

    """
    super().__init__(_id, _rev)
    if isinstance(name, str | None):
      self._name: str = name
    else:
      raise IncorrectParameterError(f"Expected string type for name but got {type(name)}")
    if isinstance(comment, str | None):
      self._comment: str = comment
    else:
      raise IncorrectParameterError(f"Expected string type for comment but got {type(comment)}")
    if isinstance(user, str | None):
      self._user: str = user
    else:
      raise IncorrectParameterError(f"Expected string type for user but got {type(user)}")
    if isinstance(date, str | None):
      self._date: str = date
    else:
      raise IncorrectParameterError(f"Expected string type for date but got {type(date)}")
    if isinstance(status, str | None):
      self._status: str = status
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(status)}")
    if isinstance(objective, str | None):
      self._objective: str = objective
    else:
      raise IncorrectParameterError(f"Expected string type for objective but got {type(objective)}")

  @property
  def name(self) -> str:
    """
    Returns the name of the project.

    Returns:
        str: The name of the project.

    """
    return self._name

  @name.setter
  def name(self, value: str) -> None:
    """
    Sets the name of the project.

    Args:
        value (str): The name value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str):
      self._name = value
    else:
      raise IncorrectParameterError(f"Expected string type for name but got {type(value)}")

  @name.deleter
  def name(self) -> None:
    """
    Deletes the name of the project.

    Returns:
        None

    """
    del self._name

  @property
  def comment(self) -> str:
    """
    Returns the comment associated with the project.

    Returns:
        str: The comment associated with the project.

    """
    return self._comment

  @comment.setter
  def comment(self, value: str) -> None:
    """
    Sets the comment associated with the project.

    Args:
        value (str): The comment value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str):
      self._comment = value
    else:
      raise IncorrectParameterError(f"Expected string type for comment but got {type(value)}")

  @comment.deleter
  def comment(self) -> None:
    """
    Deletes the comment associated with the project.

    Returns:
        None

    """
    del self._comment

  @property
  def user(self) -> str:
    """
    Returns the user associated with the project.

    Returns:
        str: The user associated with the project.

    """
    return self._user

  @user.setter
  def user(self, value: str) -> None:
    """
    Sets the user associated with the project.

    Args:
        value (str): The user value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str):
      self._user = value
    else:
      raise IncorrectParameterError(f"Expected string type for user but got {type(value)}")

  @user.deleter
  def user(self) -> None:
    """
    Deletes the user associated with the project.

    Returns:
        None

    """
    del self._user

  @property
  def date(self) -> str:
    """
    Returns the date of the project.

    Returns:
        str: The date of the project.

    """
    return self._date

  @date.setter
  def date(self, value: str) -> None:
    """
    Sets the date of the project.

    Args:
        value (str): The date value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str):
      self._date = value
    else:
      raise IncorrectParameterError(f"Expected string type for date but got {type(value)}")

  @date.deleter
  def date(self) -> None:
    """
    Deletes the date of the project.

    Returns:
        None

    """
    del self._date

  @property
  def status(self) -> str:
    """
    Returns the status of the project.

    Returns:
        str: The status of the project.

    """
    return self._status

  @status.setter
  def status(self, value: str) -> None:
    """
    Sets the status of the project.

    Args:
        value (str): The status value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str):
      self._status = value
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(value)}")

  @status.deleter
  def status(self) -> None:
    """
    Deletes the status of the project.

    Returns:
        None

    """
    del self._status

  @property
  def objective(self) -> str:
    """
    Returns the objective of the project.

    Returns:
        str: The objective of the project.

    """
    return self._objective

  @objective.setter
  def objective(self, value: str) -> None:
    """
    Sets the objective of the project.

    Args:
        value (str): The objective value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    Returns:
        None

    """
    if isinstance(value, str):
      self._objective = value
    else:
      raise IncorrectParameterError(f"Expected string type for objective but got {type(value)}")

  @objective.deleter
  def objective(self) -> None:
    """
    Deletes the objective of the project.

    Returns:
        None

    """
    del self._objective
