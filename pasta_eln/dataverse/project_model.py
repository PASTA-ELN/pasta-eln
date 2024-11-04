""" Represents a project model object. """
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
      _id (str | None): The ID of the object. Defaults to None.
      _rev (str | None): The revision of the object. Defaults to None.
      name (str | None): The name of the project. Defaults to None.
      comment (str | None): The comment associated with the project. Defaults to None.
      user (str | None): The user associated with the project. Defaults to None.
      date (str | None): The date of the project. Defaults to None.
      status (str | None): The status of the project. Defaults to None.
      objective (str | None): The objective of the project. Defaults to None.

  Raises:
      IncorrectParameterError: If any of the parameters are not of type str or None.

  Attributes:
      id (str | None): The ID of the object.
      rev (str | None): The revision of the object.
      name (str | None): The name of the project.
      comment (str | None): The comment associated with the project.
      user (str | None): The user associated with the project.
      date (str | None): The date of the project.
      status (str | None): The status of the project.
      objective (str | None): The objective of the project.

  """

  def __init__(self,
               _id: str | None = None,
               name: str | None = None,
               comment: str | None = None,
               user: str | None = None,
               date_created: str | None = None,
               date_modified: str | None = None,
               status: str | None = None,
               objective: str | None = None) -> None:
    """
    Initializes a project model object.

    Args:
        _id (str | None): The ID of the object. Defaults to None.
        _rev (str | None): The revision of the object. Defaults to None.
        name (str | None): The name of the project. Defaults to None.
        comment (str | None): The comment associated with the project. Defaults to None.
        user (str | None): The user associated with the project. Defaults to None.
        date (str | None): The date of the project. Defaults to None.
        status (str | None): The status of the project. Defaults to None.
        objective (str | None): The objective of the project. Defaults to None.

    Raises:
        IncorrectParameterError: If any of the parameters are not of type str or None.

    """
    super().__init__(_id)
    if isinstance(name, str | None):
      self._name: str | None = name
    else:
      raise IncorrectParameterError(f"Expected string type for name but got {type(name)}")
    if isinstance(comment, str | None):
      self._comment: str | None = comment
    else:
      raise IncorrectParameterError(f"Expected string type for comment but got {type(comment)}")
    if isinstance(user, str | None):
      self._user: str | None = user
    else:
      raise IncorrectParameterError(f"Expected string type for user but got {type(user)}")
    if isinstance(date_created, str | None):
      self._date_created: str | None = date_created
    else:
      raise IncorrectParameterError(f"Expected string type for date_created but got {type(date_created)}")
    if isinstance(date_modified, str | None):
      self._date_modified: str | None = date_modified
    else:
      raise IncorrectParameterError(f"Expected string type for date_modified but got {type(date_modified)}")
    if isinstance(status, str | None):
      self._status: str | None = status
    else:
      raise IncorrectParameterError(f"Expected string type for status but got {type(status)}")
    if isinstance(objective, str | None):
      self._objective: str | None = objective
    else:
      raise IncorrectParameterError(f"Expected string type for objective but got {type(objective)}")

  @property
  def name(self) -> str | None:
    """
    Returns the name of the project.

    Returns:
        str | None: The name of the project.

    """
    return self._name

  @name.setter
  def name(self, value: str | None) -> None:
    """
    Sets the name of the project.

    Args:
        value (str | None): The name value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._name = value
    else:
      raise IncorrectParameterError(f"Expected string type for name but got {type(value)}")

  @name.deleter
  def name(self) -> None:
    """
    Deletes the name of the project.

    """
    del self._name

  @property
  def comment(self) -> str | None:
    """
    Returns the comment associated with the project.

    Returns:
        str | None: The comment associated with the project.

    """
    return self._comment

  @comment.setter
  def comment(self, value: str | None) -> None:
    """
    Sets the comment associated with the project.

    Args:
        value (str | None): The comment value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._comment = value
    else:
      raise IncorrectParameterError(f"Expected string type for comment but got {type(value)}")

  @comment.deleter
  def comment(self) -> None:
    """
    Deletes the comment associated with the project.

    """
    del self._comment

  @property
  def user(self) -> str | None:
    """
    Returns the user associated with the project.

    Returns:
        str | None: The user associated with the project.

    """
    return self._user

  @user.setter
  def user(self, value: str | None) -> None:
    """
    Sets the user associated with the project.

    Args:
        value (str | None): The user value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._user = value
    else:
      raise IncorrectParameterError(f"Expected string type for user but got {type(value)}")

  @user.deleter
  def user(self) -> None:
    """
    Deletes the user associated with the project.

    """
    del self._user

  @property
  def date_created(self) -> str | None:
    """
    Returns the date_created of the project.

    Returns:
        str | None: The date_created for the project.

    """
    return self._date_created

  @date_created.setter
  def date_created(self, value: str | None) -> None:
    """
    Sets the date_created for the project.

    Args:
        value (str | None): The date_created value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._date_created = value
    else:
      raise IncorrectParameterError(f"Expected string type for date_created but got {type(value)}")

  @date_created.deleter
  def date_created(self) -> None:
    """
    Deletes the date_created for the project.

    """
    del self._date_created

  @property
  def date_modified(self) -> str | None:
    """
    Returns the date_modified for the project.

    Returns:
        str | None: The date_modified for the project.

    """
    return self._date_modified

  @date_modified.setter
  def date_modified(self, value: str | None) -> None:
    """
    Sets the date_modified for the project.

    Args:
        value (str | None): The date_modified value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._date_modified = value
    else:
      raise IncorrectParameterError(f"Expected string type for date_modified but got {type(value)}")

  @date_modified.deleter
  def date_modified(self) -> None:
    """
    Deletes the date_modified for the project.

    """
    del self._date_modified

  @property
  def status(self) -> str | None:
    """
    Returns the status of the project.

    Returns:
        str | None: The status of the project.

    """
    return self._status

  @status.setter
  def status(self, value: str | None) -> None:
    """
    Sets the status of the project.

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
    Deletes the status of the project.

    """
    del self._status

  @property
  def objective(self) -> str | None:
    """
    Returns the objective of the project.

    Returns:
        str | None: The objective of the project.

    """
    return self._objective

  @objective.setter
  def objective(self, value: str | None) -> None:
    """
    Sets the objective of the project.

    Args:
        value (str | None): The objective value to be set.

    Raises:
        IncorrectParameterError: If the value is not of type str.

    """
    if isinstance(value, str | None):
      self._objective = value
    else:
      raise IncorrectParameterError(f"Expected string type for objective but got {type(value)}")

  @objective.deleter
  def objective(self) -> None:
    """
    Deletes the objective of the project.

    """
    del self._objective
