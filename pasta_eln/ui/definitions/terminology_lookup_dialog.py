""" Terminology Lookup Dialog class which handles the IRI lookup online """
#  PASTA-ELN and all its sub-parts are covered by the MIT license
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: terminology_lookup_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information
import asyncio
import textwrap
from typing import Callable
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QMessageBox, QWidget
from pasta_eln.ui.definitions.dialog_base import Ui_TerminologyLookupDialogBase   # type: ignore[attr-defined]
from pasta_eln.ui.definitions.terminology_lookup_service import TerminologyLookupService


class TerminologyLookupDialog(Ui_TerminologyLookupDialogBase):
  """ Terminology Lookup Dialog class which handles the IRI lookup online """

  def __init__(self, defaultLookupTerm: str | None = None,
               acceptedCallback: Callable[[list[str]], None] = None) -> None:       # type: ignore[assignment]
    """
    Initializes the dialog
    Args:
      default_lookup_term (str): Default search term to be used by the terminology lookup service
      accepted_callback (Callable[[], None]): Accepted button parent callback
    """
    self.acceptedCallback: Callable[[list[str]], None] = acceptedCallback
    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    super().setupUi(self.instance)
    self.terminologyLookupService = TerminologyLookupService()
    # User selected urls
    self.selectedIris: list[str] = []
    # Load the icon images for lookup portals
    self.iconsPixmap = self.terminologyLookupService.getIconDict()
    # Hide the error console and button, constantly
    self.errorConsole.hide()
    self.errorConsoleBtn.hide()
    # self.errorConsoleBtn.clicked.connect(lambda: self.errorConsole.setVisible(not self.errorConsole.isVisible()))
    self.buttonBox.accepted.connect(self.setSelectedIris)
    self.buttonBox.accepted.connect(lambda: self.acceptedCallback(self.selectedIris))
    self.terminologySearchPushButton.clicked.connect(self.terminologySearchButtonClicked)
    self.terminologyLineEdit.setText(defaultLookupTerm)
    self.checkBox = QCheckBox()
    self.terminologySearchButtonClicked()


  def show(self) -> None:
    """ Displays the dialog """
    self.instance.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    self.instance.show()
    return


  def addScrollAreaEntry(self, pixmap: QPixmap, checkboxText: str, checkboxTooltip: str) -> None:
    """
    Adds an entry to the scroll area of terminology lookup dialog
    Entry consists of a checkbox and a label
    The search result is added as a checkbox and a label (icon) to the end of the entry
    Args:
      pixmap (QPixmap): Icon image to be added
      checkboxText (str): Text to be added to the checkbox
      checkboxTooltip (str): Tooltip for the checkbox
    """
    # Set up the layout for the entry with check box and label
    entryLayout = QHBoxLayout()
    self.checkBox = QCheckBox(checkboxText)
    self.checkBox.setToolTip(checkboxTooltip)
    entryLayout.addWidget(self.checkBox)
    entryLayout.addStretch(1)
    entryLayout.addWidget(QLabel(pixmap=pixmap))
    # Create a widget for the entry with the created layout
    entryWidget = QWidget()
    entryWidget.setLayout(entryLayout)
    self.scrollAreaContentsVerticalLayout.addWidget(entryWidget)
    return


  def clearScrollArea(self) -> None:
    """ Clears the scroll area by removing all the widgets """
    for widgetPos in reversed(range(self.scrollAreaContentsVerticalLayout.count())):
      self.scrollAreaContentsVerticalLayout.itemAt(widgetPos).widget().setParent(None)
    return


  def setSelectedIris(self) -> None:
    """
    Gets the IRIs from the checked QCheckBoxes of the scroll area and appends them to the list of selected IRIs
    Tooltip of the checked QCheckBox holds the IRI information
    """
    self.selectedIris.clear()
    for widgetPos in range(self.scrollAreaContentsVerticalLayout.count()):
      checkBox = self.scrollAreaContentsVerticalLayout.itemAt(widgetPos).widget().findChildren(QCheckBox)[0]
      if checkBox.isChecked():
        self.selectedIris.append(checkBox.toolTip())
    return


  def terminologySearchButtonClicked(self) -> None:
    """
    terminologySearchPushButton Button click event handler which initiates
    the terminology search, retrieve the results and updated the scroll area
    """
    self.resetUi()
    searchTerm = self.terminologyLineEdit.text()
    if not searchTerm or searchTerm.isspace():
      QMessageBox.warning(self.instance, 'Error', 'Enter non null search term!',
                          QMessageBox.StandardButton.NoButton, QMessageBox.StandardButton.Ok)
      return
    self.searchProgressBar.setValue(5)
    eventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(eventLoop)
    if lookupResults := eventLoop.run_until_complete(self.terminologyLookupService.doLookup(searchTerm)):
      for service in lookupResults:
        for result in service['results']:
          self.addScrollAreaEntry(self.iconsPixmap[service['name']],
                                     textwrap.fill(result['information'], width=100, max_lines=2),
                                     result['iri'])
          self.searchProgressBar.setValue((100 - self.searchProgressBar.value()) / 2)
    self.searchProgressBar.setValue(100)
    return


  def resetUi(self) -> None:
    """ Resets the UI elements for the dialog """
    self.searchProgressBar.setValue(0)
    self.clearScrollArea()
    self.errorConsole.clear()
    self.errorConsole.setVisible(False)
    self.selectedIris.clear()
    return


if __name__ == '__main__':
  import sys
  app = QtWidgets.QApplication(sys.argv)
  ui = TerminologyLookupDialog('Project')
  ui.instance.show()
  sys.exit(app.exec())
