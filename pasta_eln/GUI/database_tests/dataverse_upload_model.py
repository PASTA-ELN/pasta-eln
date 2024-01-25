#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class DataverseUploadModel(object):

  def __init__(self,
               project_name: str = None,
               upload_status: str = None,
               upload_finished_time: str = None,
               upload_log: str = None,
               dataverse_url: str = None,
               _id: str = None,
               _rev: str = None,
               data_type: str = None):
    super().__init__()
    self._id = _id
    self._rev = _rev
    self.data_type = 'dataverse_upload' if data_type is None else data_type
    self.project_name = project_name
    self.upload_status = upload_status
    self.upload_finished_time = upload_finished_time
    self.upload_log = upload_log
    self.dataverse_url = dataverse_url

  def append_log(self, value):
    self.upload_log += value

  @property
  def id(self):
    return self._id
