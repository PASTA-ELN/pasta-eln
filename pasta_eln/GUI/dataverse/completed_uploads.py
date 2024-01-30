#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: completed_uploads.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from datetime import datetime
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QFrame

from pasta_eln.GUI.dataverse.completed_upload_task import Ui_CompletedUploadTaskFrame
from pasta_eln.GUI.dataverse.completed_uploads_base import Ui_CompletedUploadsForm
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.upload_model import UploadModel


class CompletedUploads(Ui_CompletedUploadsForm):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    """
    Instantiates the create type dialog
    """
    return super(CompletedUploads, cls).__new__(cls)

  def __init__(self):
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.db_api = DatabaseAPI()
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)

  def load_ui(self):
    self.clear_ui()
    for upload in self.db_api.get_models(UploadModel):
      widget = self.get_completed_upload_task_widget(upload)
      self.completedUploadsVerticalLayout.addWidget(widget)

  def clear_ui(self):
    for widget_pos in reversed(range(self.completedUploadsVerticalLayout.count())):
      self.completedUploadsVerticalLayout.itemAt(widget_pos).widget().setParent(None)

  def get_completed_upload_task_widget(self, upload: UploadModel) -> QFrame:
    completedTaskFrame = QtWidgets.QFrame()
    completedTaskUi = Ui_CompletedUploadTaskFrame()
    completedTaskUi.setupUi(completedTaskFrame)
    completedTaskUi.projectNameLabel.setText(upload.project_name)

    completedTaskUi.statusLabel.setText(upload.status)
    match upload.status:
      case "In progress":
        completedTaskUi.dataverseUrlLabel.setText("Waiting..")
        completedTaskUi.finishedDateTimeLabel.setText("Waiting..")
      case "Finished":
        completedTaskUi.dataverseUrlLabel.setText(upload.dataverse_url)
        completedTaskUi.finishedDateTimeLabel.setText(datetime.fromisoformat(upload.finished_date_time).strftime(
          "%Y-%m-%d %H:%M:%S") if upload.finished_date_time else "")
      case "Failed" | "Cancelled":
        completedTaskUi.dataverseUrlLabel.setText("NA")
        completedTaskUi.finishedDateTimeLabel.setText("NA")
      case "Queued":
        completedTaskUi.dataverseUrlLabel.setText("Waiting..")
        completedTaskUi.finishedDateTimeLabel.setText("Waiting..")
      case _:
        completedTaskUi.dataverseUrlLabel.setText("Error state..")
        completedTaskUi.finishedDateTimeLabel.setText("Error state..")
    return completedTaskFrame


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = CompletedUploads()
  ui.instance.show()
  sys.exit(app.exec())
