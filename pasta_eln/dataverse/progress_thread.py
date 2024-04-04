#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: progress_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import random
import time

from PySide6 import QtCore
from PySide6.QtCore import QThread


class ProgressThread(QThread):
  progress_update = QtCore.Signal(int)
  cancel = QtCore.Signal()

  def __init__(self)-> None:
    super().__init__()
    self.finished = False
    self.cancel.connect(self.cancel_progress)

  def run(self) -> None:
    progress = 0
    step = random.randint(1, 5)
    while not self.finished:
      progress += step if (progress + step < 98) else 0
      self.progress_update.emit(progress)
      time.sleep(1)
    self.progress_update.emit(100)
    for progress in range(1, 98, random.randint(1, 5)):
      time.sleep(1)
      if self.finished:
        break
      self.progress_update.emit(progress)
    self.progress_update.emit(100)
    self.exit()

  def cancel_progress(self):
    self.finished = True
