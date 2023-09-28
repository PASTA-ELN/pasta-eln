""" Terminology Lookup Dialog class which handles the IRI lookup online """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: terminology_lookup_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
import uuid

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QCheckBox

from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog_base import Ui_TerminologyLookupDialogBase


class TerminologyLookupDialog(Ui_TerminologyLookupDialogBase):
  """ Terminology Lookup Dialog class which handles the IRI lookup online """

  def __init__(self) -> None:
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    super().setupUi(self.instance)

  def show(self) -> None:
    """
    Displays the dialog

    Returns: None

    """
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.instance.show()

  def add_scroll_area_entry(self,
                            pixmap: QPixmap,
                            checkbox_text: str) -> None:
    """
    Adds an entry to the scroll area of terminology lookup dialog.
    Entry consists of a checkbox and a label
    The search result is added as a checkbox and a label (icon) to the end of the entry
    Args:
      pixmap (QPixmap): Icon image to be added
      checkbox_text (str): Text to be added to the checkbox

    Returns: Nothing

    """
    self.logger.info("Adding entry to scroll area, checkbox_text: %s", checkbox_text)
    # Set up the layout for the entry with check box and label
    entry_layout = QHBoxLayout()
    entry_layout.addWidget(QCheckBox(checkbox_text))
    entry_layout.addStretch(1)
    entry_layout.addWidget(QLabel(pixmap=pixmap))  # type: ignore[call-overload]

    # Create a widget for the entry with the created layout
    entry_widget = QWidget()
    entry_widget.setLayout(entry_layout)

    self.scrollAreaContentsVerticalLayout.addWidget(entry_widget)

  def clear_scroll_area(self) -> None:
    """
      Clears the scroll area by removing all the widgets

    Returns: Nothing

    """
    self.logger.info("Clearing scroll area..")
    for widget_pos in reversed(range(self.scrollAreaContentsVerticalLayout.count())):
      self.scrollAreaContentsVerticalLayout.itemAt(widget_pos).widget().setParent(None)


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)
  TerminologyLookupDialogBase = TerminologyLookupDialog()
  TerminologyLookupDialogBase.show()
  tibPixmap = QPixmap()
  baTIB = QByteArray.fromBase64(
    b'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')
  tibPixmap.loadFromData(baTIB)
  for i in range(12):
    TerminologyLookupDialogBase.add_scroll_area_entry(tibPixmap,
                                                      f"Test {uuid.uuid4()}{uuid.uuid4()}{uuid.uuid4()}{uuid.uuid4()}")
  TerminologyLookupDialogBase.terminologySearchPushButton.clicked.connect(TerminologyLookupDialogBase.clear_scroll_area)
  sys.exit(app.exec())
