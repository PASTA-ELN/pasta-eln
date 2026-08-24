""" widget that shows the table of the items """
import itertools
import logging
from enum import Enum
from pathlib import Path
from typing import Any
import pandas as pd
import qtawesome as qta
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Slot
from PySide6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)
from ...misc_tools import callAddOn
from ..gui_communicate import Communicate
from ..gui_style import SPACE, Button, ButtonStyle
from ..icon_button_delegate import IconButtonDelegate
from .terminology_lookup_dialog import TerminologyLookupDialog

COLUMN_NAMES = ['key','label','PURL','', '']
COLUMN_WIDTH = [200,  400,   250, 50, 50]


def _hasOnlineLink(index: QModelIndex) -> bool:
  """Return whether the row contains a usable online identifier."""
  link = index.model().index(index.row(), 2).data()
  return bool(link and 'http' in link and '://' in link)


def _openOnlineLink(_: QAbstractItemModel, index: QModelIndex) -> None:
  """Open the first online identifier from the selected row."""
  import webbrowser
  webbrowser.open(index.model().index(index.row(), 2).data().split(', ')[0])


def _hasKeyOrLabel(index: QModelIndex) -> bool:
  """Return whether terminology lookup has a search term."""
  model = index.model()
  return bool(model.index(index.row(), 0).data() or model.index(index.row(), 1).data())


