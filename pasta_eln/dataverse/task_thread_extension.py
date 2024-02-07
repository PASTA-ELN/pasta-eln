""" Represents a task worker_thread extension. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_task_thread_extension.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging

from PySide6 import QtCore
from PySide6.QtCore import QObject

from pasta_eln.dataverse.generic_task_object import GenericTaskObject


class TaskThreadExtension(QObject):
  """
  Represents a task worker_thread extension.

  Explanation:
      This class provides an extension for running a task in a separate worker_thread.
      It initializes the task and worker_thread, and provides a method to quit the task and clean up resources.

  Args:
      task (GenericTaskObject): The task to be executed in the separate worker_thread.

  Returns:
      None
  """

  def __init__(self, task: GenericTaskObject) -> None:
    """
    Initializes the TaskThreadExtension instance.

    Explanation:
        This method initializes the TaskThreadExtension instance by setting the task and worker_thread attributes.
        It moves the task to the worker_thread and starts the worker_thread.

    Args:
        task (GenericTaskObject): The task object to be executed in the separate worker_thread.

    Returns:
        None
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.task: GenericTaskObject = task
    self.worker_thread: QtCore.QThread = QtCore.QThread()
    self.task.moveToThread(self.worker_thread)
    self.worker_thread.start()

  def quit(self) -> None:
    """
    Quits the task and cleans up resources.

    Explanation:
        This method emits the cancel signal of the task, performs cleanup, and signals the worker_thread to quit.

    Args:
        self: The TaskThreadExtension instance.

    """
    self.logger.info("Quitting task thread extension, Task id: %s", self.task.id)
    self.task.cancel.emit()
    self.task.cleanup()
    self.worker_thread.quit()
