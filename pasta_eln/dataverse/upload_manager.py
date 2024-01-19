#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_manager_task_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import time

from pasta_eln.dataverse.generic_task_object import GenericTaskObject
from pasta_eln.dataverse.task_thread_abstraction import TaskThreadAbstraction


class UploadManager(GenericTaskObject):
  def __init__(self):
    super().__init__()
    self.upload_queue: list[TaskThreadAbstraction] = []
    self.running_queue: list[TaskThreadAbstraction] = []
    self.number_of_concurrent_uploads = 5

  def add_to_queue(self, upload_task_thread: TaskThreadAbstraction):
    self.upload_queue.append(upload_task_thread)
    upload_task_thread.task.finished.connect(lambda: self.remove_from_queue(upload_task_thread))

  def remove_from_queue(self, upload_task_thread: TaskThreadAbstraction):
    if upload_task_thread in self.upload_queue:
      self.upload_queue.remove(upload_task_thread)
    if upload_task_thread in self.running_queue:
      self.running_queue.remove(upload_task_thread)
    upload_task_thread.thread.quit()

  def start_task(self):
    super().start_task()
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
    print(f"Cleanup..., queue count: {len(self.upload_queue)}")
    self.empty_upload_queue()

  def empty_upload_queue(self):
    for upload_task_thread in self.upload_queue:
      upload_task_thread.quit()
    self.upload_queue.clear()

  def cancel_task(self):
    super().cancel_task()
    for upload_task_thread in self.upload_queue:
      upload_task_thread.task.cancel.emit()
