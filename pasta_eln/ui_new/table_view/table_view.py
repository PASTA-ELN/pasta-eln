"""Displays the Table with the Action-buttons of a DocType (one TableView per DocType)"""
import logging
from enum import Enum
from typing import Any

import pandas as pd
import qtawesome
from PySide6.QtCore import QItemSelectionModel, QModelIndex, QSize, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QMenu, QPushButton, QTableView, QVBoxLayout, QWidget

from pasta_eln.misc_tools import isDocID
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Action
from pasta_eln.ui_new.table_view.pandas_table_model import PandasTableModel
from pasta_eln.ui_new.workplan_creator.workplan_creator_dialog import WorkplanCreatorDialog


class TableView(QWidget):
  """Displays the Table with the Action-buttons of a DocType (one TableView per DocType)"""

  def __init__(self, comm: Communicate, docType: str):
    super().__init__()
    self.comm = comm
    self.docType = docType
    self.data = pd.DataFrame()
    self.showAll = self.comm.configuration['GUI']['showHidden'] == 'Yes'
    self.detailsDocID = ''
    self.tableData = pd.DataFrame()
    self.reloadComboBoxFlag = True

    # Subtype-Combobox
    self.subTypeCombo = QComboBox()
    self.subTypeCombo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    self.subTypeCombo.setPlaceholderText("Select Subtype")
    self.subTypeCombo.currentTextChanged.connect(self.onSubTypeChanged)

    # NewEntry-Button
    self.newEntryButton = QPushButton("New Entry", default=True)
    iconColor = self.comm.palette.getThemeColor("background", "base")
    self.newEntryButton.setIcon(qtawesome.icon("ri.add-fill", color=iconColor))
    self.newEntryButton.setIconSize(QSize(20, 20))
    self.newEntryButton.clicked.connect(lambda: self.execute([Command.NEW_ENTRY]))

    # Action-Button
    self.actionButton = QPushButton("Actions")
    iconColor = self.comm.palette.getThemeColor("foreground", "base")
    self.actionButton.setIcon(qtawesome.icon("ri.task-line", color=iconColor))
    self.actionButton.setIconSize(QSize(20, 20))
    self.actionMenu = QMenu(self)
    self.actionButton.setMenu(self.actionMenu)
    Action('Group Edit', self, [Command.GROUP_EDIT], self.actionMenu)
    self.actionMenu.addSeparator()
    Action('Delete', self, [Command.DELETE], self.actionMenu)

    # More-Button
    self.moreButton = QPushButton("More")
    self.moreButton.setIcon(qtawesome.icon("ri.more-fill", color=iconColor))
    self.moreButton.setIconSize(QSize(20, 20))
    self.moreMenu = QMenu(self)
    self.moreButton.setMenu(self.moreMenu)
    Action('Test1', self, [Command.TEST], self.moreMenu)

    # Buttonbar
    self.buttonbar = QWidget(self)
    self.buttonbarLayout = QHBoxLayout()
    self.buttonbarLayout.addWidget(self.subTypeCombo)
    self.buttonbarLayout.addStretch()
    self.buttonbarLayout.addWidget(self.newEntryButton)
    self.buttonbarLayout.addWidget(self.actionButton)
    self.buttonbarLayout.addWidget(self.moreButton)
    self.buttonbarLayout.setContentsMargins(0, 10, 0, 10)
    self.buttonbar.setLayout(self.buttonbarLayout)

    # Table
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

    # Layout
    self.layout = QVBoxLayout()
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.setSpacing(0)
    self.layout.addWidget(self.buttonbar)
    self.layout.addWidget(self.table)
    self.setLayout(self.layout)

    # Style

    # Signals
    self.comm.backendThread.worker.beSendTable.connect(self.onGetData)
    self.comm.changeTable.connect(self.onTableChange)

  def paint(self) -> None:
    """
    Update the table
    """
    # Set up the subTypeCombobox. Is regenerated everytime, could be optimized
    if self.reloadComboBoxFlag and "/" not in self.docType:
      self.subTypeCombo.clear()
      docTypeKeys = [i for i in self.comm.docTypesTitles if i.startswith(self.docType)]
      currentSubTypes = [self.comm.docTypesTitles[key]["title"] for key in docTypeKeys]
      if len(currentSubTypes) <= 1:
        self.subTypeCombo.setDisabled(True)
      else:
        self.subTypeCombo.setDisabled(False)
        self.subTypeCombo.addItems(currentSubTypes)
    self.reloadComboBoxFlag = True
    # Populate Table
    self.tableData = self.reformatData().iloc[:, :-2]
    model = PandasTableModel(self.tableData)
    self.table.setModel(model)
    model.rowCheckChanged.connect(self.onRowCheckChanged)
    self.table.selectionModel().selectionChanged.connect(self.synchronizeSelectionAndCheckbox)
    self.table.resizeColumnsToContents()
    normalizeColumns(self.table)
    self.table.setColumnWidth(0, 30)

  def execute(self, command: list[Any]) -> None:
    """
    Handler for the Buttons that use Actions/Commands

    Args:
      command (list): list of commands
    """
    if command[0] is Command.TEST:
      print("Test")

    elif command[0] is Command.NEW_ENTRY:
      if self.docType == "workflow/workplan":
        workplanCreatorDialog = WorkplanCreatorDialog(self.comm)
        workplanCreatorDialog.exec()
      else:
        self.comm.formDoc.emit({'type': [self.docType], '_projectID': self.comm.projectID})
      self.comm.changeTable.emit(self.docType, self.comm.projectID)
      if self.docType == 'x0':
        self.comm.changeSidebar.emit('redraw')

    elif command[0] is Command.GROUP_EDIT:
      print("group edit")
      # docIDs = []
      # finalModel = self.filterManager.getFinalModel()
      # for row in range(finalModel.rowCount()):
      #   item, docID = self.itemFromRow(row)
      #   if (self.flagGallery and self.gallery.isDocSelected(docID)) or \
      #     (not self.flagGallery and item.checkState() == Qt.CheckState.Checked):
      #     docIDs.append(docID)
      # if docIDs:
      #   self.comm.formDoc.emit({'type': [self.docType], '_ids': docIDs})
      #   self.changeTable(self.docType, self.comm.projectID)

    elif command[0] is Command.DELETE:
      print("Delete")

  @Slot(str, str)
  def onTableChange(self, docType: str, projID: str) -> None:
    """ What happens when user clicks to change doc-type
    Args:
      docType (str): document type
      projID (str): project id
    """
    if docType != self.docType:
      return
    if projID:
      self.comm.projectID = projID
    logging.debug('request table for %s, %s %s', self.docType, self.comm.projectID, self.showAll)
    self.comm.uiRequestTable.emit(self.docType, self.comm.projectID, self.showAll)

  @Slot(pd.DataFrame, str)
  def onGetData(self, data: pd.DataFrame, docType: str) -> None:
    """
    Callback function to handle the received data

    Args:
      data (pd.DataFrame): DataFrame containing table
      docType (str): document type
    """
    logging.debug('got table data %s', docType)
    if docType == self.docType:
      self.data = data
      if self.detailsDocID and self.detailsDocID not in data.id.values:
        self.comm.changeDetails.emit('')
      self.paint()

  def reformatData(self) -> pd.DataFrame:
    """
    Formats the data to create the table out of.
    """
    tableData = self.data.copy()
    tableData.fillna("-", inplace=True)
    tableData.replace(['None', '', 'nan'], "-", inplace=True)
    tableData.replace("True", "Y", inplace=True)
    tableData.mask(tableData.map(isDocID), "oo", inplace=True)  # TODO WHY?
    return tableData

  @Slot()
  def onCellClicked(self, index: QModelIndex) -> None:
    """
    What happens when user clicks cell in table of tags, projects, samples, ..
    -> show details

    Args:
      index (QModelIndex): cell clicked
    """
    row = index.row()
    docID = self.data.id[row]
    self.comm.changeDetails.emit(docID)

  @Slot()
  def onCellDoubleClicked(self, index: QModelIndex) -> None:
    """
    What happens when the user double-clicks on a cell in the table
      -> Nothing yet.
    Args:
      index (QModelIndex): Index of the cell clicked
    """
    pass

  @Slot()
  def onSubTypeChanged(self, title: str) -> None:
    """
    What happens when the subType is changed, typically using the QCombobox in the tableView
    Args:
      title: The displayed title of the subType e.g. 'Procedure', not the internal 'workflow/procedure'
    """
    if not title:
      return
    docType = [i for i in self.comm.docTypesTitles if self.comm.docTypesTitles[i]["title"] == title][0]
    if self.docType in docType or docType in self.docType:
      self.reloadComboBoxFlag = False
    self.docType = docType
    self.comm.changeTable.emit(docType, '')

  @Slot(int, bool)
  def onRowCheckChanged(self, row: int, checked: bool) -> None:
    """
    When a checkbox is (un)checked, update the selection of the row accordingly
    """
    index = self.table.model().index(row, 0)
    self.table.selectionModel().blockSignals(True)
    try:
      if checked:
        self.table.selectionModel().select(index,
                                           QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
      else:
        self.table.selectionModel().select(index,
                                           QItemSelectionModel.SelectionFlag.Deselect | QItemSelectionModel.SelectionFlag.Rows)
    finally:
      self.table.selectionModel().blockSignals(False)

  def synchronizeSelectionAndCheckbox(self, selected, deselected):
    """
    When a row is selected, the Checkbox should be selected, too
    """
    model = self.table.model()
    if not isinstance(model, PandasTableModel):
      print("Wrong model in tableview")
      return

    for idx in selected.indexes():
      if idx.column() != 0:
        continue
      if not model.checkedRows()[idx.row()]:
        model.checkRow(idx.row(), True)

    for idx in deselected.indexes():
      if idx.column() != 0:
        continue
      if model.checkedRows()[idx.row()]:
        model.checkRow(idx.row(), False)


def normalizeColumns(view: QTableView) -> None:
  """
  Calculates the relative width of each column to prevent horizontal overflow
  Args:
    view: The Table that needs to be normalized
  """
  model = view.model()

  total = 0
  widths = []

  for c in range(model.columnCount()):
    w = view.columnWidth(c)
    widths.append(w)
    total += w

  viewportWidth = view.viewport().width() - 25

  scale = viewportWidth / total

  for c, w in enumerate(widths):
    view.setColumnWidth(c, int(w * scale))


class Command(Enum):
  """Commands for execute function in this file"""
  TEST = 0
  NEW_ENTRY = 1
  GROUP_EDIT = 2
  DELETE = 3
