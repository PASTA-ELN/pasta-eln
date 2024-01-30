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
  def __init__(self,
               _id: str = None,
               _rev: str = None,
               name: str = None,
               comment: str = None,
               user: str = None,
               date: str = None,
               status: str = None,
               objective: str = None):
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
  def name(self):
    return self._name

  @name.setter
  def name(self, value):
    self._name = value

  @name.deleter
  def name(self):
    del self._name

  @property
  def comment(self):
    return self._comment

  @comment.setter
  def comment(self, value):
    self._comment = value

  @comment.deleter
  def comment(self):
    del self._comment

  @property
  def user(self):
    return self._user

  @user.setter
  def user(self, value):
    self._user = value

  @user.deleter
  def user(self):
    del self._user

  @property
  def date(self):
    return self._date

  @date.setter
  def date(self, value):
    self._date = value

  @date.deleter
  def date(self):
    del self._date

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
  def objective(self):
    return self._objective

  @objective.setter
  def objective(self, value):
    self._objective = value

  @objective.deleter
  def objective(self):
    del self._objective
