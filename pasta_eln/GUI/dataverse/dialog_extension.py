#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dialog_extension.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6 import QtCore
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog


class DialogExtension(QDialog):
  closed = QtCore.Signal()

  def __init__(self) -> None:
    super().__init__()

  def closeEvent(self, close_event: QCloseEvent) -> None:
    super().closeEvent(close_event)
    self.closed.emit()
