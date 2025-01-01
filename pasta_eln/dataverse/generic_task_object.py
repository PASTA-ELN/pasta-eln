""" Represents a generic task object. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: generic_task_object.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import itertools
import logging
from PySide6 import QtCore
from PySide6.QtCore import QObject, Qt


class GenericTaskObject(QObject):
  """
  Represents a generic task object.

  Explanation:
      This class represents a generic task object and provides methods for managing the task.
      It includes methods for cancelling the task, starting the task, and cleaning up the task.
  """
  cancel = QtCore.Signal()
  start = QtCore.Signal()
  finish = QtCore.Signal()
  id_iterator = itertools.count()

  def __init__(self) -> None:
    """
    Initializes the GenericTaskObject instance.

    Explanation:
        This method initializes the GenericTaskObject instance by setting the initial values of the cancelled, started, and cleaned attributes.
        It also connects the cancel signal to the cancel_task method and the start signal to the start_task method.

    Args:
        self: The GenericTaskObject instance.

    Returns:
        None
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.id = next(self.id_iterator)
    self.cancelled = False
    self.started = False
    self.cleaned = False
    self.finished = False
    self.cancel.connect(self.cancel_task, type=Qt.DirectConnection)  # type: ignore[attr-defined]
    self.finish.connect(self.finish_task, type=Qt.DirectConnection)  # type: ignore[attr-defined]
    self.start.connect(self.start_task)

  def cancel_task(self) -> None:
    """
    Cancels the task.

    Explanation:
        This method sets the canceled attribute of the GenericTaskObject instance to True.

    Args:
        self: The GenericTaskObject instance.

    """
    self.logger.info('Cancelling task, id: %s', self.id)
    self.cancelled = True

  def start_task(self) -> None:
    """
    Starts the task.

    Explanation:
        This method sets the cancelled attribute to False and the started attribute to True.

    Args:
        self: The GenericTaskObject instance.

    """
    self.logger.info('Starting task, id: %s', self.id)
    self.cancelled = False
    self.started = True

  def cleanup(self) -> None:
    """
    Cleans up the task.

    Explanation:
        This method sets the cleaned attribute of the GenericTaskObject instance to True.

    Args:
        self: The GenericTaskObject instance.

    """
    self.logger.info('Cleaning up task, id: %s', self.id)
    self.cleaned = True

  def finish_task(self) -> None:
    """
    Finish up the task.

    Args:
        self: The instance of the class.
    """

    self.logger.info('Finishing up the task, id: %s', self.id)
    self.finished = True
