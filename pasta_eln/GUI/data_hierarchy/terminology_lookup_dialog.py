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
import textwrap
from asyncio import get_event_loop
from os import getcwd
from os.path import dirname, join, realpath
from typing import Callable

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QMessageBox, QWidget

from pasta_eln.GUI.data_hierarchy.terminology_lookup_dialog_base import Ui_TerminologyLookupDialogBase
from pasta_eln.GUI.data_hierarchy.terminology_lookup_service import TerminologyLookupService


class TerminologyLookupDialog(Ui_TerminologyLookupDialogBase):
  """ Terminology Lookup Dialog class which handles the IRI lookup online """

  def __init__(self,
               default_lookup_term: str | None = None,
               accepted_callback: Callable[[], None] = None) -> None:  # type: ignore[assignment]
    """
    Initializes the dialog
    Args:
      default_lookup_term (str): Default search term to be used by the terminology lookup service.
      accepted_callback (Callable[[], None]): Accepted button parent callback.
    """
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.accepted_callback: Callable[[], None] = accepted_callback
    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    super().setupUi(self.instance)
    self.terminology_lookup_service = TerminologyLookupService()

    # User selected urls
    self.selected_iris: list[str] = []

    # Load the icon images for lookup portals
    current_path = realpath(join(getcwd(), dirname(__file__)))
    resources_path = join(current_path, "../../Resources/Icons")
    self.icons_pixmap = {
      "wikipedia": QPixmap(join(resources_path, "wikipedia.png")).scaledToWidth(50),
      "wikidata": QPixmap(join(resources_path, "wikidata.png")).scaledToWidth(50),
      "ontology_lookup_service": QPixmap(join(resources_path, "ols.png")).scaledToWidth(50),
      "tib_terminology_service": QPixmap(join(resources_path, "tib.png")).scaledToWidth(50),
    }

    # Hide the error console and connect the slot
    self.errorConsoleTextEdit.hide()
    self.errorConsolePushButton.clicked.connect(lambda:
                                                self.errorConsoleTextEdit
                                                .setVisible(not self.errorConsoleTextEdit.isVisible()))
    self.buttonBox.accepted.connect(self.set_selected_iris)
    self.buttonBox.accepted.connect(self.accepted_callback)
    self.terminologySearchPushButton.clicked.connect(self.terminology_search_button_clicked)
    self.terminologyLineEdit.setText(default_lookup_term)

  def show(self) -> None:
    """
    Displays the dialog

    Returns: None

    """
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.instance.show()

  def add_scroll_area_entry(self,
                            pixmap: QPixmap,
                            checkbox_text: str,
                            checkbox_tooltip: str) -> None:
    """
    Adds an entry to the scroll area of terminology lookup dialog.
    Entry consists of a checkbox and a label
    The search result is added as a checkbox and a label (icon) to the end of the entry
    Args:
      pixmap (QPixmap): Icon image to be added
      checkbox_text (str): Text to be added to the checkbox
      checkbox_tooltip (str): Tooltip for the checkbox

    Returns: Nothing

    """
    self.logger.info("Adding entry to scroll area, checkbox_text: %s", checkbox_text)
    # Set up the layout for the entry with check box and label
    entry_layout = QHBoxLayout()
    check_box = QCheckBox(checkbox_text)
    check_box.setToolTip(checkbox_tooltip)
    entry_layout.addWidget(check_box)
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

  def set_selected_iris(self) -> None:
    """
      Gets the IRIs from the checked QCheckBoxes of the scroll area and appends them to the list of selected IRIs
      Tooltip of the checked QCheckBox holds the IRI information
    """
    self.selected_iris.clear()
    for widget_pos in range(self.scrollAreaContentsVerticalLayout.count()):
      check_box = self.scrollAreaContentsVerticalLayout.itemAt(widget_pos).widget().findChildren(QCheckBox)[0]
      if check_box.isChecked():
        self.selected_iris.append(check_box.toolTip())
    self.logger.info("Set IRIs: %s", self.selected_iris)

  def terminology_search_button_clicked(self) -> None:
    """
      terminologySearchPushButton Button click event handler which initiates
      the terminology search, retrieve the results and updated the scroll area
    Returns: Nothing

    """
    self.reset_ui()
    search_term = self.terminologyLineEdit.text()
    if not search_term or search_term.isspace():
      self.logger.warning("Enter non null search term!")
      QMessageBox.warning(self.instance, "Error", "Enter non null search term!")
      return

    self.logger.info("Terminology search initiated for term: %s..", search_term)
    self.searchProgressBar.setValue(5)
    event_loop = get_event_loop()
    if lookup_results := event_loop.run_until_complete(
        self.terminology_lookup_service.do_lookup(search_term)):
      for service in lookup_results:
        for result in service['results']:
          self.add_scroll_area_entry(self.icons_pixmap[service['name']],
                                     textwrap.fill(result['information'], width=100, max_lines=2),
                                     result['iri'])
          self.searchProgressBar.setValue((100 - self.searchProgressBar.value()) / 2)
    if self.terminology_lookup_service.http_client.session_request_errors:
      self.errorConsoleTextEdit.setText('\n'.join(self.terminology_lookup_service.http_client.session_request_errors))
      self.errorConsoleTextEdit.setVisible(True)
    self.searchProgressBar.setValue(100)

  def reset_ui(self) -> None:
    """
    Resets the UI elements for the dialog
    Returns:

    """
    self.logger.info("Resetting UI..")
    self.searchProgressBar.setValue(0)
    self.clear_scroll_area()
    self.errorConsoleTextEdit.clear()
    self.errorConsoleTextEdit.setVisible(False)
    self.selected_iris.clear()


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)
  ui = TerminologyLookupDialog()
  ui.instance.show()
  sys.exit(app.exec())
