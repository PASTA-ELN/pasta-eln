""" dialog to edit docType schema """
from enum import Enum
from typing import Any
import numpy as np
import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QInputDialog, QMessageBox, QTabBar, QTableWidget,
                               QTableWidgetItem, QTabWidget, QVBoxLayout)
from ..guiCommunicate import Communicate
from ..guiStyle import IconButton, Label, TextButton, widgetAndLayout
from ..messageDialog import showMessage
from .delete_column_delegate import DeleteColumnDelegate
from .docTypeEdit import DocTypeEditor
from .listFreeDelegate import ListFreeDelegate
from .listItemDelegate import ListItemDelegate
from .mandatory_column_delegate import MandatoryColumnDelegate
from .name_column_delegate import NameColumnDelegate
from .reorder_column_delegate import ReorderColumnDelegate

#                0       1            2      3           4      5         6
COLUMN_NAMES = ['name','description','unit','mandatory','item list','free list','move up','delete']
COLUMN_WIDTH = [100,   250,          60,    80,         150,        200,        60,       50]
pd.options.mode.copy_on_write = True

class SchemeEditor(QDialog):
  """ dialog to edit docType schema """
  def __init__(self, comm:Communicate):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      doc (dict):  document to change / create
    """
    super().__init__()
    self.comm = comm
    self.comm.backendThread.worker.beSendSQL.connect(self.onGetData)
    self.docType = ''
    self.docLabel= ''
    self.cmd     = ''
    self.df      = pd.DataFrame()
    self.docTypesLabels = [(k,v['title']) for k,v in self.comm.docTypesTitles.items()]
    self.closeButtons:list[IconButton] = []                                             #close buttons of tabs
    self.setWindowTitle('Data scheme editor')
    self.restartAfterClose = False

    # GUI elements
    self.setMinimumWidth(int(np.sum(COLUMN_WIDTH))+80)
    self.setMinimumHeight(500)
    mainL = QVBoxLayout(self)
    Label('Item type editor', 'h1', mainL)
    Label('Warning: every change of the item type saves that content', 'h3', mainL)
    _, docTypeL = widgetAndLayout('H', mainL, 's')
    Label('Item type:', '', docTypeL)
    self.selectDocType = QComboBox()
    self.selectDocType.currentTextChanged.connect(self.changeDocType)
    self.selectDocType.setStyleSheet(self.comm.palette.get('secondaryText','color'))
    docTypeL.addWidget(self.selectDocType)
    docTypeL.addStretch(1)
    IconButton('fa5s.plus',  self, [Command.NEW],  docTypeL, tooltip='New item type')
    IconButton('fa5s.edit',  self, [Command.EDIT], docTypeL, tooltip='Edit item type')
    IconButton('fa5s.trash', self, [Command.DEL],  docTypeL, tooltip='Delete item type')

    # tabs: empty
    self.tabW = QTabWidget(self)
    self.tabW.tabBarDoubleClicked.connect(self.renameTab)
    self.tabW.tabBarClicked.connect(self.createNewTab)
    mainL.addWidget(self.tabW, stretch=10)
    self.nameColumnDelegates     :list[NameColumnDelegate]      = []
    self.mandatoryColumnDelegates:list[MandatoryColumnDelegate] = []
    self.listItemDelegates       :list[ListItemDelegate]        = []
    self.listFreeDelegates       :list[ListFreeDelegate]        = []
    self.reorderColumnDelegates  :list[ReorderColumnDelegate]   = []
    self.deleteColumnDelegates   :list[DeleteColumnDelegate]    = []
    self.newWidget = QTableWidget()
    #final button box
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    #initialize
    _ = [self.selectDocType.addItem(v,k) for k,v in self.docTypesLabels]
    self.selectDocType.setCurrentIndex(0)
    return


  @Slot(str, pd.DataFrame)
  def onGetData(self, cmd:str, data:pd.DataFrame) -> None:
    """ Handle data received from backend worker
    Args:
      cmd (str): command that was sent
      data (pd.DataFrame): DataFrame containing the data
    """
    if cmd==self.cmd:
      self.df = data
      self.paint()


  def changeDocType(self, label:str) -> None:
    """ Change the item / document type

    Args:
      label (str): label of item / document type
    """
    # get data frame
    if not label:
      return
    if self.docType:
      self.finishDocType()
    self.docLabel= label
    fittingDocTypes = [k for k,v in self.docTypesLabels if v==label]
    if not fittingDocTypes:                                        #nothing to save since docType just created
      return
    self.docType = fittingDocTypes[0]
    self.cmd = 'SELECT docTypeSchema.docType, docTypeSchema.class, docTypeSchema.idx, docTypeSchema.name, '\
          'docTypeSchema.unit, docTypeSchema.mandatory, docTypeSchema.list, definitions.long '\
          'FROM docTypeSchema LEFT JOIN definitions ON definitions.key = (docTypeSchema.class || "." || docTypeSchema.name) '\
          f'WHERE docTypeSchema.docType=="{self.docType}"'
    self.comm.uiSendSQL.emit([{'type':'get_df', 'cmd':self.cmd}])

  def paint(self) -> None:
    """ Paint the dialog with the data """
    df = self.df.rename(columns={'long':'description'})
    df['item list'] = df['list'].apply(lambda x: '' if ',' in x else x)
    df['free list'] = df['list'].apply(lambda x: x  if ',' in x else '')
    df = df.drop('list', axis=1)
    df['idx'] = df['idx'].astype('int')
    # GUI
    self.tabW.clear()
    self.reorderColumnDelegates.clear()
    for group in df['class'].unique():
      data  = df[df['class']==group]
      table = QTableWidget(len(data)+1, 8)
      table.verticalHeader().hide()
      table.setAlternatingRowColors(True)
      table.setHorizontalHeaderLabels(COLUMN_NAMES)
      table.horizontalHeader().setStyleSheet('QHeaderView::section {padding: 1px; margin: 0px;}')
      for idx, width in enumerate(COLUMN_WIDTH[:-1]):
        table.setColumnWidth(idx, width)
      for _,row in data.iterrows():
        idx = int(row['idx'])
        for col in range(6):
          table.setItem(idx, col, QTableWidgetItem(row[COLUMN_NAMES[col]]))
      #Delegates to give function to row
      self.nameColumnDelegates.append(NameColumnDelegate())
      table.setItemDelegateForColumn(0, self.nameColumnDelegates[-1])
      self.mandatoryColumnDelegates.append(MandatoryColumnDelegate())
      table.setItemDelegateForColumn(3, self.mandatoryColumnDelegates[-1])
      self.listItemDelegates.append(ListItemDelegate(self.docTypesLabels))
      table.setItemDelegateForColumn(4, self.listItemDelegates[-1])
      self.listFreeDelegates.append(ListFreeDelegate())
      table.setItemDelegateForColumn(5, self.listFreeDelegates[-1])
      self.reorderColumnDelegates.append(ReorderColumnDelegate())
      table.setItemDelegateForColumn(6, self.reorderColumnDelegates[-1])
      self.deleteColumnDelegates.append(DeleteColumnDelegate())
      table.setItemDelegateForColumn(7, self.deleteColumnDelegates[-1])
      self.tabW.addTab(table, group or 'default')
    # define close buttons on some of the tabs
    self.closeButtons.clear()
    for idx in range(1, self.tabW.count()):
      self.closeButtons.append(IconButton('fa5s.times', self, [Command.DEL_GROUP,idx], None, 'Delete group'))
      self.tabW.tabBar().setTabButton(idx, QTabBar.ButtonPosition.RightSide, self.closeButtons[-1])
      header = table.horizontalHeader()
      header.setStretchLastSection(True)
    self.tabW.addTab(self.newWidget, '+')
    return


  def finishDocType(self) -> None:
    """
    Finish a docType and save to DB,
    - either by selecting another docType or by pressing save
    """
    df = self.table2schema()
    # verification: uniqueness in names. etc
    unique = ( df.groupby('class')['name'].nunique() == df.groupby('class')['name'].count()  ).all()
    if not unique:
      showMessage(self, 'Error', 'Within each table, the text in the first column has to be unique. E.g. no '
                  'two "tags" are allowed.', 'Critical')
      return
    # SAVE DATA
    dfSchema = df.drop('description', axis=1)
    dfDef = df[['class','name','description']]
    dfDef['key'] = dfDef['class']+'.'+dfDef['name']
    dfDef = dfDef.drop(['name','class'], axis=1)[['key','description']]
    dfDef.rename(columns={'description':'long'}, inplace=True)
    nonUnique = dict(dfDef.groupby(['key'])['long'].apply(lambda x: len(np.unique(x))))
    if nonUniqueStr:= ', '.join(k for k,v in nonUnique.items() if v>1):
      button = QMessageBox.question(self, 'Non unique definitions',
                                  f'The definitions are non-unique for {nonUniqueStr}. Do you want to flatten?',
                                  QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.No:
        return
    dfDef = dfDef.groupby(['key']).first()
    listDef = list(dfDef.itertuples(name=None))
    # save to sqlite
    self.comm.uiSendSQL.emit([
      {'type':'many', 'cmd':'INSERT INTO definitions (key, long, PURL) VALUES (?, ?, "") ON CONFLICT(key) DO '
                            'UPDATE SET long = excluded.long;', 'list':listDef},
      {'type':'one',  'cmd':f"DELETE FROM docTypeSchema WHERE docType == '{self.docType}'"},
      {'type':'df',   'table':'docTypeSchema', 'df':dfSchema}])
    return


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      self.finishDocType()
      if self.restartAfterClose:
        self.comm.start()
      self.accept()
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.NEW:
      dialog = DocTypeEditor(self.comm, '', self.createdNewDocType)
      dialog.exec()
    elif command[0] is Command.EDIT:
      dialog = DocTypeEditor(self.comm, self.selectDocType.currentData())
      dialog.exec()
    elif command[0] is Command.DEL:
      button = QMessageBox.question(self, 'Question', 'Do you really want to remove the doc-type?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.No:
        return
      self.comm.uiSendSQL.emit([
        {'type':'one', 'cmd':f"DELETE FROM docTypes WHERE docType == '{self.selectDocType.currentData()}'"},
        {'type':'one', 'cmd':f"DELETE FROM docTypeSchema WHERE docType == '{self.selectDocType.currentData()}'"}
      ])
      self.comm.commSendConfiguration.emit(self.comm.configuration, self.comm.projectGroup)#reset docTypes, etc.
      self.selectDocType.clear()
    elif command[0] is Command.DEL_GROUP:
      docLabel = str(self.docLabel)
      button = QMessageBox.question(self, 'Question', 'Do you really want to remove this group?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.Yes:
        group = self.tabW.tabBar().tabText(command[1])
        self.comm.uiSendSQL.emit([{'type':'one','cmd':
          f"DELETE FROM docTypeSchema WHERE docType == '{self.docType}' AND class == '{group}'"}])
        self.changeDocType(docLabel)
    return


  def table2schema(self) -> pd.DataFrame:
    """ save text content of tables """
    df = pd.DataFrame()
    lastRow = 0
    for tabID in range(self.tabW.count()-1):                                           # -1: ignore last tab +
      group = self.tabW.tabBar().tabText(tabID)
      group = '' if group=='default' else group
      widget:QTableWidget = self.tabW.widget(tabID)                                 # type: ignore[assignment]
      for row in range(widget.rowCount()-1):                   # -1: ignore last row as it is meant for adding
        df.at[lastRow, 'docType'] = self.docType
        df.at[lastRow, 'class']   = group
        df.at[lastRow, 'idx']     = str(row)
        for col in range(6):
          item = widget.item(row,col)
          df.at[lastRow, COLUMN_NAMES[col]] = '' if item is None else item.text()
        lastRow += 1
    df['list'] = df['item list']+df['free list']
    df.drop(['item list','free list'], axis=1, inplace=True)
    return df


  def renameTab(self, idx:int) -> None:
    """ rename tab after double clicking

    Args:
      idx (int): index of the tab
    """
    if 0 < idx <self.tabW.count()-1:
      textOld = self.tabW.tabText(idx)
      textNew, ok = QInputDialog.getText(self, 'Rename group', 'Enter new group name:', text=textOld)
      if ok and textNew.strip():
        self.tabW.setTabText(idx, textNew.strip())
    return


  def createNewTab(self, idx:int) -> None:
    """ Create new group

    Args:
      idx (int): index of the tab
    """
    if idx == self.tabW.count()-1:
      textNew, ok = QInputDialog.getText(self, 'Create group', 'Enter new group name:', text='')
      if ok and textNew.strip():
        self.comm.uiSendSQL.emit([{'type':'one',
                                   'cmd':f"INSERT INTO docTypeSchema VALUES ({', '.join(['?']*7)})",
                                   'list':[self.docType, textNew.strip(), '0', 'item', '', '', '']}])
        self.docType = ''                               # prevent self.finishDocType from deleting new entries
        self.changeDocType(self.docLabel)
    return


  def createdNewDocType(self,label:str, docType:str) -> None:
    """ Callback function to change docType after creating a new one

    Args:
      label (str): label of the new docType
      docType (str): name of the new docType
    """
    if docType not in [self.selectDocType.itemData(i) for i in range(self.selectDocType.count())]:
      self.selectDocType.addItem(label, docType)
    self.restartAfterClose = True
    self.selectDocType.setCurrentText(label)
    return

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
  NEW          = 1
  DEL          = 2
  EDIT         = 3
  DEL_GROUP    = 4