class Editor(QDialog):
  """ widget that shows the table of the items """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): Shared communication object.
    """
    super().__init__()
    self.comm = comm
    self.comm.backendThread.worker.beSendSQL.connect(self.onGetData)
    self.data:pd.DataFrame = pd.DataFrame()
    self.df0:pd.DataFrame = pd.DataFrame()
    self.df1:pd.DataFrame = pd.DataFrame()
    self.terminologyDialog: TerminologyLookupDialog | None = None
    self.setMinimumWidth(1000)
    self.setWindowTitle('Edit definitions')

    ### GUI elements
    mainL = QVBoxLayout(self)
    mainL.setContentsMargins(SPACE.M, SPACE.M, SPACE.M, SPACE.M)
    mainL.setSpacing(SPACE.S)
    ### Table
    self.table = QTableWidget(1, 5)
    self.table.verticalHeader().hide()
    self.table.setAlternatingRowColors(True)
    self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    self.table.setHorizontalHeaderLabels(COLUMN_NAMES)
    for idx, width in enumerate(COLUMN_WIDTH):
      self.table.setColumnWidth(idx, width)
    self.linkOnlineDelegate = IconButtonDelegate('mdi.earth-arrow-right', _hasOnlineLink, _openOnlineLink)
    self.table.setItemDelegateForColumn(3, self.linkOnlineDelegate)
    self.lookupDelegate = IconButtonDelegate('fa5s.search', _hasKeyOrLabel, self.openTerminologyLookup)
    self.table.setItemDelegateForColumn(4, self.lookupDelegate)
    self.table.horizontalHeader().setStretchLastSection(True)
    mainL.addWidget(self.table)
    ### final button box
    buttonLineW = QWidget(self)
    buttonLineL = QHBoxLayout(buttonLineW)
    buttonLineL.setSpacing(SPACE.M)
    buttonLineL.setContentsMargins(0, 0, 0, 0)
    mainL.addWidget(buttonLineW)
    Button('Import', self, Command.IMPORT, buttonLineL, tooltip='Import from CSV')
    Button('Export', self, Command.EXPORT, buttonLineL, tooltip='Export to CSV')
    buttonLineL.addStretch(1)
    projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
    if 'definition' in projectGroup.get('addOns',{}) and projectGroup['addOns']['definition']:
      Button('Autofill PURL', self, Command.ADDON, buttonLineL, tooltip='Autofill by using add-on')
      buttonLineL.addStretch(1)
    self.saveBtn = Button('Save', self, Command.SAVE, buttonLineL, tooltip='Save changes',
                          style=ButtonStyle.HIGHLIGHTED)
    self.saveBtn.setShortcut('Ctrl+Return')
    Button('Cancel', self, Command.CANCEL, buttonLineL, tooltip='Discard changes')
    ### Data
    self.comm.uiSendSQL.emit([{'type':'get_df','cmd':'SELECT docType, PURL, title FROM docTypes'},
                              {'type':'get_df','cmd':'SELECT * FROM definitions'}])
    self.paint()


  @Slot(str, pd.DataFrame)
  def onGetData(self, cmd:str, data:pd.DataFrame) -> None:
    """ Handle data received from backend worker
    Args:
      cmd (str): command that was sent
      data (pd.DataFrame): DataFrame containing the data
    """
    if cmd == 'SELECT * FROM definitions':
      data = data[data['key'].str.contains(r'\.')]  #filter out rows that do not contain a . in the key column
      data['defType'] = 'attribute'
      self.df1 = data
    elif cmd == 'SELECT docType, PURL, title FROM docTypes':
      data['defType'] = 'class'
      self.df0 = data.rename({'docType':'key', 'title':'long'}, axis=1)
    self.data = pd.concat([self.df0,self.df1])[['key','long','PURL','defType']]
    self.data.rename({'long':'label'}, axis=1, inplace=True)
    self.paint()


  def execute(self, command:'Command') -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command is Command.EXPORT:
      fileName = QFileDialog.getSaveFileName(self, 'Save table to .csv file', str(Path.home()), '*.csv')[0]
      if fileName != '':
        self.getDataframe().to_csv(fileName, index=False)
    elif command is Command.IMPORT:
      fileName = QFileDialog.getOpenFileName(self, 'Read table from .csv file', str(Path.home()), '*.csv')[0]
      if fileName != '':
        importedData = pd.read_csv(fileName, dtype=str).fillna('')
        requiredColumns = {'key', 'description', 'PURL', 'defType'}
        if set(importedData.columns) != requiredColumns:
          QMessageBox.warning(self, 'Invalid definitions file',
                              'The CSV file must contain exactly the columns: key, description, PURL, defType.')
          return
        if not importedData['defType'].isin({'class', 'attribute'}).all():
          QMessageBox.warning(self, 'Invalid definitions file',
                              'The defType column may contain only "class" or "attribute".')
          return
        self.data = importedData.rename({'description':'label'}, axis=1)[['key', 'label', 'PURL', 'defType']]
        self.paint()
    elif command is Command.ADDON:
      try:
        self.data = callAddOn('definition_autofill', self.comm, self.data, self)
        self.paint()
      except Exception:
        pass
    elif command is Command.CANCEL:
      self.reject()
    elif command is Command.SAVE:
      tasks:list[dict[str,Any]] = []
      for _, row in self.getDataframe().iterrows():
        key, description, purl, dType = row.values
        if dType == 'class':
          tasks.append({'type':'one', 'cmd':'UPDATE docTypes SET PURL = ?, title = ? WHERE docType = ?',
                        'list':[purl, description, key]})
        else:
          tasks.append({'type':'one', 'cmd':'INSERT OR REPLACE INTO definitions VALUES (?, ?, ?);',
                        'list':[key, description, purl]})
      self.comm.uiSendSQL.emit(tasks)
      self.accept()
    else:
      logging.error('Command unknown: %s',command, exc_info=True)
    return


  def paint(self) -> None:
    """ Show data frame in the GUI """
    self.table.setRowCount(len(self.data))
    nRows, nCols = self.data.shape
    for i, j in itertools.product(range(nRows), range(nCols-1)):
      rowType = self.data.iloc[i, 3]
      icon = qta.icon('msc.symbol-class' if rowType=='class' else 'msc.symbol-property', scale_factor=1)
      item = QTableWidgetItem(self.data.iloc[i, j])
      if j==0:
        item.setIcon(icon)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
      self.table.setItem(i, j, item)
    return


  def openTerminologyLookup(self, _: QAbstractItemModel, index: QModelIndex) -> None:
    """Show terminology lookup and store selected identifiers in the PURL column."""
    model = index.model()
    key = model.index(index.row(), 0).data()
    label = model.index(index.row(), 1).data()

    def setPURL(iris: list[str]) -> None:
      """Write the selected persistent URLs into the current definition row.

      Args:
        iris (list[str]): Persistent identifiers selected by the terminology lookup.
      """
      model.setData(model.index(index.row(), 2), ', '.join(iris))

    self.terminologyDialog = TerminologyLookupDialog(label or key, setPURL)
    self.terminologyDialog.show()


  def getDataframe(self) -> pd.DataFrame:
    """ Get dataframe from table """
    model = self.table.model()
    data = []
    for row in range(model.rowCount()):
      rowRes = [model.index(row, column).data() for column in range(3)]
      data.append(rowRes)
    df = pd.DataFrame(data)
    df = df.rename({0:'key',1:'description',2:'PURL'}, axis=1)
    df = df.merge(self.data, how='left', left_on='key', right_on='key')
    df = df.drop(['label','PURL_y'], axis=1).rename({'PURL_x':'PURL'}, axis=1)
    # df['defType']=self.data['defType'].values    # ignore
    return df


  def reject(self) -> None:
    """ Reject the dialog, stop the thread and disconnect signals """
    self.comm.backendThread.worker.beSendSQL.disconnect(self.onGetData)
    super().reject()


  def accept(self) -> None:
    """ Accept the dialog, stop the thread and disconnect signals """
    self.comm.backendThread.worker.beSendSQL.disconnect(self.onGetData)
    super().accept()


class Command(Enum):
  """ Commands used in this file """
  SAVE   = 1
  CANCEL = 2
  IMPORT = 3
  EXPORT = 4
  ADDON  = 5
