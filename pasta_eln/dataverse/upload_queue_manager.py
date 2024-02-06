""" Manages the upload queue. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_manager_task_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from time import sleep

from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.task_thread_extension import TaskThreadExtension


class UploadQueueManager(GenericTaskObject):
  """
  Manages the upload queue.

  Explanation:
      This class handles the management of an upload queue.
      It provides methods to add tasks to the queue, remove tasks from the queue,
      start the task execution, clean up resources, and cancel the task.

  """

  def __init__(self) -> None:
    """
    Initializes the UploadQueueManager instance.

    Explanation:
        This method initializes the UploadQueueManager instance by setting up the logger,
        attributes for concurrent uploads,
        the upload and running queues, and the database API.
        It also calls the set_concurrent_uploads method to retrieve the number of concurrent uploads from the database.

    Args:
        None

    Returns:
        None
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.number_of_concurrent_uploads: int | None = None
    self.config_model: ConfigModel | None = None
    self.upload_queue: list[TaskThreadExtension] = []
    self.running_queue: list[TaskThreadExtension] = []
    self.db_api: DatabaseAPI = DatabaseAPI()
    self.set_concurrent_uploads()

  def set_concurrent_uploads(self) -> None:
    """
    Resets the number of concurrent uploads.

    Explanation:
        This method retrieves the number of concurrent uploads from the database and sets it as the value for the
        number_of_concurrent_uploads attribute.

    Args:
        None

    Returns:
        None
    """
    self.logger.info("Resetting number of concurrent uploads..")
    model = self.db_api.get_model(self.db_api.config_doc_id, ConfigModel)
    self.config_model = model if isinstance(model, ConfigModel) else None
    self.number_of_concurrent_uploads = self.config_model.parallel_uploads_count if self.config_model else None

  def add_to_queue(self, upload_task_thread: TaskThreadExtension) -> None:
    """
    Adds a thread task to the upload queue.

    Explanation:
        This method adds the given upload_task_thread to the upload queue.
        It also connects the finished signal of the task to the remove_from_queue method.

    Args:
        upload_task_thread (TaskThreadExtension): The thread task to be added to the upload queue.

    Returns:
        None
    """
    self.logger.info("Adding thread task to upload queue, id: %s", upload_task_thread.task.id)
    self.upload_queue.append(upload_task_thread)
    upload_task_thread.task.finished.connect(lambda: self.remove_from_queue(upload_task_thread))

  def remove_from_queue(self, upload_task_thread: TaskThreadExtension) -> None:
    """
    Removes a thread task from the upload queue.

    Explanation:
        This method removes the given upload_task_thread from the upload queue.
        It also removes the task from the running queue and quits the worker thread.

    Args:
        upload_task_thread (TaskThreadExtension): The thread task to be removed from the upload queue.

    Returns:
        None
    """
    self.logger.info("Removing thread task from upload queue, id: %s", upload_task_thread.task.id)
    if upload_task_thread in self.upload_queue:
      self.upload_queue.remove(upload_task_thread)
    if upload_task_thread in self.running_queue:
      self.running_queue.remove(upload_task_thread)
    upload_task_thread.worker_thread.quit()

  def start_task(self) -> None:
    """
    Starts the upload queue task.

    Explanation:
        This method starts the upload queue task by calling the super-class's start_task method.
        It iterates over the upload queue
        and starts the tasks if the running queue is not full and the task is not canceled.

    Args:
        None

    Returns:
        None
    """
    self.logger.info("Starting upload queue..")
    super().start_task()
    while not self.cancelled:
      if self.number_of_concurrent_uploads and len(self.running_queue) < self.number_of_concurrent_uploads:
        for upload_task_thread in self.upload_queue:
          if self.cancelled or len(self.running_queue) >= self.number_of_concurrent_uploads:
            break
          if not upload_task_thread.task.started and not upload_task_thread.task.cancelled:
            self.running_queue.append(upload_task_thread)
            upload_task_thread.task.start.emit()
      sleep(0.5)

  def cleanup(self) -> None:
    """
    Cleans up the upload manager.

    Explanation:
        This method performs the cleanup of the upload manager by calling the super-class's cleanup method
        and emptying the upload queue.

    Args:
        None

    Returns:
        None
    """
    self.logger.info("Cleaning up upload manager..")
    super().cleanup()
    self.empty_upload_queue()

  def empty_upload_queue(self) -> None:
    """
    Empties the upload queue.

    Explanation:
        This method empties the upload queue by quitting each upload task thread and clearing the upload queue.

    Args:
        None

    Returns:
        None
    """
    self.logger.info("Emptying upload queue..")
    for upload_task_thread in self.upload_queue:
      upload_task_thread.quit()
    self.upload_queue.clear()

  def cancel_task(self) -> None:
    """
    Cancels the upload queue manager completely.

    Explanation:
        This method cancels the upload queue by calling the super-class's cancel_task method.
        It emits the cancel signal for each task in the running queue and empties the upload queue.

    Args:
        None

    Returns:
        None
    """
    self.logger.info("Cancelling upload queue..")
    super().cancel_task()
    for upload_task_thread in self.running_queue:
      upload_task_thread.task.cancel.emit()
    self.empty_upload_queue()
