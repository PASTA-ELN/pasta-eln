""" widget that shows the table of the items """
import itertools
import logging
from enum import Enum
from pathlib import Path
from typing import Any
import pandas as pd
import qtawesome as qta
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout
from ...miscTools import callAddOn
from ..guiCommunicate import Communicate
from ..guiStyle import TextButton, space, widgetAndLayout
from .key_delegate import KeyDelegate
from .link_online_delegate import LinkOnlineDelegate
from .lookup_delegate import LookupDelegate

COLUMN_NAMES = ['key','long','PURL','', '']
COLUMN_WIDTH = [200,  400,   250, 50, 50]


class Editor(QDialog):
  """ widget that shows the table of the items """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    self.comm.backendThread.worker.beSendSQL.connect(self.onGetData)
    self.data:pd.DataFrame = pd.DataFrame()
    self.df0:pd.DataFrame = pd.DataFrame()
    self.df1:pd.DataFrame = pd.DataFrame()
    self.setMinimumWidth(1000)
    self.setWindowTitle('Edit definitions')

    ### GUI elements
    mainL = QVBoxLayout()
    mainL.setSpacing(space['l'])
    self.setLayout(mainL)
    ### Table
    self.table = QTableWidget(1, 5)
    self.table.verticalHeader().hide()
    self.table.setAlternatingRowColors(True)
    self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    self.table.setHorizontalHeaderLabels(COLUMN_NAMES)
    for idx, width in enumerate(COLUMN_WIDTH):
      self.table.setColumnWidth(idx, width)
    self.keyDelegate = KeyDelegate()
    self.table.setItemDelegateForColumn(0, self.keyDelegate)
    self.linkOnlineDelegate = LinkOnlineDelegate()
    self.table.setItemDelegateForColumn(3, self.linkOnlineDelegate)
    self.lookupDelegate     = LookupDelegate()
    self.table.setItemDelegateForColumn(4, self.lookupDelegate)
    self.table.horizontalHeader().setStretchLastSection(True)
    mainL.addWidget(self.table)
    ### final button box
    _, buttonLineL = widgetAndLayout('H', mainL, 'm')
    TextButton('Import', self, [Command.Import], buttonLineL, 'Import from Excel')
    TextButton('Export', self, [Command.Export], buttonLineL, 'Export to Excel')
    buttonLineL.addStretch(1)
    projectGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
    if 'definition' in projectGroup.get('addOns',{}) and projectGroup['addOns']['definition']:
      TextButton('Autofill PURL',  self, [Command.AddOn], buttonLineL, 'Autofill by using add-on')
      buttonLineL.addStretch(1)
    self.saveBtn = TextButton('Save', self, [Command.Save], buttonLineL, 'Save changes')
    self.saveBtn.setShortcut('Ctrl+Return')
    TextButton('Cancel', self, [Command.Cancel],   buttonLineL, 'Discard changes')
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
      data['defType'] = 'attribute'
      self.df1 = data
    elif cmd == 'SELECT docType, PURL, title FROM docTypes':
      data['defType'] = 'class'
      self.df0 = data.rename({'docType':'key', 'title':'long'}, axis=1)
    self.data = pd.concat([self.df0,self.df1])[['key','long','PURL','defType']]
    self.paint()


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.Export:
      fileName = QFileDialog.getSaveFileName(self, 'Save table to .csv file', str(Path.home()), '*.csv')[0]
      if fileName != '':
        self.getDataframe().to_csv(fileName, index=False)
    elif command[0] is Command.Import:
      fileName = QFileDialog.getOpenFileName(self, 'Read table from .csv file', str(Path.home()), '*.csv')[0]
      if fileName != '':
        self.data = pd.read_csv(fileName).fillna('')
        self.paint()
    elif command[0] is Command.AddOn:
      try:
        self.data = callAddOn('definition_autofill', self.comm, self.data, self)
        self.paint()
      except Exception:
        pass
    elif command[0] is Command.Cancel:
      self.reject()
    elif command[0] is Command.Save:
      tasks:list[dict[str,Any]] = []
      for _, row in self.getDataframe().iterrows():
        key, description, purl, dType = row.values
        if dType == 'class':
          tasks.append({'type':'one',
                   'cmd':f"UPDATE docTypes SET PURL='{purl}', title='{description}' WHERE docType = '{key}'"})
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
      self.table.setItem(i, j, item)
    return


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
    df = df.drop(['long','PURL_y'], axis=1).rename({'PURL_x':'PURL'}, axis=1)
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
  Save   = 1
  Cancel = 2
  Import = 3
  Export = 4
  AddOn  = 5
