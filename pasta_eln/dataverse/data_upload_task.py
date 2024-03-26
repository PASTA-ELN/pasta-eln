""" Represents a data upload task. """
import asyncio
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_task_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import datetime
import time

from PySide6 import QtCore

from pasta_eln.GUI.dataverse.upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.dataverse.client import DataverseClient
from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.progress_thread import ProgressThread
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import get_adjusted_metadata, update_status


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
    self.config_model = self.db_api.get_config_model()
    if (self.config_model is None
        or not isinstance(self.config_model, ConfigModel)
        or not self.config_model.dataverse_login_info):
      raise ConfigError("Config model not found/Invalid Login Information.")
    self.dataverse_server_url = self.config_model.dataverse_login_info.get("server_url") or ""
    self.dataverse_api_token = self.config_model.dataverse_login_info.get("api_token") or ""
    self.dataverse_id = self.config_model.dataverse_login_info.get("dataverse_id") or ""
    self.metadata = self.config_model.metadata or {}
    self.dataverse_client = DataverseClient(self.dataverse_server_url, self.dataverse_api_token, 60)
    widget.uploadCancelPushButton.clicked.connect(self.cancel.emit)
    self.progress_thread = ProgressThread()
    self.progress_thread.progress_update = self.progressChanged

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

    """

    super().start_task()
    self.progressChanged.emit(0)
    self.statusChanged.emit(UploadStatusValues.Queued.name)
    self.statusChanged.emit(UploadStatusValues.Uploading.name)
    self.uploadModelCreated.emit(self.upload_model.id)
    test_file_path = "/home/jmurugan/Artefacts/10/Text File1.txt"
    self.upload_model.log = f"Generating ELN file..... {test_file_path}"
    self.db_api.update_model_document(self.upload_model)

    self.progress_thread.start()
    pid = ""
    try:
      self.upload_model.log = f"Creating dataset..... {self.upload_model.project_name}"
      metadata = get_adjusted_metadata(self.metadata)
      metadata["title"] = self.upload_model.project_name
      result = asyncio.run(self.dataverse_client.create_and_publish_dataset(self.dataverse_id, metadata))
      pid = f"{result['protocol']}:{result['authority']}/{result['identifier']}"
      self._extracted_from_start_task_32(
        'Created dataset in dataverse with PID:', pid, 25)
      # Uploading the ELN file to dataverse
      time.sleep(5)
      result = asyncio.run(self.dataverse_client.upload_file(pid,
                                                             test_file_path,
                                                             f"ELN file for the project: {self.upload_model.project_name}",
                                                             ["ELN"]))
      dataset_publish_result = result["dataset_publish_result"]
      file_pid = f"{dataset_publish_result['protocol']}:{dataset_publish_result['authority']}/{dataset_publish_result['identifier']}"
      self._extracted_from_start_task_32('Uploaded in dataverse with PID:',
                                         file_pid, 75)
    except Exception as e:
      self.upload_model.log = f"Error while uploading to dataverse: {e}"
      self.db_api.update_model_document(self.upload_model)
      self.statusChanged.emit(UploadStatusValues.Error.name)
    self._extracted_from_start_task_32('Finished the upload in dataverse with URL: ',
                                       f"{self.dataverse_server_url}/dataset.xhtml?persistentId={pid}", 75)
    self.progress_thread.finished = True
    self.finished.emit()
    self.statusChanged.emit(UploadStatusValues.Cancelled.name if self.cancelled else UploadStatusValues.Finished.name)

  def _extracted_from_start_task_32(self, arg0, identifier, arg2):
    self.upload_model.log = f"{arg0}{identifier}"
    self.db_api.update_model_document(self.upload_model)
    # self.progressChanged.emit(arg2)

  def cancel_task(self) -> None:
    """
    Cancels the data upload task.

    Explanation:
        This method cancels the data upload task by calling the super-class's cancel_task method.
        It updates the upload model log and status accordingly, and emits the statusChanged signal.

    """
    super().cancel_task()
    self.upload_model.log = f"Cancelled at {datetime.datetime.now().isoformat()}"
    self.upload_model.status = UploadStatusValues.Cancelled.name
    self.statusChanged.emit(UploadStatusValues.Cancelled.name)
