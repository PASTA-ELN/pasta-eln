#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_manager_task_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
import time

from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_api import DatabaseAPI
from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.task_thread_extension import TaskThreadExtension


class UploadQueueManager(GenericTaskObject):
  def __init__(self):
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.number_of_concurrent_uploads = None
    self.config_model = None
    self.upload_queue: list[TaskThreadExtension] = []
    self.running_queue: list[TaskThreadExtension] = []
    self.db_api = DatabaseAPI()
    self.set_concurrent_uploads()

  def set_concurrent_uploads(self):
    self.logger.info("Resetting number of concurrent uploads..")
    self.config_model = self.db_api.get_model(self.db_api.config_doc_id, ConfigModel)
    self.number_of_concurrent_uploads = self.config_model.parallel_uploads_count

  def add_to_queue(self, upload_task_thread: TaskThreadExtension):
    self.logger.info("Adding thread task to upload queue, id: %s", upload_task_thread.task.id)
    self.upload_queue.append(upload_task_thread)
    upload_task_thread.task.finished.connect(lambda: self.remove_from_queue(upload_task_thread))

  def remove_from_queue(self, upload_task_thread: TaskThreadExtension):
    self.logger.info("Removing thread task from upload queue, id: %s", upload_task_thread.task.id)
    if upload_task_thread in self.upload_queue:
      self.upload_queue.remove(upload_task_thread)
    if upload_task_thread in self.running_queue:
      self.running_queue.remove(upload_task_thread)
    upload_task_thread.worker_thread.quit()

  def start_task(self):
    super().start_task()
    self.logger.info("Starting upload queue..")
    while not self.cancelled:
      if len(self.running_queue) < self.number_of_concurrent_uploads:
        for upload_task_thread in self.upload_queue:
          if self.cancelled or len(self.running_queue) >= self.number_of_concurrent_uploads:
            break
          if not upload_task_thread.task.started:
            self.running_queue.append(upload_task_thread)
            upload_task_thread.task.start.emit()
      time.sleep(0.5)

  def cleanup(self):
    super().cleanup()
    self.logger.info("Cleaning up upload manager..")
    self.empty_upload_queue()

  def empty_upload_queue(self):
    self.logger.info("Emptying upload queue..")
    for upload_task_thread in self.upload_queue:
      upload_task_thread.quit()
    self.upload_queue.clear()

  def cancel_task(self):
    super().cancel_task()
    self.logger.info("Cancelling upload queue..")
    for upload_task_thread in self.running_queue:
      upload_task_thread.task.cancel.emit()
    self.empty_upload_queue()
