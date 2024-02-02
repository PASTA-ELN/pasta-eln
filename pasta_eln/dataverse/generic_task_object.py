#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: generic_task_object.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal


class GenericTaskObject(QObject):
  cancel = QtCore.Signal()
  start = QtCore.Signal()
  finished = QtCore.Signal()

  def __init__(self):
    super().__init__()
    self.cancelled = False
    self.started = False
    self.cleaned = False
    self.cancel.connect(lambda: self.cancel_task())
    self.start.connect(self.start_task)

  def cancel_task(self):
    self.cancelled = True

  def start_task(self):
    self.cancelled = False
    self.started = True

  def cleanup(self):
    self.cleaned = True
