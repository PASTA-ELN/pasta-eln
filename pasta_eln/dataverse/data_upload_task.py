""" Represents a data upload task. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_upload_task.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Callable

from PySide6 import QtCore
from PySide6.QtGui import QImage, QPixmap

from pasta_eln.dataverse.client import DataverseClient
from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.progress_updater_thread import ProgressUpdaterThread
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import get_flattened_metadata, update_status


class DataUploadTask(GenericTaskObject):
  """
  Represents a task for uploading data to a Dataverse repository.

  Explanation:
      This class manages the process of uploading data to Dataverse, including creating datasets,
      uploading files, checking dataset locks, and handling cancellation of the upload task.
  """
  progress_changed = QtCore.Signal(int)
  status_changed = QtCore.Signal(str)
  upload_model_created = QtCore.Signal(str)

  def __init__(self,
               project_name: str,
               progress_update_callback: Callable[[int], None],
               status_label_set_text_callback: Callable[[str], None],
               status_icon_set_pixmap_callback: Callable[[QPixmap | QImage | str], None],
               upload_cancel_clicked_signal_callback: QtCore.Signal) -> None:
    """
    Initializes the DataUploadTask with necessary callbacks and information.

    Args:
        project_name (str): The name of the project for the upload task.
        progress_update_callback (Callable[[int], None]): Callback for updating progress.
        status_label_set_text_callback (Callable[[str], None]): Callback for setting status label text.
        status_icon_set_pixmap_callback (Callable[[QPixmap | QImage | str], None]): Callback for setting status icon.
        upload_cancel_clicked_signal_callback (QtCore.Signal): Signal for upload cancellation.
    """
    super().__init__()
    self.db_api: DatabaseAPI | None = None
    self.dataverse_client: DataverseClient | None = None
    self.upload_model: UploadModel | None = None
    self.config_model: ConfigModel | None = None
    self.dataverse_id: str = ""
    self.dataverse_api_token: str = ""
    self.dataverse_server_url: str = ""
    self.metadata: dict[str, Any] = {}

    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.project_name = project_name

    # Connect slots
    self.progress_changed.connect(progress_update_callback)
    self.status_changed.connect(
      lambda status: update_status(status, status_label_set_text_callback, status_icon_set_pixmap_callback))
    upload_cancel_clicked_signal_callback.connect(self.cancel.emit)  # type: ignore[attr-defined]

    # Create progress thread to update the progress
    self.progress_thread = ProgressUpdaterThread()
    self.progress_thread.progress_update = self.progress_changed

  def start_task(self) -> None:
    """
    Start the data upload task by generating an ELN file, creating a dataset in Dataverse,
    uploading the file, and finalizing the upload task.

    Args:
        self: Instance of the data upload task.
    """
    super().start_task()
    self.initialize()

    # Emitting signals to update initial status
    self.update_changed_status(UploadStatusValues.Uploading.name)
    # Emit the upload model id
    # so that the parent thread can retrieve the model
    if self.upload_model:
      self.upload_model_created.emit(self.upload_model.id)

    # Start the progress updater thread
    self.progress_thread.start()

    # Step 1: Generate ELN file for the project
    if self.check_if_cancelled():
      return
    self.update_log(f"Step 1: Generating ELN file for project: {self.project_name}", self.logger.info)
    # Add logic to generate ELN file for the project
    eln_file_path = "/home/jmurugan/Artefacts/10/Text File1.txt"
    self.update_log(f"Successfully generated ELN file: {eln_file_path}", self.logger.info)

    # Step 2: Create dataset for the project in dataverse
    if self.check_if_cancelled():
      return
    persistent_id = self.create_dataset_for_pasta_project()
    if persistent_id is None:
      self.logger.warning("Failed to create dataset for project: %s, hence finalizing the upload",
                          self.project_name)
      self.finalize_upload_task(UploadStatusValues.Error.name)
      return

    # Step 3: Check if the dataset is unlocked post the creation
    if self.check_if_cancelled():
      return
    if not self.check_if_dataset_is_unlocked(persistent_id):
      self.logger.warning("Failed to unlock dataset for project: %s, hence finalizing the upload",
                          self.project_name)
      self.finalize_upload_task(UploadStatusValues.Error.name)
      return

    # Step 4: Upload the generated ELN file to the dataset
    if self.check_if_cancelled():
      return
    file_pid = self.upload_generated_eln_file_to_dataset(persistent_id, eln_file_path)
    if file_pid is None:
      self.logger.warning("Failed to upload eln file to dataset for project: %s, hence finalizing the upload",
                          self.project_name)
      self.finalize_upload_task(UploadStatusValues.Error.name)
      return

    # Final step: Update the log and finalize the upload task
    upload_url = f"{self.dataverse_server_url}/dataset.xhtml?persistentId={persistent_id}"
    self.update_log(
      f"Successfully uploaded ELN file, URL: {upload_url}",
      self.logger.info)
    if self.upload_model:
      self.upload_model.dataverse_url = upload_url
    self.finalize_upload_task(UploadStatusValues.Cancelled.name if self.cancelled else UploadStatusValues.Finished.name)

  def initialize(self) -> None:
    """
    Initialize the data upload task by setting up the database API,
    creating an upload model, and reading configuration information.
    Since this method consists of heavy operations, it's not invoked inside the constructor.

    Raises:
        ConfigError: If the config model is not found or contains invalid login information.
    """

    self.db_api = DatabaseAPI()
    # Create upload model in database
    self.upload_model = UploadModel(project_name=self.project_name,
                                    status=UploadStatusValues.Queued.name,
                                    log=f"Upload initiated for project {self.project_name} at {datetime.now().isoformat()}\n")
    self.upload_model = self.db_api.create_model_document(self.upload_model)  # type: ignore[assignment]
    self.logger.info("Upload model created: %s", self.upload_model)
    # Read config and get the login information along with the metadata
    self.config_model = self.db_api.get_config_model()
    if self.config_model is None:
      raise ConfigError("Config model not found/Invalid Login Information.")
    login_info = self.config_model.dataverse_login_info or {}
    self.dataverse_server_url = login_info.get("server_url", "")
    self.dataverse_api_token = login_info.get("api_token", "")
    self.dataverse_id = login_info.get("dataverse_id", "")
    self.metadata = self.config_model.metadata or {}
    self.dataverse_client = DataverseClient(self.dataverse_server_url, self.dataverse_api_token, 60)

  def finalize_upload_task(self, status: str = UploadStatusValues.Finished.name) -> None:
    """
    Finalizes the upload task by emitting signals to cancel progress, mark as finished, and update the UI status.

    Args:
        status (str): The status to be emitted.
    """
    self.progress_thread.finalize.emit()
    self.finished.emit()
    if self.upload_model:
      self.upload_model.finished_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.update_changed_status(status)

  def create_dataset_for_pasta_project(self) -> str | None:
    """
    Creates a dataset for the PASTA project by adjusting metadata and invoking the dataverse client method.

    Returns:
        str or None: The persistent identifier of the created dataset if successful, None otherwise.
    """
    if self.upload_model is None or self.dataverse_client is None:
      return None
    self.update_log(f"Step 2: Creating dataset..... {self.upload_model.project_name}", self.logger.info)
    persistent_id = None

    # Get the saved metadata from the database
    # and adjust it to the required format for invoking the dataverse client method
    metadata_adjusted = get_flattened_metadata(self.metadata)
    metadata_adjusted["title"] = self.upload_model.project_name  # Set the title to the PASTA project name
    result = asyncio.run(self.dataverse_client.create_and_publish_dataset(self.dataverse_id, metadata_adjusted))
    if (isinstance(result, dict) and
        'identifier' in result and
        'authority' in result and
        'protocol' in result):
      persistent_id = f"{result.get('protocol')}:{result.get('authority')}/{result.get('identifier')}"
      log = f'Dataset creation succeeded with PID: {persistent_id}'
      self.update_log(log, self.logger.info)
      self.logger.info(log)
    else:
      self.update_log(f'Dataset creation failed with errors: {result}', self.logger.error)
    return persistent_id

  def check_if_dataset_is_unlocked(self, persistent_id: str) -> bool:
    """
    Checks if a dataset is unlocked after a publish operation.

    Args:
        persistent_id (str): The persistent identifier of the dataset to check.

    Returns:
        bool: True if the dataset is unlocked, False otherwise.
    """
    if self.dataverse_client is None:
      return False
    self.update_log("Step 3: Checking if dataset is unlocked after the publish operation..", self.logger.info)
    unlocked = False
    for _ in range(10):
      result = asyncio.run(self.dataverse_client.get_dataset_locks(persistent_id))
      if isinstance(result, dict):
        if locks := result.get('locks'):
          for lock in locks:
            self.update_log(
              f"Dataset with PID: {persistent_id} is locked. Lock type: {lock.get('lockType')}, Message: {lock.get('message')}",
              self.logger.info)
        else:
          self.update_log(f"Dataset with PID: {persistent_id} is unlocked already!", self.logger.info)
          unlocked = True
          break
      else:
        self.update_log(f"Dataset lock check failed. {result}", self.logger.info)
      time.sleep(1)
    if not unlocked:
      self.update_log(f"Dataset with PID: {persistent_id} is still locked after 10 retries!", self.logger.error)
    return unlocked

  def upload_generated_eln_file_to_dataset(self, persistent_id: str, eln_file_path: str) -> str | None:
    """
    Uploads the generated ELN file to a dataset in Dataverse.

    Args:
        persistent_id (str): The persistent identifier of the dataset.
        eln_file_path (str): The path to the ELN file to upload.

    Returns:
        str or None: The file PID if upload is successful, None otherwise.
    """
    self.update_log(f"Step 4: Uploading file {eln_file_path} to dataset with PID: {persistent_id}.....",
                    self.logger.info)
    if self.upload_model is None or self.dataverse_client is None:
      return None
    result = asyncio.run(self.dataverse_client.upload_file(persistent_id,
                                                           eln_file_path,
                                                           f"Generated ELN file for the project: {self.upload_model.project_name}",
                                                           ["ELN"]))
    if (isinstance(result, dict)
        and 'file_upload_result' in result
        and 'dataset_publish_result' in result):
      dataset_publish_result = result["dataset_publish_result"]
      file_pid = f"{dataset_publish_result.get('protocol')}:{dataset_publish_result.get('authority')}/{dataset_publish_result.get('identifier')}"
      self.update_log(f'ELN File uploaded successfully, generated file PID: {file_pid}', self.logger.info)
    else:
      self.update_log(f'ELN File upload failed with errors: {result}', self.logger.error)
      return None
    return file_pid

  def update_log(self, log: str, logger_method: Callable[[str], None] | None) -> None:
    """
    Updates the log with the provided message and triggers the logger method if available.

    Args:
        log (str): The log message to be updated.
        logger_method (Callable[[str], None] | None): The method to handle logging.
    """
    if logger_method:
      logger_method(log)
    if self.upload_model and self.db_api:
      self.upload_model.log = log
      self.db_api.update_model_document(self.upload_model)

  def cancel_task(self) -> None:
    """
    Cancels the data upload task.

    Explanation:
        This method cancels the data upload task by calling the super-class's cancel_task method.
        It updates the upload model log and status accordingly, and emits the status_changed signal.

    """
    if self.cancelled:
      return
    super().cancel_task()
    if self.upload_model:
      self.upload_model.log = f"Cancelled at {datetime.now().isoformat()}"
    self.progress_thread.cancel.emit()
    self.update_changed_status(UploadStatusValues.Cancelled.name)

  def update_changed_status(self, status: str = UploadStatusValues.Queued.name) -> None:
    """
    Updates the status of the upload task.

    Explanation:
        This function updates the status of the upload task to the specified status value.
        It then updates the model document in the database and emits a signal for the status change.

    Args:
        status (str): The status value to update the upload task to. Defaults to 'Queued'.
    """
    if self.upload_model and self.db_api:
      self.upload_model.status = status
      self.db_api.update_model_document(self.upload_model)
    self.status_changed.emit(status)

  def check_if_cancelled(self) -> bool:
    """
    Checks if the data upload task has been cancelled and finalizes the upload if cancelled.

    Returns:
        bool: True if the task is cancelled, False otherwise.
    """
    if self.cancelled:
      self.update_log(
        "User cancelled the upload, hence finalizing the upload!",
        self.logger.info,
      )
      self.finalize_upload_task(UploadStatusValues.Cancelled.name)
    return self.cancelled
