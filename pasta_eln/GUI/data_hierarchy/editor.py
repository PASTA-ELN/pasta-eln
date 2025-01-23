""" dialog to edit docType schema """
import re
from enum import Enum
from typing import Any
from PySide6.QtWidgets import (QComboBox, QDialog, QTableWidget, QTableWidgetItem,  # pylint: disable=no-name-in-module
                               QTabWidget, QVBoxLayout, QTabWidget, QDialogButtonBox, QWidget, QMessageBox)
from .mandatory_column_delegate import MandatoryColumnDelegate
from .reorder_column_delegate import ReorderColumnDelegate
from .delete_column_delegate import DeleteColumnDelegate
from ...guiCommunicate import Communicate
from ...guiStyle import (IconButton, Label, TextButton, showMessage, widgetAndLayout)
from .docTypeEdit import DocTypeEditor

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
    self.requiredColumnDelegate = MandatoryColumnDelegate()
    self.reorderColumnDelegate  = ReorderColumnDelegate()
    self.deleteColumnDelegate   = DeleteColumnDelegate()
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


  def changeDocType(self, item:str):
    """
    change the document type

    Args:
      item (str): name of document type
    """
    self.tabW.clear()
    schema = self.db.dataHierarchy(item, 'meta')
    groups = self.db.dataHierarchy(item, 'metaColumns')
    for group in groups:
      table = QTableWidget(64, 7)
      #                                0       1            2      3           4      5         6
      table.setHorizontalHeaderLabels(['name','description','unit','mandatory','list','move up','delete'])
      table.verticalHeader().hide()
      table.setAlternatingRowColors(True)
      table.setColumnWidth(0, 100)
      table.setColumnWidth(1, 250)
      table.setColumnWidth(2, 100)
      table.setColumnWidth(3, 50)
      table.setColumnWidth(4, 245)
      table.setColumnWidth(5, 55)
      table.setColumnWidth(6, 50)
      for idx, row in enumerate(i for i in schema if i['class']==group):
        table.setItem(idx, 0, QTableWidgetItem(row['name']))
        table.setItem(idx, 2, QTableWidgetItem(row['unit']))
        table.setItem(idx, 3, QTableWidgetItem(row['mandatory']))
        table.setItem(idx, 4, QTableWidgetItem(row['list']))
      #Delegates to give function to row
      table.setItemDelegateForColumn(3, self.requiredColumnDelegate)
      table.setItemDelegateForColumn(5, self.reorderColumnDelegate)
      table.setItemDelegateForColumn(6, self.deleteColumnDelegate)
      self.tabW.addTab(table, group or 'default')
    self.tabW.addTab(self.newWidget, '+')
    return


class Command(Enum):
  """ Commands used in this file """
  NEW          = 1
  DEL          = 2
  EDIT         = 3
