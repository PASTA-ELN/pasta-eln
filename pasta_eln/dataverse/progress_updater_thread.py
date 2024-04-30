""" Class for simulating progress updates in the background. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: progress_updater_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import random
import time

from PySide6 import QtCore
from PySide6.QtCore import QThread


class ProgressUpdaterThread(QThread):
  """
   Class for simulating progress updates in the background.

   Explanation:
       This class represents a thread for simulating progress updates in the background.
       It inherits from the QThread class and provides methods for simulating progress updates and emitting signals.
   """
  progress_update = QtCore.Signal(int)
  cancel = QtCore.Signal()
  finalize = QtCore.Signal()
  end = QtCore.Signal()

  def __init__(self) -> None:
    """
    Initialize the progress updater thread.

    Args:
        self: The instance of the progress updater thread.
    """
    super().__init__()
    self.cancelled = False
    self.finalized = False
    self.cancel.connect(self.cancel_progress)
    self.finalize.connect(self.finalize_progress)

  def run(self) -> None:
    """
    Simulates progress updates and emits progress signals until completion or interruption.

    Explanation:
        This method simulates progress updates in the background, emitting signals for each progress step.
        It emits progress updates until the task is cancelled or finalized.
        It waits for a total of 120 seconds before emitting the final progress signal and exiting.
    """
    # Simulate progress updates in the background for around 20 seconds
    for progress in range(1, 98, random.randint(1, 5)):
      if self.cancelled or self.finalized:
        break
      self.progress_update.emit(progress)
      time.sleep(1)

    # Wait for 100 seconds more before emitting the final progress
    for _ in range(1, 100):
      if self.cancelled or self.finalized:
        break
      time.sleep(1)
    if not self.cancelled:
      self.progress_update.emit(100)
    self.end.emit()

  def cancel_progress(self) -> None:
    """
    Sets the flag to indicate that the progress should be cancelled.

    Explanation:
        This method sets the 'finish' flag to True, indicating that the progress should be terminated.
    """
    self.cancelled = True

  def finalize_progress(self) -> None:
    """
    Finalizes the progress update.

    Explanation:
        This function sets the 'finalized' attribute to True, indicating that the progress update is complete.
    """
    self.finalized = True
