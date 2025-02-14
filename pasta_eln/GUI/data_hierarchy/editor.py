""" dialog to edit docType schema """
from enum import Enum
from typing import Any
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (QComboBox, QDialog, QTableWidget, QTableWidgetItem,  # pylint: disable=no-name-in-module
                               QTabWidget, QVBoxLayout, QDialogButtonBox, QMessageBox, QInputDialog, QTabBar)
from .mandatory_column_delegate import MandatoryColumnDelegate
from .reorder_column_delegate   import ReorderColumnDelegate
from .delete_column_delegate    import DeleteColumnDelegate
from .name_column_delegate      import NameColumnDelegate
from ...guiCommunicate import Communicate
from ...guiStyle import (IconButton, Label, TextButton, widgetAndLayout)
from .docTypeEdit import DocTypeEditor

#                0       1            2      3           4      5         6
COLUMN_NAMES = ['name','description','unit','mandatory','list','move up','delete']
COLUMN_WIDTH = [100,   250,          100,   50,         245,   60,       50]
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
    self.db   = self.comm.backend.db
    self.docType = ''
    cmd = 'SELECT docTypeSchema.docType, docTypeSchema.class, docTypeSchema.idx, docTypeSchema.name, '\
          'docTypeSchema.unit, docTypeSchema.mandatory, docTypeSchema.list, definitions.long '\
          'FROM docTypeSchema LEFT JOIN definitions ON definitions.key = (docTypeSchema.class || "." || docTypeSchema.name)'
    self.df = pd.read_sql_query(cmd, self.db.connection).fillna('')
    self.df.rename(columns={'long':'description'}, inplace=True)
    self.df['idx'] = self.df['idx'].astype('int')
    self.closeButtons:list[IconButton] = []  #close buttons of tabs

    # GUI elements
    self.setMinimumWidth(905)
    self.setMinimumHeight(500)
    mainL = QVBoxLayout(self)
    Label('Schema-editor for document types', 'h1', mainL)
    Label('Warning: verification not fully implemented yet', 'h2', mainL)
    _, docTypeL = widgetAndLayout('H', mainL, 's')
    self.selectDocType = QComboBox()
    docTypes = self.db.dataHierarchy('','')
    self.selectDocType.addItems(docTypes)
    self.selectDocType.currentTextChanged.connect(self.changeDocType)
    docTypeL.addWidget(self.selectDocType)
    docTypeL.addStretch(1)
    IconButton('fa5s.plus',  self, [Command.NEW],  docTypeL, tooltip='New document type')
    IconButton('fa5s.edit',  self, [Command.EDIT], docTypeL, tooltip='Edit document type')
    IconButton('fa5s.trash', self, [Command.DEL],  docTypeL, tooltip='Delete document type')

    # tabs: empty
    self.tabW = QTabWidget(self)
    self.tabW.tabBarDoubleClicked.connect(self.renameTab)
    self.tabW.tabBarClicked.connect(self.createNewTab)
    mainL.addWidget(self.tabW, stretch=10)
    self.nameColumnDelegate     = NameColumnDelegate()
    self.nameColumnDelegate.add_row_signal.connect(self.addRow)
    self.requiredColumnDelegate = MandatoryColumnDelegate()
    self.reorderColumnDelegate  = ReorderColumnDelegate()
    self.reorderColumnDelegate.re_order_signal.connect(self.reorderRows)
    self.deleteColumnDelegate   = DeleteColumnDelegate()
    self.deleteColumnDelegate.delete_clicked_signal.connect(self.deleteRow)
    self.newWidget = QTableWidget()

    #final button box
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    self.selectDocType.setCurrentText('x0')


  def closeDialog(self, btn:TextButton) -> None:
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      self.table2schema()
      # TODO start verification: uniqueness in names (some do test before save)
      # - in each table, name has to be unique
      # - .qrCodes, .chemistry?

      # SAVE DATA
      dfSchema = self.df.drop('description', axis=1)
      dfDef = self.df[['class','name','description']]
      dfDef['key'] = dfDef['class']+'.'+dfDef['name']
      dfDef = dfDef.drop(['name','class'], axis=1)[['key','description']]
      dfDef.rename(columns={'description':'long'}, inplace=True)
      nonUnique = dict(dfDef.groupby(['key']).apply(lambda x: len(np.unique(x))))
      if nonUniqueStr:= ', '.join(k for k,v in nonUnique.items() if v>2):
        button = QMessageBox.question(self, 'Non unique definitions',
                                   f'The definitions are non-unique for {nonUniqueStr}. Do you want to flatten?',
                                   QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if button == QMessageBox.StandardButton.No:
          return
      dfDef = dfDef.groupby(['key']).first()
      listDef = list(dfDef.itertuples(name=None))
      # save to sqlite
      dfSchema.to_sql('docTypeSchema', self.db.connection, if_exists='replace', index=False, dtype='str')
      cmd = 'INSERT INTO definitions (key, long, PURL) VALUES (?, ?, "") ON CONFLICT(key) DO '\
            'UPDATE SET long = excluded.long;'
      self.db.cursor.executemany(cmd, listDef)
      self.db.connection.commit()
      self.accept()
    return


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.NEW:
      dialog = DocTypeEditor(self.comm, '')
      dialog.exec()
    elif command[0] is Command.EDIT:
      dialog = DocTypeEditor(self.comm, self.selectDocType.currentText())
      dialog.exec()
    elif command[0] is Command.DEL:
      button = QMessageBox.question(self, 'Question', 'Do you really want to remove the doc-type?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.No:
        return
      self.comm.backend.db.cursor.execute(f"DELETE FROM docTypes WHERE docType == '{self.selectDocType.currentText()}'")
      self.comm.backend.db.cursor.execute(f"DELETE FROM docTypeSchema WHERE docType == '{self.selectDocType.currentText()}'")
      self.comm.backend.db.connection.commit()
    elif command[0] is Command.DEL_GROUP:
      button = QMessageBox.question(self, 'Question', 'Do you really want to remove this group?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.Yes:
        self.table2schema()
        group = self.tabW.tabBar().tabText(command[1])
        self.df = self.df[self.df['class']!=group]
        self.redrawTabW()
    return


  def redrawTabW(self) -> None:
    """ Redraw tab-widget: all tables """
    self.tabW.clear()
    df = self.df[self.df['docType']==self.docType]
    for group in df['class'].unique():
      data  = df[df['class']==group]
      self.nameColumnDelegate.numRows    = len(data)
      self.reorderColumnDelegate.numRows = len(data)
      self.deleteColumnDelegate.numRows  = len(data)
      table = QTableWidget(len(data)+1, 7)
      table.verticalHeader().hide()
      table.setAlternatingRowColors(True)
      table.setHorizontalHeaderLabels(COLUMN_NAMES)
      for idx, width in enumerate(COLUMN_WIDTH):
        table.setColumnWidth(idx, width)
      for _,row in data.iterrows():
        idx = int(row['idx'])
        for col in range(5):
          table.setItem(idx, col, QTableWidgetItem(row[COLUMN_NAMES[col]]))
      #Delegates to give function to row
      table.setItemDelegateForColumn(0, self.nameColumnDelegate)
      table.setItemDelegateForColumn(3, self.requiredColumnDelegate)
      table.setItemDelegateForColumn(5, self.reorderColumnDelegate)
      table.setItemDelegateForColumn(6, self.deleteColumnDelegate)
      self.tabW.addTab(table, group or 'default')
    # define close buttons on some of the tabs
    self.closeButtons.clear()
    for idx in range(1, self.tabW.count()):
      self.closeButtons.append(IconButton('fa5s.times', self, [Command.DEL_GROUP,idx], None, 'Delete group'))
      self.tabW.tabBar().setTabButton(idx, QTabBar.ButtonPosition.RightSide, self.closeButtons[-1])
    self.tabW.addTab(self.newWidget, '+')
    return


  def changeDocType(self, docType:str) -> None:
    """ Change the document type

    Args:
      docType (str): name of document type
    """
    self.docType = docType
    self.redrawTabW()
    return



  def table2schema(self) -> None:
    """ save text content of tables
    - should be executed at each function that calls redrawTabW
    """
    for tabID in range(self.tabW.count()-1):  # -1: ignore last tab +
      group = self.tabW.tabBar().tabText(tabID)
      group = '' if group=='default' else group
      widget:QTableWidget = self.tabW.widget(tabID) # type: ignore[assignment]
      for row in range(widget.rowCount()-1):  # -1: ignore last row as it is meant for adding
        for col in range(5):
          item = widget.item(row,col)
          self.df.at[row, COLUMN_NAMES[col]] = '' if item is None else item.text()
    return


  def reorderRows(self, row:int) -> None:
    """
    Re-order the data rows: row will be moved up

    Args:
      row (int): row of the data to be shifted up.
    """
    if row>0:
      self.table2schema()
      group = self.tabW.tabBar().tabText(self.tabW.currentIndex())
      group = '' if group=='default' else group
      column= (self.df['docType']==self.docType) & (self.df['class']==group)
      self.df.loc[column & (self.df['idx']==row),   'idx']=-1
      self.df.loc[column & (self.df['idx']==row-1), 'idx']=row
      self.df.loc[column & (self.df['idx']==-1),    'idx']=row-1
      self.df = self.df.sort_values('idx').reset_index(drop=True)
      self.redrawTabW()
    return


  def deleteRow(self, row:int) -> None:
    """
    Delete the data row

    Args:
      row (int): row will be deleted
    """
    if row>0:
      self.table2schema()
      group = self.tabW.tabBar().tabText(self.tabW.currentIndex())
      group = '' if group=='default' else group
      column= (self.df['docType']==self.docType) & (self.df['class']==group)
      self.df = self.df.drop(self.df[column & (self.df['idx']==row)].index)
      self.df.loc[column & (self.df['idx']>row), 'idx'] -= 1
      self.redrawTabW()
    return


  def addRow(self) -> None:
    """
    Add a data row
    """
    self.table2schema()
    group = self.tabW.tabBar().tabText(self.tabW.currentIndex())
    group = '' if group=='default' else group
    widget:QTableWidget  = self.tabW.currentWidget()   # type: ignore[assignment]
    newIdx = widget.rowCount()-1
    name   = widget.currentItem().text()
    newRow = {'docType':self.docType, 'class':group, 'idx':newIdx, 'name':name,
              'unit': '', 'mandatory': '', 'list': '', 'description':''}
    self.df = pd.concat([self.df, pd.DataFrame([newRow])], ignore_index=True)
    self.redrawTabW()
    return


  def renameTab(self, idx:int) -> None:
    """ rename tab after double clicking

    Args:
      idx (int): index of the tab
    """
    if 0 < idx <self.tabW.count()-1:
      textOld = self.tabW.tabText(idx)
      textNew, ok = QInputDialog.getText(self, "Rename group", "Enter new group name:", text=textOld)
      if ok and textNew.strip():
        self.tabW.setTabText(idx, textNew.strip())
        column= (self.df['docType']==self.docType) & (self.df['class']==textOld)
        self.df.loc[column, 'class'] = textNew
    return


  def createNewTab(self, idx:int) -> None:
    """ Create new group

    Args:
      idx (int): index of the tab
    """
    if idx == self.tabW.count()-1:
      textNew, ok = QInputDialog.getText(self, "Create group", "Enter new group name:", text='')
      if ok and textNew.strip():
        newRow = {'docType':self.docType, 'class':textNew.strip(), 'idx':0, 'name':'item',
              'unit': '', 'mandatory': '', 'list': '', 'description':''}
        self.df = pd.concat([self.df, pd.DataFrame([newRow])], ignore_index=True)
        self.redrawTabW()
    return


class Command(Enum):
  """ Commands used in this file """
  NEW          = 1
  DEL          = 2
  EDIT         = 3
  DEL_GROUP    = 4
