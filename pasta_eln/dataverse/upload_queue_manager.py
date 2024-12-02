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

from PySide6 import QtCore
from PySide6.QtCore import Qt

from pasta_eln.database.models.config_model import ConfigModel
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
  cancel_all_tasks = QtCore.Signal()

  def __init__(self) -> None:
    """
    Initializes the UploadQueueManager instance.

    Explanation:
        This method initializes the UploadQueueManager instance by setting up the logger,
        attributes for concurrent uploads,
        the upload and running queues, and the database API.
        It also calls the set_concurrent_uploads method to retrieve the number of concurrent uploads from the database.
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.number_of_concurrent_uploads: int | None = None
    self.config_model: ConfigModel | None = None
    self.upload_queue: list[TaskThreadExtension] = []
    self.running_queue: list[TaskThreadExtension] = []
    self.db_api: DatabaseAPI = DatabaseAPI()
    self.cancel_all_tasks.connect(self.cancel_all_queued_tasks_and_empty_queue,
                                  type=Qt.DirectConnection)  # type: ignore[attr-defined]
    self.set_concurrent_uploads()

  def set_concurrent_uploads(self) -> None:
    """
    Resets the number of concurrent uploads.

    Explanation:
        This method retrieves the number of concurrent uploads from the database and sets it as the value for the
        number_of_concurrent_uploads attribute.
    """
    self.logger.info("Resetting number of concurrent uploads..")
    self.config_model = self.db_api.get_config_model()
    self.number_of_concurrent_uploads = self.config_model.parallel_uploads_count if self.config_model else None

  def add_to_queue(self, upload_task_thread: TaskThreadExtension) -> None:
    """
    Adds a thread task to the upload queue.

    Explanation:
        This method adds the given upload_task_thread to the upload queue.
        It also connects the finish signal of the task to the remove_from_queue method.

    Args:
        upload_task_thread (TaskThreadExtension): The thread task to be added to the upload queue.

    """
    self.logger.info("Adding thread task to upload queue, id: %s", upload_task_thread.task.id)
    self.upload_queue.append(upload_task_thread)
    upload_task_thread.task.finish.connect(lambda: self.remove_from_queue(upload_task_thread))

  def remove_from_queue(self, upload_task_thread: TaskThreadExtension) -> None:
    """
    Removes a thread task from the upload queue.

    Explanation:
        This method removes the given upload_task_thread from the upload queue.
        It also removes the task from the running queue and quits the worker thread.

    Args:
        upload_task_thread (TaskThreadExtension): The thread task to be removed from the upload queue.

    """
    self.logger.info("Removing thread task from upload queue, id: %s", upload_task_thread.task.id)
    if upload_task_thread in self.upload_queue:
      self.upload_queue.remove(upload_task_thread)
    if upload_task_thread in self.running_queue:
      self.running_queue.remove(upload_task_thread)
    upload_task_thread.worker_thread.quit()
    upload_task_thread.task.cleanup()

  def start_task(self) -> None:
    """
    Starts the upload queue task.

    Explanation:
        This method starts the upload queue task by calling the super-class's start_task method.
        It iterates over the upload queue
        and starts the tasks if the running queue is not full and the task is not canceled.
    """
    self.logger.info("Starting upload queue..")
    super().start_task()
    while not self.cancelled:
      if self.number_of_concurrent_uploads and len(self.running_queue) < self.number_of_concurrent_uploads:
        for upload_task_thread in self.upload_queue:
          if self.cancelled or len(self.running_queue) >= self.number_of_concurrent_uploads:
            break
          if (not upload_task_thread.task.started
              and not upload_task_thread.task.cancelled
              and not upload_task_thread.task.finished
              and upload_task_thread not in self.running_queue):
            self.running_queue.append(upload_task_thread)
            upload_task_thread.task.start.emit()
      sleep(0.5)

  def cleanup(self) -> None:
    """
    Cleans up the upload manager.

    Explanation:
        This method performs the cleanup of the upload manager by calling the super-class's cleanup method
        and emptying the upload queue.
    """
    self.logger.info("Cleaning up upload manager..")
    super().cleanup()
    self.empty_upload_queue()

  def empty_upload_queue(self) -> None:
    """
    Empties the upload queue.

    Explanation:
        This method empties the upload queue by quitting each upload task thread and clearing the upload queue.
    """
    self.logger.info("Emptying upload queue..")
    for upload_task_thread in self.upload_queue:
      upload_task_thread.worker_thread.quit()
    self.upload_queue.clear()

  def remove_cancelled_tasks(self) -> None:
    """
    Removes cancelled tasks from the upload queue.

    Explanation:
        This method identifies tasks in the upload queue that have been cancelled and removes them from the queue.
        It also logs the removal of each cancelled task.

    Args:
        self: The instance of the UploadQueueManager.
    """
    self.logger.info("Removing cancelled tasks from the queue..")
    cancelled_tasks = [upload_task_thread for upload_task_thread in self.upload_queue if
                       upload_task_thread.task.cancelled]
    for upload_task_thread in cancelled_tasks:
      self.remove_from_queue(upload_task_thread)

  def cancel_task(self) -> None:
    """
    Cancels the upload queue manager completely.

    Explanation:
        This method cancels the upload queue by calling the super-class's cancel_task method.
        It emits the cancel signal for each task in the running queue and empties the upload queue.
    """
    self.logger.info("Cancelling upload manager..")
    super().cancel_task()
    # Cancel all the tasks in the pool and remove them all from the queue
    self.cancel_all_queued_tasks_and_empty_queue()

  def cancel_all_queued_tasks_and_empty_queue(self) -> None:
    """
    Cancels all queued tasks and empties the upload queue.

    Explanation:
        This function iterates through the upload queue, cancelling each task thread by emitting a cancel signal.
        It then empties the upload queue.

    Args:
        self: The instance of the class.
    """
    self.logger.info("Cancelling upload queue and the empty the upload queue..")
    for upload_task_thread in self.upload_queue:
      upload_task_thread.task.cancel.emit()
    if self.upload_queue:
      self.remove_cancelled_tasks()
