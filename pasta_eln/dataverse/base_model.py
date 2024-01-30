#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: base_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class BaseModel(object):

  def __init__(self, _id: str = None, _rev: str = None):
    super().__init__()
    if isinstance(_id, str | None):
      self._id: str = _id
    else:
      raise IncorrectParameterError(f"Expected string type for id but got {type(_id)}")
    if isinstance(_rev, str | None):
      self._rev: str = _rev
    else:
      raise IncorrectParameterError(f"Expected string type for rev but got {type(_rev)}")

  def __iter__(self):
    for key in self.__dict__:
      if key in ['_id', '_rev']:
        yield key, getattr(self, key)
      else:
        yield key[1:], getattr(self, key)

  @property
  def id(self):
    return self._id

  @id.setter
  def id(self, value: str):
    self._id = value

  @id.deleter
  def id(self):
    del self._id

  @property
  def rev(self):
    return self._rev

  @rev.setter
  def rev(self, value: str):
    self._rev = value

  @rev.deleter
  def rev(self):
    del self._rev
