""" Terminology Lookup Dialog class which handles the IRI lookup online """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: terminology_lookup_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import textwrap
from asyncio import get_event_loop
from typing import Callable
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QMessageBox, QWidget
from pasta_eln.GUI.definitions.dialog_base import Ui_TerminologyLookupDialogBase  # type: ignore[attr-defined]
from pasta_eln.GUI.definitions.terminology_lookup_service import TerminologyLookupService


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
    self.accepted_callback: Callable[[], None] = accepted_callback
    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    super().setupUi(self.instance)
    self.terminology_lookup_service = TerminologyLookupService()
    # User selected urls
    self.selected_iris: list[str] = []
    # Load the icon images for lookup portals
    self.icons_pixmap = self.terminology_lookup_service.getIconDict()
    # Hide the error console and connect the slot
    self.errorConsole.hide()
    self.errorConsoleBtn.clicked.connect(lambda: self.errorConsole.setVisible(not self.errorConsole.isVisible()))
    self.buttonBox.accepted.connect(self.set_selected_iris)
    self.buttonBox.accepted.connect(lambda: self.accepted_callback(self.selected_iris))
    self.terminologySearchPushButton.clicked.connect(self.terminology_search_button_clicked)
    self.terminologyLineEdit.setText(default_lookup_term)
    self.terminology_search_button_clicked()


  def show(self) -> None:
    """ Displays the dialog """
    self.instance.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    self.instance.show()
    return


  def add_scroll_area_entry(self, pixmap: QPixmap, checkbox_text: str, checkbox_tooltip: str) -> None:
    """
    Adds an entry to the scroll area of terminology lookup dialog.
    Entry consists of a checkbox and a label
    The search result is added as a checkbox and a label (icon) to the end of the entry
    Args:
      pixmap (QPixmap): Icon image to be added
      checkbox_text (str): Text to be added to the checkbox
      checkbox_tooltip (str): Tooltip for the checkbox
    """
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
    return


  def clear_scroll_area(self) -> None:
    """ Clears the scroll area by removing all the widgets """
    for widget_pos in reversed(range(self.scrollAreaContentsVerticalLayout.count())):
      self.scrollAreaContentsVerticalLayout.itemAt(widget_pos).widget().setParent(None)
    return


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
    return


  def terminology_search_button_clicked(self) -> None:
    """
    terminologySearchPushButton Button click event handler which initiates
    the terminology search, retrieve the results and updated the scroll area
    """
    self.reset_ui()
    search_term = self.terminologyLineEdit.text()
    if not search_term or search_term.isspace():
      QMessageBox.warning(self.instance, 'Error', 'Enter non null search term!',
                          QMessageBox.StandardButton.NoButton, QMessageBox.StandardButton.Ok)
      return
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
    self.searchProgressBar.setValue(100)
    return


  def reset_ui(self) -> None:
    """ Resets the UI elements for the dialog """
    self.searchProgressBar.setValue(0)
    self.clear_scroll_area()
    self.errorConsole.clear()
    self.errorConsole.setVisible(False)
    self.selected_iris.clear()
    return


if __name__ == '__main__':
  import sys
  app = QtWidgets.QApplication(sys.argv)
  ui = TerminologyLookupDialog('Project')
  ui.instance.show()
  sys.exit(app.exec())
