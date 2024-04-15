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

  def __init__(self) -> None:
    """
    Initializes the ProgressUpdaterThread instance with default values and connects the cancel signal.

    Explanation:
        Sets the 'finished' attribute to False and connects the 'cancel' signal to the 'cancel_progress' method.
    """
    super().__init__()
    self.finished = False
    self.cancel.connect(self.cancel_progress)

  def run(self) -> None:
    """
    Simulates progress updates and emits progress signals until completion or interruption.

    Explanation:
        This method simulates progress updates in the background, emitting signals for each progress step.
        It waits for a total of 120 seconds before emitting the final progress signal and exiting.
    """
    # Simulate progress updates in the background for around 20 seconds
    for progress in range(1, 98, random.randint(1, 5)):
      if self.finished:
        break
      self.progress_update.emit(progress)
      time.sleep(1)

    # Wait for 100 seconds more before emitting the final progress
    for _ in range(1, 100):
      if self.finished:
        break
      time.sleep(1)
    self.progress_update.emit(100)
    self.exit()

  def cancel_progress(self) -> None:
    """
    Sets the flag to indicate that the progress should be cancelled.

    Explanation:
        This method sets the 'finished' flag to True, indicating that the progress should be terminated.
    """
    self.finished = True
