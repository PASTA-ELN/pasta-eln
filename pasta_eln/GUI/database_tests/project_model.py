#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: project_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pasta_eln.GUI.database_tests.base_model import BaseModel


class ProjectModel(BaseModel):
  def __init__(self,
               _id: str = None,
               _rev: str = None,
               _name: str = None,
               _comment: str = None,
               _user: str = None,
               _date: str = None,
               _status: str = None,
               _objective: str = None):
    super().__init__(_id, _rev)
    self._name = _name
    self._comment = _comment
    self._user = _user
    self._date = _date
    self._status = _status
    self._objective = _objective

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
