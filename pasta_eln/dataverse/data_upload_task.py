""" Represents a data upload task. """
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
from time import sleep

from PySide6 import QtCore

from pasta_eln.GUI.dataverse.upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import update_status


class DataUploadTask(GenericTaskObject):
  """
  Represents a data upload task.

  Explanation:
      This class handles the data upload task, including tracking progress, updating status,
      and managing the upload model.
      It provides methods to start the task, cancel the task, and handle the initialization of the task.

  Args:
      widget (Ui_UploadWidgetFrame): The widget containing the upload task elements.

  Returns:
      None
  """
  progressChanged = QtCore.Signal(int)
  statusChanged = QtCore.Signal(str)
  uploadModelCreated = QtCore.Signal(str)

  def __init__(self, widget: Ui_UploadWidgetFrame) -> None:
    """
    Initializes a DataUploadTask instance.

    Explanation:
        This method initializes a DataUploadTask instance by connecting signals to the widget elements,
        setting up attributes for project name, database API, upload model, and configuration model,
        and connecting the cancel button to the cancel signal.

    Args:
        widget (Ui_UploadWidgetFrame): The widget containing the upload task elements.

    Returns:
        None
    """
    super().__init__()
    self.progressChanged.connect(widget.uploadProgressBar.setValue)
    self.statusChanged.connect(lambda status: update_status(status, widget.statusIconLabel, widget.statusLabel))
    self.project_name = widget.uploadProjectLabel.text()
    self.db_api = DatabaseAPI()
    self.upload_model = UploadModel(project_name=self.project_name,
                                    status=UploadStatusValues.Queued.name,
                                    log=f"Upload initiated for project {self.project_name} at {datetime.datetime.now().isoformat()}\n")
    self.upload_model = self.db_api.create_model_document(self.upload_model)  # type: ignore[assignment]
    self.config_model = self.db_api.get_model(self.db_api.config_doc_id, ConfigModel)
    widget.uploadCancelPushButton.clicked.connect(lambda: self.cancel.emit())

  def start_task(self) -> None:
    """
    Starts the data upload task.

    Explanation:
        This method starts the data upload task by emitting signals to update the progress and status,
        creating the upload model, and performing the upload process.
        It updates the progress and status, and updates the upload model accordingly.
        It also handles the cancellation of the task and emits the appropriate signals.
        It also handles the upload tasks to dataverse
          - Generating ELN file
          - Uploading to dataverse
          - Saving the upload model whenever needed

    Args:
        None

    """
    super().start_task()
    self.progressChanged.emit(0)
    self.statusChanged.emit(UploadStatusValues.Queued.name)
    self.statusChanged.emit(UploadStatusValues.Uploading.name)
    self.uploadModelCreated.emit(self.upload_model.id)
    self.upload_model.log = "Generating ELN file....."
    for progressbar_value in range(101):
      self.progressChanged.emit(progressbar_value)
      if self.cancelled:
        self.upload_model.status = UploadStatusValues.Cancelled.name
        break
      self.upload_model.log = f"Uploading.......... Progress: {progressbar_value}%"
      self.upload_model.status = UploadStatusValues.Uploading.name
      self.db_api.update_model_document(self.upload_model)

      sleep(random.uniform(0.01, 0.06))
    if not self.cancelled:
      self.upload_model.log = f"Uploading completed at {datetime.datetime.now().isoformat()}"
      self.upload_model.finished_date_time = datetime.datetime.now().isoformat()
      self.upload_model.status = UploadStatusValues.Finished.name
      self.upload_model.dataverse_url = f"https://dataverse.harvard.edu/dataverse/{self.upload_model.project_name}"
      self.upload_model.log = f"Uploading to url: {self.upload_model.dataverse_url}"
    self.db_api.update_model_document(self.upload_model)
    self.finished.emit()
    self.statusChanged.emit(UploadStatusValues.Cancelled.name if self.cancelled else UploadStatusValues.Finished.name)

  def cancel_task(self) -> None:
    """
    Cancels the data upload task.

    Explanation:
        This method cancels the data upload task by calling the super-class's cancel_task method.
        It updates the upload model log and status accordingly, and emits the statusChanged signal.

    Args:
        None

    """
    super().cancel_task()
    self.upload_model.log = f"Cancelled at {datetime.datetime.now().isoformat()}"
    self.upload_model.status = UploadStatusValues.Cancelled.name
    self.statusChanged.emit(UploadStatusValues.Cancelled.name)
