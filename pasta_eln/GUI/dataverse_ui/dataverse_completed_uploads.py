#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_completed_uploads.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from datetime import datetime
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QFrame

from pasta_eln.GUI.database_tests.dataverse_db_api import DataverseDBAPI
from pasta_eln.GUI.database_tests.dataverse_upload_model import DataverseUploadModel
from pasta_eln.GUI.dataverse_ui.dataverse_completed_upload_task import Ui_CompletedUploadTaskFrame
from pasta_eln.GUI.dataverse_ui.dataverse_completed_uploads_base import Ui_DataverseCompletedUploadsForm


class DataverseCompletedUploads(Ui_DataverseCompletedUploadsForm):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the create type dialog
    """
    return super(DataverseCompletedUploads, cls).__new__(cls)

  def __init__(self):
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.db_api = DataverseDBAPI()
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)

  def load_ui(self):
    for upload in self.db_api.get_all_upload_models():
      widget = self.get_completed_upload_task_widget(upload)
      self.completedUploadsVerticalLayout.addWidget(widget)

  def get_completed_upload_task_widget(self, upload: DataverseUploadModel)->QFrame:
    completedTaskFrame = QtWidgets.QFrame()
    completedTaskUi = Ui_CompletedUploadTaskFrame()
    completedTaskUi.setupUi(completedTaskFrame)
    completedTaskUi.projectNameLabel.setText(upload.project_name)
    completedTaskUi.dataverseUrlLabel.setText(upload.dataverse_url)
    completedTaskUi.finishedDateTimeLabel.setText(datetime.fromisoformat(upload.upload_finished_time).strftime("%Y-%m-%d %H:%M:%S") if upload.upload_finished_time else "")
    completedTaskUi.statusLabel.setText(upload.upload_status)
    return completedTaskFrame


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = DataverseCompletedUploads()
  ui.instance.show()
  sys.exit(app.exec())
