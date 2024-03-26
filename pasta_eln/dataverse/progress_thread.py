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

from PySide6.QtCore import QThread


class ProgressThread(QThread):
  progress_update = None

  def __init__(self)-> None:
    super().__init__()
    self.finished = False

  def run(self) -> None:
    if self.progress_update is None:
      return
    for progress in range(1, 100, random.randint(1, 5)):
      time.sleep(1)
      if self.finished:
        break
      self.progress_update.emit(progress)
    self.progress_update.emit(100)
    self.exit()
