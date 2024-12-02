#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_dialog_extension.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication

from pasta_eln.GUI.dataverse.dialog_extension import DialogExtension


@pytest.fixture(scope="session")
def qapp():
  return QApplication([])


@pytest.mark.skip(
  reason="Disabled until the issue with instantiating DialogExtension is resolved")
class TestDataverseDialogExtension(object):
  @pytest.mark.parametrize("test_id", [
    ("happy_path"),
    ("edge_case_no_event_data"),  # Simulating an edge case if possible
    # Error cases are not directly applicable here since the method and class are straightforward
  ])
  def test_closeEvent_emits_closed_signal(self, qapp, mocker, test_id):
    # Arrange
    mocker.patch("PySide6.QtWidgets.QDialog")
    dialog = DialogExtension()
    closed_emitted = False

    def on_closed():
      nonlocal closed_emitted
      closed_emitted = True

    dialog.closed.connect(on_closed)

    if test_id == "happy_path":
      close_event = QCloseEvent()
    elif test_id == "edge_case_no_event_data":
      # This is a hypothetical edge case; in reality, QCloseEvent doesn't require additional data
      close_event = QCloseEvent()

    # Act
    dialog.closeEvent(close_event)

    # Assert
    assert closed_emitted, f"Closed signal was not emitted for {test_id}"
