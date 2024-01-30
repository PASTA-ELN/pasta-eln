#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_task_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import datetime
import random
import time

import qtawesome as qta
from PySide6 import QtCore
from PySide6.QtWidgets import QLabel

from pasta_eln.GUI.dataverse.upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.upload_model import UploadModel


def update_status(status,
                  statusIconLabel: QLabel,
                  statusLabel: QLabel):
  statusLabel.setText(status)
  match status:
    case "Queued":
      statusIconLabel.setPixmap(qta.icon('ph.queue-bold').pixmap(statusIconLabel.size()))
    case "Uploading":
      statusIconLabel.setPixmap(qta.icon('mdi6.progress-upload').pixmap(statusIconLabel.size()))
    case "Cancelled":
      statusIconLabel.setPixmap(qta.icon('mdi.cancel').pixmap(statusIconLabel.size()))
    case "Finished":
      statusIconLabel.setPixmap(qta.icon('fa.check-circle-o').pixmap(statusIconLabel.size()))
    case "Error":
      statusIconLabel.setPixmap(qta.icon('msc.error-small').pixmap(statusIconLabel.size()))
    case "Warning":
      statusIconLabel.setPixmap(qta.icon('fa.warning').pixmap(statusIconLabel.size()))


class DataUploadTask(GenericTaskObject):
  progressChanged = QtCore.Signal(int)
  statusChanged = QtCore.Signal(str)
  uploadModelCreated = QtCore.Signal(str)

  def __init__(self, widget: Ui_UploadWidgetFrame):
    super().__init__()
    self.progressChanged.connect(widget.uploadProgressBar.setValue)
    self.statusChanged.connect(lambda status: update_status(status, widget.statusIconLabel, widget.statusLabel))
    self.project_name = widget.uploadProjectLabel.text()
    self.db_api = DatabaseAPI()
    self.upload_model = UploadModel(project_name=self.project_name, status="Queued",
                                    log=f"Upload initiated for project {self.project_name} at {time.asctime()}\n")
    self.upload_model = self.db_api.create_model_document(self.upload_model)
    self.config_model = self.db_api.get_model("-dataverseConfig-", ConfigModel)
    widget.uploadCancelPushButton.clicked.connect(lambda: self.cancel.emit())

  def start_task(self):
    super().start_task()
    self.progressChanged.emit(0)
    self.statusChanged.emit("Queued")
    self.statusChanged.emit("Uploading")
    self.uploadModelCreated.emit(self.upload_model.id)
    self.upload_model.log = "Generating ELN file....."
    for progressbar_value in range(101):
      self.progressChanged.emit(progressbar_value)
      if self.cancelled:
        break
      self.upload_model.log = f"Uploading.......... Progress: {progressbar_value}%"
      self.upload_model.status = "In progress"
      self.db_api.update_model_document(self.upload_model)

      time.sleep(random.uniform(0.01, 0.06))
      # time.sleep(0.05)
    if not self.cancelled:
      self.upload_model.log = f"Uploading completed at {time.asctime()}"
      self.upload_model.finished_date_time = datetime.datetime.now().isoformat()
      self.upload_model.status = "Finished"
      self.upload_model.dataverse_url = f"https://dataverse.harvard.edu/dataverse/{self.upload_model.project_name}"
      self.upload_model.log = f"Uploading to url: {self.upload_model.dataverse_url}"
    self.db_api.update_model_document(self.upload_model)
    self.finished.emit()
    self.statusChanged.emit("Cancelled" if self.cancelled else "Finished")

  def cancel_task(self):
    super().cancel_task()
    self.upload_model.log = f"Cancelled at {time.asctime()}"
    self.upload_model.status = "Cancelled"
    self.statusChanged.emit("Cancelled")
