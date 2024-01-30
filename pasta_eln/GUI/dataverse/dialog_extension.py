#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dialog_extension.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog


class DialogExtension(QDialog):
  closed = Signal()

  def __init__(self):
    super().__init__()

  def closeEvent(self, arg__1):
    super().closeEvent(arg__1)
    self.closed.emit()
