#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: base_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class BaseModel(object):

  def __init__(self, _id: str = None, _rev: str = None):
    super().__init__()
    self._id = _id
    self._rev = _rev

  def __iter__(self):
    for key in self.__dict__:
      if key in ['_id', '_rev']:
        yield key, getattr(self, key)
      else:
        yield key[1:], getattr(self, key)
