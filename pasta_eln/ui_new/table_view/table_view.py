"""Displays the Table with the Action-buttons of a DocType (one TableView per DocType)"""
import logging

import pandas as pd
from PySide6.QtCore import QModelIndex, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QTableView, QVBoxLayout, QWidget

from pasta_eln.misc_tools import isDocID
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui_new.table_view.pandas_table_model import PandasTableModel


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

    # Buttonbar
    self.buttonbar = QWidget(self)
    self.buttonbarLayout = QHBoxLayout()
    self.buttonbarLayout.addWidget(self.subTypeCombo)
    self.buttonbarLayout.addStretch()
    self.buttonbarLayout.addWidget(QPushButton("Test Right"))
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
    self.table.resizeColumnsToContents()
    normalizeColumns(self.table)

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
    What happens when the user double clicks on a cell in the table
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
