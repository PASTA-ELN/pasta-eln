""" dialog to edit docType schema """
import sqlite3
from enum import Enum
from typing import Any
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
    self.schema:list[dict[str,str]] = [{}]  # entire schema of this docType
    self.groups = ['']  # group names
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
    elif btn.text().endswith('Save') and self.saveDocTypeSchema():
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
        group = self.groups[command[1]]
        self.schema = [i for i in self.schema if i['class']!=group]
        self.groups.remove(group)
        self.redrawTabW()
    return


  def redrawTabW(self) -> None:
    """ Redraw tab-widget: all tables """
    self.tabW.clear()
    for group in self.groups:
      data  = [i for i in self.schema if i['class']==group]
      self.nameColumnDelegate.numRows    = len(data)
      self.reorderColumnDelegate.numRows = len(data)
      self.deleteColumnDelegate.numRows  = len(data)
      table = QTableWidget(len(data)+1, 7)
      table.verticalHeader().hide()
      table.setAlternatingRowColors(True)
      table.setHorizontalHeaderLabels(COLUMN_NAMES)
      for idx, width in enumerate(COLUMN_WIDTH):
        table.setColumnWidth(idx, width)
      for row in data:
        idx = int(row['idx'])
        table.setItem(idx, 0, QTableWidgetItem(row['name']))
        table.setItem(idx, 1, QTableWidgetItem(row['long']))
        table.setItem(idx, 2, QTableWidgetItem(row['unit']))
        table.setItem(idx, 3, QTableWidgetItem(row['mandatory']))
        table.setItem(idx, 4, QTableWidgetItem(row['list']))
      #Delegates to give function to row
      table.setItemDelegateForColumn(0, self.nameColumnDelegate)
      table.setItemDelegateForColumn(3, self.requiredColumnDelegate)
      table.setItemDelegateForColumn(5, self.reorderColumnDelegate)
      table.setItemDelegateForColumn(6, self.deleteColumnDelegate)
      self.tabW.addTab(table, group or 'default')
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
    if self.docType and docType!=self.docType and not self.saveDocTypeSchema():
      self.selectDocType.setCurrentText(self.docType)
      return
    # get schema by custom command as general does not exist that includes the definition
    self.db.connection.row_factory = sqlite3.Row
    cursor = self.db.connection.cursor()
    cursor.execute('SELECT docTypeSchema.docType, docTypeSchema.class, docTypeSchema.idx, docTypeSchema.name, '
                  'docTypeSchema.unit, docTypeSchema.mandatory, docTypeSchema.list, definitions.long '
                  'FROM docTypeSchema LEFT JOIN definitions ON docTypeSchema.name = definitions.key '
                  f'WHERE docType == "{docType}"')
    self.schema = [dict(i) for i in cursor.fetchall()]
    self.groups = self.db.dataHierarchy(docType, 'metaColumns')
    self.docType = docType
    self.redrawTabW()
    return


  def saveDocTypeSchema(self) -> bool:
    """ Save table information to database """
    # TODO start verification: uniqueness in names (some do test on save)
    # SAVE
    print("TODO: implement save")
    return True


  def table2schema(self) -> None:
    """ save text content of tables
    - should be executed at each function that calls redrawTabW
    """
    for tabID in range(self.tabW.count()-1):  # -1: ignore last tab +
      group = self.tabW.tabBar().tabText(tabID)
      group = '' if group=='default' else group
      widget:QTableWidget = self.tabW.widget(tabID) # type: ignore[assignment]
      for row in range(widget.rowCount()-1):  # -1: ignore last row as it is meant for adding
        thisRow = {'docType':self.docType, 'class':group, 'idx':str(row)}
        for col in range(5):
          item = widget.item(row,col)
          thisRow[COLUMN_NAMES[col]] = '' if item is None else item.text()
        thisRow['long'] = thisRow.pop('description')
        self.schema = [thisRow if i['class']==group and i['idx']==str(row) else i for i in self.schema]
    return


  def reorderRows(self, row:int) -> None:
    """
    Re-order the data rows: row will be moved up

    Args:
      row (int): row of the data to be shifted up.
    """
    if row>0:
      self.table2schema()
      group = self.groups[self.tabW.currentIndex()]
      self.schema = [ i|{'idx':str(row-1)} if i['class']==group and i['idx']==str(row)   else
                     (i|{'idx':str(row)}   if i['class']==group and i['idx']==str(row-1) else i) for i in self.schema]
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
      group = self.groups[self.tabW.currentIndex()]
      self.schema = [ i|{'idx':str(int(i['idx'])-1)} if i['class']==group and int(i['idx'])>row else i for i in self.schema
                                                 if not(i['class']==group and i['idx']==str(row))]
      self.redrawTabW()
    return


  def addRow(self) -> None:
    """
    Add a data row
    """
    self.table2schema()
    group  = self.groups[self.tabW.currentIndex()]
    widget:QTableWidget  = self.tabW.currentWidget()   # type: ignore[assignment]
    newIdx = widget.rowCount()-1
    name   = widget.currentItem().text()
    self.schema += [{'docType':self.docType, 'class':group, 'idx':str(newIdx), 'name':name,
                     'unit': '', 'mandatory': '', 'list': '', 'long':''}]
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
        self.schema = [ i|{'class':textNew.strip() if i['class']==textOld else i['class']} for i in self.schema]
        self.groups[self.groups.index(textOld)] = textNew
    return


  def createNewTab(self, idx:int) -> None:
    """ Create new group

    Args:
      idx (int): index of the tab
    """
    if idx == self.tabW.count()-1:
      textNew, ok = QInputDialog.getText(self, "Create group", "Enter new group name:", text='')
      if ok and textNew.strip():
        self.groups.append(textNew.strip())
        self.redrawTabW()
    return


class Command(Enum):
  """ Commands used in this file """
  NEW          = 1
  DEL          = 2
  EDIT         = 3
  DEL_GROUP    = 4
