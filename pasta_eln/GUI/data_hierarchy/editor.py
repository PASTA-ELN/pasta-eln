""" dialog to edit docType schema """
import re
from enum import Enum
from typing import Any
from PySide6.QtWidgets import (QComboBox, QDialog, QTableWidget, QTableWidgetItem,  # pylint: disable=no-name-in-module
                               QTabWidget, QVBoxLayout, QTabWidget, QDialogButtonBox, QWidget, QMessageBox)
from .mandatory_column_delegate import MandatoryColumnDelegate
from .reorder_column_delegate   import ReorderColumnDelegate
from .delete_column_delegate    import DeleteColumnDelegate
from .name_column_delegate      import NameColumnDelegate
from ...guiCommunicate import Communicate
from ...guiStyle import (IconButton, Label, TextButton, showMessage, widgetAndLayout)
from .docTypeEdit import DocTypeEditor

#                0       1            2      3           4      5         6
COLUMN_NAMES = ['name','description','unit','mandatory','list','move up','delete']
COLUMN_WIDTH = [100,   250,          100,   50,         245,   55,       50]

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
    docTypes = self.db.dataHierarchy('','')
    self.docType = ''
    # GUI elements
    self.setMinimumWidth(900)
    mainL = QVBoxLayout(self)
    Label('Schema-editor for document types', 'h1', mainL)
    _, docTypeL = widgetAndLayout('H', mainL, 's')
    self.selectDocType = QComboBox()
    self.selectDocType.addItems(docTypes)
    self.selectDocType.currentTextChanged.connect(self.changeDocType)
    docTypeL.addWidget(self.selectDocType)
    docTypeL.addStretch(1)
    IconButton('fa5s.plus',  self, [Command.NEW],  docTypeL, tooltip='New document type')
    IconButton('fa5s.edit',  self, [Command.EDIT], docTypeL, tooltip='Edit document type')
    IconButton('fa5s.trash', self, [Command.DEL],  docTypeL, tooltip='Delete document type')

    # tabs: empty
    self.tabW = QTabWidget(self)
    mainL.addWidget(self.tabW)
    self.nameColumnDelegate     = NameColumnDelegate()
    self.nameColumnDelegate.add_row_signal.connect(self.addRow)
    self.requiredColumnDelegate = MandatoryColumnDelegate()
    self.reorderColumnDelegate  = ReorderColumnDelegate()
    self.reorderColumnDelegate.re_order_signal.connect(self.reorderRows)
    self.deleteColumnDelegate   = DeleteColumnDelegate()
    self.deleteColumnDelegate.delete_clicked_signal.connect(self.deleteRow)
    self.newWidget = QWidget()

    #final button box
    mainL.addStretch(1)
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    self.selectDocType.setCurrentText('x0')


  def closeDialog(self, btn:TextButton):
    """
    cancel or save entered data

    Args:
      btn (QButton): save or cancel button
    """
    if btn.text().endswith('Cancel'):
      self.reject()


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    if command[0] is Command.NEW:
      dialog = DocTypeEditor(self.comm, '')
      dialog.exec()
    if command[0] is Command.EDIT:
      dialog = DocTypeEditor(self.comm, self.selectDocType.currentText())
      dialog.exec()
    if command[0] is Command.DEL:
      button = QMessageBox.question(self, 'Question', 'Do you really want to remove the doc-type?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.No:
          return
      self.comm.backend.db.cursor.execute(f"DELETE FROM docTypes WHERE docType == '{self.selectDocType.currentText()}'")
      self.comm.backend.db.cursor.execute(f"DELETE FROM docTypeSchema WHERE docType == '{self.selectDocType.currentText()}'")
      self.comm.backend.db.connection.commit()
    return


  def changeDocType(self, item:str) -> None:
    """ Change the document type

    Args:
      item (str): name of document type
    """
    self.schema = self.db.dataHierarchy(item, 'meta')
    self.groups = self.db.dataHierarchy(item, 'metaColumns')
    self.docType = item
    self.redrawTabW()
    return


  def redrawTabW(self) -> None:
    """ Redraw tab-widget """
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
        table.setItem(idx, 2, QTableWidgetItem(row['unit']))
        table.setItem(idx, 3, QTableWidgetItem(row['mandatory']))
        table.setItem(idx, 4, QTableWidgetItem(row['list']))
      #Delegates to give function to row
      table.setItemDelegateForColumn(0, self.nameColumnDelegate)
      table.setItemDelegateForColumn(3, self.requiredColumnDelegate)
      table.setItemDelegateForColumn(5, self.reorderColumnDelegate)
      table.setItemDelegateForColumn(6, self.deleteColumnDelegate)
      self.tabW.addTab(table, group or 'default')
    self.tabW.addTab(self.newWidget, '+')
    return


  def reorderRows(self, row:int) -> None:
    """
    Re-order the data rows: row will be moved up

    Args:
      row (int): row of the data to be shifted up.
    """
    if row>0:
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
      group = self.groups[self.tabW.currentIndex()]
      self.schema = [ i|{'idx':str(int(i['idx'])-1)} if i['class']==group and int(i['idx'])>row else i for i in self.schema
                                                 if not(i['class']==group and i['idx']==str(row))]
      self.redrawTabW()
    return


  def addRow(self) -> None:
    """
    Add a data row

    Args:
      row (int): row that is edited
    """
    group  = self.groups[self.tabW.currentIndex()]
    newIdx = self.tabW.currentWidget().rowCount()-1
    name   = self.tabW.currentWidget().currentItem().text()
    self.schema += [{'docType':self.docType, 'class':group, 'idx':str(newIdx), 'name':name,
                     'unit': '', 'mandatory': '', 'list': ''}]
    self.redrawTabW()
    return


class Command(Enum):
  """ Commands used in this file """
  NEW          = 1
  DEL          = 2
  EDIT         = 3
