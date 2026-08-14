"""Document list views and their table-specific commands."""
import csv
import logging
from enum import Enum
from pathlib import Path
from typing import Any
import pandas as pd
from PySide6.QtCore import QByteArray, QItemSelection, QItemSelectionModel, QModelIndex, QSize, Qt, Slot
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QListWidget, QListWidgetItem, QMenu, QMessageBox,
                               QTableView, QVBoxLayout, QWidget)
from pasta_eln.backend_worker.worker import Task
from pasta_eln.misc_tools import callAddOn, isDocID
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Action
from pasta_eln.ui.table.filter_row import FilterRow
from pasta_eln.ui.table.pandas_table_model import PandasTableModel
from pasta_eln.ui.table.table_header import TableHeader
from pasta_eln.ui.gui_style import SPACE, Action, Button, ButtonStyle, Widget
from pasta_eln.ui.workplan_creator.workplan_creator_dialog import WorkplanCreatorDialog


class TableView(Widget):
  """Displays a document list with selection, view, and export commands."""

  def __init__(self, comm: Communicate, docType: str):
    """ Initializes TableView
    Args:
      comm (Communicate): The communication object to obtain data and send commands to
      docType (str): The type of documents to display.
    """
    super().__init__()
    self.comm = comm
    self.docType = docType
    self.data = pd.DataFrame()                                               # raw data received from database
    self.tableData = pd.DataFrame()                                             # data to display in the table
    self.showAll = self.comm.configuration['GUI']['showHidden'] == 'Yes'
    self.filterRows: list[FilterRow] = []
    self.detailsDocID = ''
    self.reloadComboBoxFlag = True                           # prevent combobox reloads after sub-type changes
    self.galleryDocumentIds: set[str] = set()
    self._stopSequentialEdit = False

    # Toolbar
    self.buttonbarW = QWidget(self)
    self.buttonbarL = QHBoxLayout(self.buttonbarW)
    self.buttonbarL.setContentsMargins(SPACE.M, 10, SPACE.M, 10)
    self.subTypeCombo = QComboBox()
    self.subTypeCombo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    self.subTypeCombo.setPlaceholderText('Select Subtype')
    self.subTypeCombo.currentTextChanged.connect(self.onSubTypeChanged)
    self.buttonbarL.addWidget(self.subTypeCombo)
    self.buttonbarL.addStretch()
    self.newEntryButton = Button('New Entry', self, Command.NEW_ENTRY, self.buttonbarL, icon='ri.add-fill',
                                 style=ButtonStyle.HIGHLIGHTED)
    self.actionButton   = Button('Actions',   self, layout=self.buttonbarL, icon='ri.task-line',
                               style=ButtonStyle.PRIMARY)
    self.actionMenu = QMenu(self)
    self.actionButton.setMenu(self.actionMenu)
    self.toggleSelectionAction = Action('Toggle selection', self, Command.TOGGLE_SELECTION, self.actionMenu)
    self.actionMenu.addSeparator()
    self.groupEditAction = Action('Group edit', self, Command.GROUP_EDIT, self.actionMenu)
    self.sequentialEditAction = Action('Sequential edit', self, Command.SEQUENTIAL_EDIT, self.actionMenu)
    self.toggleHiddenAction = Action('Hide/show selected', self, Command.TOGGLE_HIDDEN, self.actionMenu)
    self.rerunExtractorsAction = Action('Rerun extractors', self, Command.RERUN_EXTRACTORS, self.actionMenu)
    self.deleteAction = Action('Delete', self, Command.DELETE, self.actionMenu)

    self.viewButton = Button('View', self, layout=self.buttonbarL, icon='ri.eye-line', style=ButtonStyle.PRIMARY)
    self.viewMenu = QMenu(self)
    self.viewButton.setMenu(self.viewMenu)
    Action('Add filter', self, Command.ADD_FILTER, self.viewMenu)
    self.showHiddenAction = Action('Show hidden rows', self, Command.SHOW_HIDDEN, self.viewMenu)
    self.galleryAction = Action('Gallery view', self, Command.TOGGLE_GALLERY, self.viewMenu)
    self.galleryAction.setVisible(False)

    self.moreButton = Button('More', self, layout=self.buttonbarL, icon='ri.more-fill', style=ButtonStyle.PRIMARY)
    self.moreMenu = QMenu(self)
    self.moreButton.setMenu(self.moreMenu)
    Action('Export CSV', self, Command.EXPORT_CSV, self.moreMenu)
    self.moreMenu.addSeparator()
    self.tableAddOnMenu = self.moreMenu.addMenu('Table add-ons')
    self.moreMenu.addSeparator()
    self.changeColumnsAction = Action('Change list columns', self, Command.CHANGE_COLUMNS, self.moreMenu)
    self.paintTableAddOnsMenu()

    # Filter rows live directly above the document table.
    self.filterW = QWidget()
    self.filterL = QVBoxLayout(self.filterW)
    self.filterL.setContentsMargins(SPACE.M, 0, SPACE.M, 0)
    self.filterL.setSpacing(SPACE.S)
    self.filterW.hide()

    # Table and gallery occupy the same content area.
    self.table = QTableView()
    self.table.clicked.connect(self.onCellClicked)
    self.table.doubleClicked.connect(self.onCellDoubleClicked)
    self.table.setAlternatingRowColors(True)
    self.table.horizontalHeader().setStretchLastSection(True)
    self.table.horizontalHeader().setSectionsMovable(True)
    self.table.horizontalHeader().setSortIndicatorShown(True)
    self.table.verticalHeader().hide()
    self.table.setSortingEnabled(True)
    self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    self.gallery = QListWidget()
    self.gallery.setViewMode(QListWidget.ViewMode.IconMode)
    self.gallery.setResizeMode(QListWidget.ResizeMode.Adjust)
    self.gallery.setMovement(QListWidget.Movement.Static)
    self.gallery.setIconSize(QSize(180, 140))
    self.gallery.setGridSize(QSize(210, 190))
    self.gallery.setWordWrap(True)
    self.gallery.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
    self.gallery.itemClicked.connect(self.onGalleryItemClicked)
    self.gallery.itemDoubleClicked.connect(self.onGalleryItemDoubleClicked)
    self.gallery.hide()

    self.tableW = QWidget()
    self.tableL = QVBoxLayout(self.tableW)
    self.tableL.setContentsMargins(SPACE.M, 0, SPACE.M, 0)
    self.tableL.addWidget(self.table)
    self.tableL.addWidget(self.gallery)

    self.mainL = QVBoxLayout(self)
    self.mainL.setContentsMargins(0, 0, 0, 0)
    self.mainL.setSpacing(SPACE.S)
    self.mainL.addWidget(self.buttonbarW)
    self.mainL.addWidget(self.filterW)
    self.mainL.addWidget(self.tableW)

    self.comm.backendThread.worker.beSendTable.connect(self.onGetData)
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetGalleryDoc)
    self.comm.changeTable.connect(self.onTableChange)
    self.comm.stopSequentialEdit.connect(self.stopSequentialEdit)


  @Slot(str, str)
  def onTableChange(self, docType: str, projID: str) -> None:
    """React to table change requests.
    Args:
      docType (str): The type of documents to display.
      projID (str): The ID of the project.
    """
    if docType != self.docType:
      return
    if projID:
      self.comm.projectID = projID
    logging.debug('request table for %s, %s %s', self.docType, self.comm.projectID, self.showAll)
    self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)


  @Slot(pd.DataFrame, str)
  def onGetData(self, data: pd.DataFrame, docType: str) -> None:
    """React to table data requests.
    Args:
      data (pd.DataFrame): The table data.
      docType (str): The type of documents.
    """
    if docType == self.docType:
      self.data = data
      if self.detailsDocID and self.detailsDocID not in data.id.values:
        self.comm.changeDetails.emit('')
      self.paint()


  def paint(self) -> None:
    """Rebuild the list after data, filtering, or visibility changes."""
    if self.reloadComboBoxFlag and '/' not in self.docType:
      self.subTypeCombo.blockSignals(True)
      self.subTypeCombo.clear()
      docTypeKeys = [key for key in self.comm.docTypesTitles if key.startswith(self.docType)]
      titles = [self.comm.docTypesTitles[key]['title'] for key in docTypeKeys]
      self.subTypeCombo.setVisible(len(titles) > 1)
      self.subTypeCombo.addItems(titles)
      self.subTypeCombo.blockSignals(False)
    self.reloadComboBoxFlag = True

    self.tableData, documentIds = self.filteredTableData()
    model = PandasTableModel(self.tableData, documentIds)
    self.table.setModel(model)
    model.rowCheckChanged.connect(self.onRowCheckChanged)
    self.table.selectionModel().selectionChanged.connect(self.synchronizeSelectionAndCheckbox)
    self.table.resizeColumnsToContents()
    normalizeColumns(self.table)
    self.table.setColumnWidth(0, 30)

    self.galleryAction.setVisible(self.docType.startswith('measurement'))
    self.changeColumnsAction.setVisible(self.docType not in ('-', '_tags_'))
    self.showHiddenAction.setText('Hide hidden rows' if self.showAll else 'Show hidden rows')
    self.filterW.setVisible(bool(self.filterRows))
    if self.gallery.isVisible():
      self.paintGallery(documentIds)


  def paintTableAddOnsMenu(self) -> None:
    """Populate the table add-on submenu for the active project group."""
    addOns = self.comm.configuration['projectGroups'][self.comm.projectGroup].get('addOns', {}).get('table', {})
    for label, description in sorted(addOns.items(), key=lambda item: item[1].casefold()):
      Action(description, self, [Command.ADD_ON, label], self.tableAddOnMenu)
    self.tableAddOnMenu.setEnabled(bool(addOns))


  def paintGallery(self, documentIds: list[str]) -> None:
    """Show image cards and request their previews from the backend."""
    self.gallery.clear()
    self.galleryDocumentIds = set(documentIds)
    for row, docID in enumerate(documentIds):
      name = docID if self.tableData.empty else self.tableData.iloc[row, 0]
      item = QListWidgetItem(str(name))
      item.setData(Qt.ItemDataRole.UserRole, docID)
      self.gallery.addItem(item)
      self.comm.uiRequestDoc.emit(docID)


  def refresh(self) -> None:
    """Refresh the table data"""
    self.comm.changeTable.emit(self.docType, self.comm.projectID)
    if self.docType == 'x0':
      self.comm.changeSidebar.emit('redraw')


  def execute(self, command: Command | list[object]) -> None:
    """Handle commands from the table toolbar and its menus
    Args:
      command (Command | list[object]): The command to execute.
    """
    commandType = command if isinstance(command, Command) else command[0]
    payload = [] if isinstance(command, Command) else command[1:]
    selected = self.selectedDocumentIds()
    if commandType is Command.NEW_ENTRY:
      if self.docType == 'workflow/workplan':
        WorkplanCreatorDialog(self.comm).exec()
      else:
        self.comm.formDoc.emit({'type': [self.docType], '_projectID': self.comm.projectID})
      self.refresh()
    elif commandType is Command.TOGGLE_SELECTION:
      if self.gallery.isVisible():
        selectAll = len(self.gallery.selectedItems()) != self.gallery.count()
        for row in range(self.gallery.count()):
          self.gallery.item(row).setSelected(selectAll)
        return
      model = self.table.model()
      if isinstance(model, PandasTableModel):
        for row, checked in enumerate(model.checkedRows):
          model.checkRow(row, not checked)
    elif commandType is Command.GROUP_EDIT and selected:
      self.comm.formDoc.emit({'type': [self.docType], '_ids': selected})
      self.refresh()
    elif commandType is Command.SEQUENTIAL_EDIT:
      self._stopSequentialEdit = False
      for docID in selected:
        self.comm.formDoc.emit({'id': docID})
        if self._stopSequentialEdit:
          break
      self.refresh()
    elif commandType is Command.TOGGLE_HIDDEN:
      for docID in selected:
        self.comm.uiRequestTask.emit(Task.HIDE_SHOW, {'docID': docID})
      if selected:
        self.refresh()
    elif commandType is Command.RERUN_EXTRACTORS:
      if selected:
        self.comm.uiRequestTask.emit(Task.EXTRACTOR_RERUN, {'docIDs': selected, 'recipe': ''})
        self.refresh()
    elif commandType is Command.DELETE and selected:
      answer = QMessageBox.warning(self, 'Delete selected items', 'Delete the selected items?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
      if answer is QMessageBox.StandardButton.Yes:
        for docID in selected:
          self.comm.uiRequestTask.emit(Task.DELETE_DOC, {'docID': docID, 'stack': ''})
        self.refresh()
    elif commandType is Command.ADD_FILTER:
      filterRow = FilterRow(self)
      self.filterRows.append(filterRow)
      self.filterL.addWidget(filterRow)
      self.paint()
    elif commandType is Command.SHOW_HIDDEN:
      self.showAll = not self.showAll
      self.refresh()
    elif commandType is Command.TOGGLE_GALLERY:
      self.gallery.setVisible(not self.gallery.isVisible())
      self.table.setVisible(not self.gallery.isVisible())
      if self.gallery.isVisible():
        self.paintGallery(self.modelDocumentIds())
    elif commandType is Command.EXPORT_CSV:
      fileName = QFileDialog.getSaveFileName(self, 'Export list to CSV', str(Path.home()), '*.csv')[0]
      if not fileName:
        return
      if not fileName.endswith('.csv'):
        fileName += '.csv'
      self.tableData.to_csv(fileName, index=False, quoting=csv.QUOTE_ALL)
    elif commandType is Command.ADD_ON and payload:
      documentIds = self.modelDocumentIds()
      selectedRows = [row for row, docID in enumerate(documentIds) if not selected or docID in selected]
      data = self.tableData.iloc[selectedRows].copy()
      data.insert(0, 'docID', [documentIds[row] for row in selectedRows])
      callAddOn(str(payload[0]), self.comm, data, self)
    elif commandType is Command.CHANGE_COLUMNS:
      if TableHeader(self.comm, self.docType).exec():
        self.refresh()


  @Slot(dict)
  def onGetGalleryDoc(self, document: dict[str, Any]) -> None:
    """Handle requests for gallery document images

    Args:
      document (dict[str, Any]): The document data
    """
    docID = str(document.get('id', ''))
    image = document.get('image')
    if docID not in self.galleryDocumentIds or not isinstance(image, str) or ',' not in image:
      return
    imageData = QByteArray.fromBase64(image.split(',', 1)[1].encode())
    qimage = QImage.fromData(imageData)
    if qimage.isNull():
      return
    pixmap = QPixmap.fromImage(qimage).scaled(self.gallery.iconSize(), Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
    for row in range(self.gallery.count()):
      item = self.gallery.item(row)
      if item.data(Qt.ItemDataRole.UserRole) == docID:
        item.setIcon(QIcon(pixmap))
        break


  @Slot(QModelIndex)
  def onCellClicked(self, index: QModelIndex) -> None:
    """Handle cell click events

    Args:
      index (QModelIndex): The index of the clicked cell
    """
    model = self.table.model()
    if isinstance(model, PandasTableModel):
      docID = model.documentIds[index.row()]
      self.detailsDocID = docID
      self.comm.changeDetails.emit(docID)


  @Slot(QModelIndex)
  def onCellDoubleClicked(self, index: QModelIndex) -> None:
    """Handle cell double click events

    Args:
      index (QModelIndex): The index of the double clicked cell
    """
    model = self.table.model()
    if not isinstance(model, PandasTableModel):
      return
    docID = model.documentIds[index.row()]
    if self.docType == 'x0':
      self.comm.changeProject.emit(docID, '')
      self.comm.changeSidebar.emit(docID)
    else:
      self.comm.formDoc.emit({'id': docID})
      self.refresh()


  @Slot(QListWidgetItem)
  def onGalleryItemClicked(self, item: QListWidgetItem) -> None:
    """Handle gallery item click events

    Args:
      item (QListWidgetItem): The clicked gallery item
    """
    docID = str(item.data(Qt.ItemDataRole.UserRole))
    self.detailsDocID = docID
    self.comm.changeDetails.emit(docID)


  @Slot(QListWidgetItem)
  def onGalleryItemDoubleClicked(self, item: QListWidgetItem) -> None:
    """Handle gallery item double click events

    Args:
      item (QListWidgetItem): The double clicked gallery item
    """
    self.comm.formDoc.emit({'id': str(item.data(Qt.ItemDataRole.UserRole))})
    self.refresh()


  @Slot(str)
  def onSubTypeChanged(self, title: str) -> None:
    """Handle sub type changed events

    Args:
      title (str): The new sub type title
    """
    if not title:
      return
    matching = [key for key in self.comm.docTypesTitles if self.comm.docTypesTitles[key]['title'] == title]
    if not matching:
      return
    docType = matching[0]
    self.reloadComboBoxFlag = self.docType not in docType and docType not in self.docType
    self.docType = docType
    self.refresh()


  @Slot(int, bool)
  def onRowCheckChanged(self, row: int, checked: bool) -> None:
    """Handle row check changed events

    Args:
      row (int): The row index
      checked (bool): Whether the row is checked
    """
    selection = self.table.selectionModel()
    if selection is None:
      return
    index = self.table.model().index(row, 0)
    selection.blockSignals(True)
    try:
      selection.select(index, (QItemSelectionModel.SelectionFlag.Select if checked else QItemSelectionModel.SelectionFlag.Deselect)
                       | QItemSelectionModel.SelectionFlag.Rows)
    finally:
      selection.blockSignals(False)


  @Slot()
  def stopSequentialEdit(self) -> None:
    """Stop sequential edit"""
    self._stopSequentialEdit = True


  def removeFilter(self, filterRow: FilterRow) -> None:
    """Remove filter

    Args:
      filterRow (FilterRow): The filter widget to remove
    """
    self.filterRows.remove(filterRow)
    self.filterL.removeWidget(filterRow)
    filterRow.deleteLater()
    self.paint()


  def filteredTableData(self) -> tuple[pd.DataFrame, list[str]]:
    """Return formatted rows matching all active filters, plus their document IDs.

    Returns:
      pd.DataFrame: The filtered table data.
      list[str]: The document IDs corresponding to the filtered rows.
    """
    if self.data.empty:
      return pd.DataFrame(), []
    base = self.data.copy()
    base.fillna('-', inplace=True)
    base.replace(['None', '', 'nan'], '-', inplace=True)
    base.replace('True', 'Y', inplace=True)
    base.mask(base.map(isDocID), 'oo', inplace=True)
    base = base.iloc[:, :-2].copy()
    documentIds = self.data.loc[base.index, 'id']
    for filterRow in self.filterRows:
      value = filterRow.text.text()
      header = filterRow.column.currentText()
      if value and header in base.columns:
        base = base[base[header].astype(str).str.contains(value, case=False, regex=False, na=False)]
        documentIds = documentIds.loc[base.index]
    return base.reset_index(drop=True), documentIds.to_list()


  def selectedDocumentIds(self) -> list[str]:
    """Return checked rows, or gallery selections while gallery mode is active.
    Returns:
      list[str]: The document IDs corresponding to the selected rows.
    """
    if self.gallery.isVisible():
      return [str(item.data(Qt.ItemDataRole.UserRole)) for item in self.gallery.selectedItems()]
    model = self.table.model()
    if not isinstance(model, PandasTableModel):
      return []
    return [model.documentIds[row] for row, checked in enumerate(model.checkedRows) if checked]


  def modelDocumentIds(self) -> list[str]:
    """Return all document IDs in the table model.
    Returns:
      list[str]: The document IDs corresponding to the table model.
    """
    model = self.table.model()
    if not isinstance(model, PandasTableModel):
      return []
    return [model.documentIds[row] for row in range(model.rowCount())]


  def synchronizeSelectionAndCheckbox(self, selected: QItemSelection, deselected: QItemSelection) -> None:
    """Synchronize selection and checkbox

    Args:
      selected (QItemSelection): The selected indexes
      deselected (QItemSelection): The deselected indexes
    """
    model = self.table.model()
    if not isinstance(model, PandasTableModel):
      return
    for index in selected.indexes():
      if index.column() == 0 and not model.checkedRows[index.row()]:
        model.checkRow(index.row(), True)
    for index in deselected.indexes():
      if index.column() == 0 and model.checkedRows[index.row()]:
        model.checkRow(index.row(), False)


def normalizeColumns(view: QTableView) -> None:
  """Scale content-sized columns to the available viewport width.

  Args:
    view (QTableView): The table view to normalize columns for
  """
  model = view.model()
  if model is None or not model.columnCount():
    return
  widths = [view.columnWidth(column) for column in range(model.columnCount())]
  total = sum(widths)
  if total <= 0:
    return
  scale = max(1, view.viewport().width() - 25) / total
  for column, width in enumerate(widths):
    view.setColumnWidth(column, int(width * scale))


class Command(Enum):
  """Commands exposed by the document list toolbar."""
  NEW_ENTRY = 1
  TOGGLE_SELECTION = 2
  GROUP_EDIT = 3
  SEQUENTIAL_EDIT = 4
  TOGGLE_HIDDEN = 5
  RERUN_EXTRACTORS = 6
  DELETE = 7
  ADD_FILTER = 8
  SHOW_HIDDEN = 9
  TOGGLE_GALLERY = 10
  EXPORT_CSV = 11
  ADD_ON = 12
  CHANGE_COLUMNS = 13
