""" Represents QT dialog extension. """

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
  """
  Represents a dialog extension.

  Explanation:
      This class represents a dialog extension and provides a closeEvent method to handle the close event.
      It emits a closed signal when the dialog is closed.

  Args:
      None

  Returns:
      None
  """
  closed = QtCore.Signal()

  def closeEvent(self, close_event: QCloseEvent) -> None:
    """
    Overrides the close event method.

    Explanation:
        This method is called when the close event is triggered.
        It emits a closed signal.

    Args:
        close_event (QCloseEvent): The close event.
    """
    super().closeEvent(close_event)
    self.closed.emit()
