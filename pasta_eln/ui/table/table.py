"""Displays the Table with the Action-buttons of a DocType (one TableView per DocType)"""
import logging
from enum import Enum
import pandas as pd
from PySide6.QtCore import QItemSelection, QItemSelectionModel, QModelIndex, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QMenu, QTableView, QVBoxLayout, QWidget
from pasta_eln.misc_tools import isDocID
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Action
from pasta_eln.ui.table.pandas_table_model import PandasTableModel
from pasta_eln.ui.widget import Button, ButtonStyle, Widget
from pasta_eln.ui.workplan_creator.workplan_creator_dialog import WorkplanCreatorDialog


class TableView(Widget):
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
    self.subTypeCombo.setPlaceholderText('Select Subtype')
    self.subTypeCombo.currentTextChanged.connect(self.onSubTypeChanged)

    # Buttonbar
    self.buttonbarW = QWidget(self)
    self.buttonbarL = QHBoxLayout()
    self.buttonbarL.addWidget(self.subTypeCombo)
    self.buttonbarL.addStretch()

    # New entry button: the one highlighted action in this view.
    self.newEntryButton = Button('New Entry', self, Command.NEW_ENTRY, self.buttonbarL, icon='ri.add-fill',
                                 style=ButtonStyle.HIGHLIGHTED)

    # Action-Button
    self.actionButton = Button('Actions', self, layout=self.buttonbarL, icon='ri.task-line',
                               style=ButtonStyle.PRIMARY)
    self.actionMenu = QMenu(self)
    self.actionButton.setMenu(self.actionMenu)
    Action('Group Edit', self, Command.GROUP_EDIT, self.actionMenu)
    self.actionMenu.addSeparator()
    Action('Delete',     self, Command.DELETE,     self.actionMenu)

    # More-Button
    self.moreButton = Button('More', self, layout=self.buttonbarL, icon='ri.more-fill',
                             style=ButtonStyle.PRIMARY)
    self.moreMenu = QMenu(self)
    self.moreButton.setMenu(self.moreMenu)
    Action('Test1', self, Command.TEST, self.moreMenu)
    self.buttonbarL.setContentsMargins(0, 10, 0, 10)
    self.buttonbarW.setLayout(self.buttonbarL)

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
    self.mainLayout = QVBoxLayout()
    self.mainLayout.setContentsMargins(0, 0, 0, 0)
    self.mainLayout.setSpacing(0)
    self.mainLayout.addWidget(self.buttonbarW)
    self.mainLayout.addWidget(self.table)
    self.setLayout(self.mainLayout)

    # Style

    # Signals
    self.comm.backendThread.worker.beSendTable.connect(self.onGetData)
    self.comm.changeTable.connect(self.onTableChange)


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


  def paint(self) -> None:
    """
    Update the table
    """
    # Set up the subTypeCombobox. Is regenerated everytime, could be optimized
    if self.reloadComboBoxFlag and '/' not in self.docType:
      self.subTypeCombo.clear()
      docTypeKeys = [i for i in self.comm.docTypesTitles if i.startswith(self.docType)]
      currentSubTypes = [self.comm.docTypesTitles[key]['title'] for key in docTypeKeys]
      if len(currentSubTypes) <= 1:
        self.subTypeCombo.hide()
      else:
        self.subTypeCombo.show()
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


  def execute(self, command: Command) -> None:
    """
    Handler for the Buttons that use Actions/Commands

    Args:
      command: command emitted by a button or menu action
    """
    if command is Command.TEST:
      print('Test')

    elif command is Command.NEW_ENTRY:
      if self.docType == 'workflow/workplan':
        workplanCreatorDialog = WorkplanCreatorDialog(self.comm)
        workplanCreatorDialog.exec()
      else:
        self.comm.formDoc.emit({'type': [self.docType], '_projectID': self.comm.projectID})
      self.comm.changeTable.emit(self.docType, self.comm.projectID)
      if self.docType == 'x0':
        self.comm.changeSidebar.emit('redraw')

    elif command is Command.GROUP_EDIT:
      print('group edit')
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

    elif command is Command.DELETE:
      print('Delete')


  def reformatData(self) -> pd.DataFrame:
    """
    Formats the data to create the table
    """
    tableData = self.data.copy()
    tableData.fillna('-', inplace=True)
    tableData.replace(['None', '', 'nan'], '-', inplace=True)
    tableData.replace('True', 'Y', inplace=True)
    tableData.mask(tableData.map(isDocID), 'oo', inplace=True)
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
    return


  @Slot()
  def onSubTypeChanged(self, title: str) -> None:
    """
    What happens when the subType is changed, typically using the QCombobox in the tableView
    Args:
      title: The displayed title of the subType e.g. 'Procedure', not the internal 'workflow/procedure'
    """
    if not title:
      return
    docType = [i for i in self.comm.docTypesTitles if self.comm.docTypesTitles[i]['title'] == title][0]
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
    selFlag = QItemSelectionModel.SelectionFlag
    try:
      if checked:
        self.table.selectionModel().select(index, selFlag.Select | selFlag.Rows)
      else:
        self.table.selectionModel().select(index, selFlag.Deselect | selFlag.Rows)
    finally:
      self.table.selectionModel().blockSignals(False)


  def synchronizeSelectionAndCheckbox(self, selected: QItemSelection, deselected: QItemSelection) -> None:
    """When a row is selected, the Checkbox should be selected, too

    Args:
      selected (QItemSelection): The selected items
      deselected (QItemSelection): The deselected items
    """
    model = self.table.model()
    if not isinstance(model, PandasTableModel):
      logging.critical('Wrong model in tableview')
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
  for col in range(model.columnCount()):
    width = view.columnWidth(col)
    widths.append(width)
    total += width
  viewportWidth = view.viewport().width() - 25
  scale = viewportWidth / total
  for col, width in enumerate(widths):
    view.setColumnWidth(col, int(width * scale))


class Command(Enum):
  """Commands for execute function in this file"""
  TEST = 0
  NEW_ENTRY = 1
  GROUP_EDIT = 2
  DELETE = 3
