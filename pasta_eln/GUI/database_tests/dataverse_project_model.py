#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_project_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class DataverseProjectModel(object):

  def __init__(self,
               name: str,
               comment: str,
               user: str,
               date: str,
               status: str = None,
               objective: str = None,
               _id: str = None,
               _rev: str = None):
    super().__init__()
    self._id = _id
    self._rev = _rev
    self.name = name
    self.comment = comment
    self.user = user
    self.date = date
    self.status = status
    self.objective = objective
