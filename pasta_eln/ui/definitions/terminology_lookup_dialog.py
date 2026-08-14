"""Dialog for selecting terminology IRIs from online lookup services."""
import asyncio
import textwrap
from collections.abc import Callable
from enum import Enum, auto
from typing import Any
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar,
                               QPushButton, QScrollArea, QTextEdit, QVBoxLayout, QWidget)
from pasta_eln.ui.definitions.terminology_lookup_service import TerminologyLookupService
from pasta_eln.ui.gui_style import Label
from pasta_eln.ui.widget import SPACE, Button, ButtonStyle


class TerminologyLookupDialog(QDialog):
  """Search terminology services and return the IRIs selected by the user."""

  def __init__(self, defaultLookupTerm: str | None = None,
               acceptedCallback: Callable[[list[str]], None] | None = None) -> None:
    super().__init__()
    self.comm: Any = None
    self.acceptedCallback = acceptedCallback
    self.terminologyLookupService = TerminologyLookupService()
    self.selectedIris: list[str] = []
    self.resultCheckboxes: list[QCheckBox] = []
    self.checkBox: QCheckBox | None = None
    self.iconsPixmap = self.terminologyLookupService.getIconDict()
    self.setWindowTitle('Terminology lookup')
    self.setModal(True)
    self.setMinimumSize(720, 560)

    mainLayout = QVBoxLayout(self)
    mainLayout.setContentsMargins(SPACE.M, SPACE.M, SPACE.M, SPACE.M)
    mainLayout.setSpacing(SPACE.S)
    Label('Terminology lookup', 'h1', mainLayout)
    Label('Search wikis and ontologies, then select one or more matching identifiers.', 'h3', mainLayout)

    searchLayout = QHBoxLayout()
    self.terminologyLineEdit = QLineEdit(defaultLookupTerm or '', clearButtonEnabled=True)
    self.terminologyLineEdit.setPlaceholderText('Search definitions in wikis and ontologies')
    self.terminologyLineEdit.returnPressed.connect(lambda: self.execute(Command.SEARCH))
    searchLayout.addWidget(self.terminologyLineEdit)
    searchButton = QPushButton('Search')
    searchButton.clicked.connect(lambda: self.execute(Command.SEARCH))
    searchLayout.addWidget(searchButton)
    mainLayout.addLayout(searchLayout)

    self.searchProgressBar = QProgressBar()
    self.searchProgressBar.setRange(0, 100)
    mainLayout.addWidget(self.searchProgressBar)

    self.scrollArea = QScrollArea(widgetResizable=True)
    self.scrollAreaWidgetContents = QWidget()
    self.scrollAreaContentsVerticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
    self.scrollAreaContentsVerticalLayout.setContentsMargins(SPACE.S, SPACE.S, SPACE.S, SPACE.S)
    self.scrollAreaContentsVerticalLayout.setSpacing(SPACE.S)
    self.scrollAreaContentsVerticalLayout.addStretch()
    self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    mainLayout.addWidget(self.scrollArea, stretch=1)

    self.errorConsole = QTextEdit(readOnly=True)
    self.errorConsole.hide()
    mainLayout.addWidget(self.errorConsole)

    footer = QHBoxLayout()
    footer.addStretch()
    Button('Cancel', self, Command.CANCEL, footer)
    Button('Use selected', self, Command.ACCEPT, footer, style=ButtonStyle.HIGHLIGHTED)
    mainLayout.addLayout(footer)

    if defaultLookupTerm:
      self.terminologySearchButtonClicked()

  def addScrollAreaEntry(self, pixmap: QPixmap, checkboxText: str, checkboxTooltip: str) -> None:
    """Add one searchable terminology result."""
    entryWidget = QWidget()
    entryLayout = QHBoxLayout(entryWidget)
    entryLayout.setContentsMargins(SPACE.S, SPACE.S, SPACE.S, SPACE.S)
    self.checkBox = QCheckBox(checkboxText)
    self.checkBox.setToolTip(checkboxTooltip)
    entryLayout.addWidget(self.checkBox, stretch=1)
    entryLayout.addWidget(QLabel(pixmap=pixmap))
    self.scrollAreaContentsVerticalLayout.insertWidget(self.scrollAreaContentsVerticalLayout.count() - 1, entryWidget)
    self.resultCheckboxes.append(self.checkBox)

  def clearScrollArea(self) -> None:
    """Remove all current search results while preserving the layout stretch."""
    while self.scrollAreaContentsVerticalLayout.count() > 1:
      item = self.scrollAreaContentsVerticalLayout.takeAt(0)
      if item is not None and (widget := item.widget()):
        widget.deleteLater()
    self.resultCheckboxes.clear()

  def setSelectedIris(self) -> None:
    """Collect the IRIs represented by checked search results."""
    self.selectedIris = []
    for checkBox in self.resultCheckboxes:
      if checkBox.isChecked():
        self.selectedIris.append(checkBox.toolTip())

  def terminologySearchButtonClicked(self) -> None:
    """Look up the entered term and populate the result list."""
    self.resetUi()
    searchTerm = self.terminologyLineEdit.text().strip()
    if not searchTerm:
      QMessageBox.warning(self, 'Terminology lookup', 'Enter a search term.')
      return
    self.searchProgressBar.setValue(5)
    eventLoop = asyncio.new_event_loop()
    try:
      lookupResults = eventLoop.run_until_complete(self.terminologyLookupService.doLookup(searchTerm))
    finally:
      eventLoop.close()
    results = [(service, result) for service in lookupResults or [] for result in service['results']]
    for index, (service, result) in enumerate(results, start=1):
      self.addScrollAreaEntry(self.iconsPixmap[service['name']],
                              textwrap.fill(result['information'], width=100, max_lines=2), result['iri'])
      self.searchProgressBar.setValue(5 + int(95 * index / max(1, len(results))))
    self.searchProgressBar.setValue(100)

  def resetUi(self) -> None:
    """Reset result and progress state before a search."""
    self.searchProgressBar.setValue(0)
    self.clearScrollArea()
    self.errorConsole.clear()
    self.selectedIris.clear()

  def execute(self, command: 'Command') -> None:
    """Handle dialog actions."""
    if command is Command.SEARCH:
      self.terminologySearchButtonClicked()
    elif command is Command.CANCEL:
      self.reject()
    elif command is Command.ACCEPT:
      self.setSelectedIris()
      if self.acceptedCallback is not None:
        self.acceptedCallback(self.selectedIris)
      self.accept()


class Command(Enum):
  """Commands available in the terminology lookup dialog."""
  SEARCH = auto()
  CANCEL = auto()
  ACCEPT = auto()
