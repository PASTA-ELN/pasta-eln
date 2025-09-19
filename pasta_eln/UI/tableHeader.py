""" Table Header dialog: change which columns are shown and in which order """
import logging
from collections import defaultdict
from enum import Enum
from typing import Any
import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QComboBox, QListWidget, QVBoxLayout
from ..backendWorker.sqlite import MAIN_ORDER
from ..backendWorker.worker import Task
from ..fixedStringsJson import tableHeaderHelp
from .guiCommunicate import Communicate
from .guiStyle import IconButton, widgetAndLayout
from .messageDialog import showMessage


class TableHeader(QDialog):
  """ Table Header dialog: change which columns are shown and in which order """
  def __init__(self, comm:Communicate, docType:str):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      docType (string):  document type
    """
    super().__init__()
    self.comm    = comm
    self.docType = docType
    self.allSet  = set(MAIN_ORDER)
    self.allSet  = {i[1:] if i[0]=='.' else i for i in self.allSet}
    self.selectedList:list[str] = []
    self.otherDict:dict[str, list[str]] = {}

    # GUI elements
    self.setWindowTitle('Select list columns')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    _, bodyL = widgetAndLayout('H', mainL, spacing='m')

    _, leftL = widgetAndLayout('V', bodyL, spacing='m')
    self.choicesW = QListWidget()
    self.choicesW.setMinimumHeight(250)
    leftL.addWidget(self.choicesW)
    _, otherL = widgetAndLayout('H', leftL, spacing='s')
    self.other1 = QComboBox()
    self.other1.addItems(sorted(self.otherDict.keys()))
    self.other1.currentTextChanged.connect(self.changeCB1)
    otherL.addWidget(self.other1)
    self.other2 = QComboBox()
    self.other2.addItems(self.otherDict.get(self.other1.currentText(),[]))
    self.other2.activated.connect(self.changeCB2)
    otherL.addWidget(self.other2)

    _, centerL = widgetAndLayout('V', bodyL)
    IconButton('fa5s.angle-right',        self, [Command.ADD],       centerL, 'add to right')
    IconButton('fa5s.angle-left',         self, [Command.DELETE],    centerL, 'delete from right')
    IconButton('fa5s.angle-up',           self, [Command.MOVE_UP],   centerL, 'move up')
    IconButton('fa5s.angle-down',         self, [Command.MOVE_DOWN], centerL, 'move down')
    self.selectW = QListWidget()
    bodyL.addWidget(self.selectW)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Help)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)
    # request data
    self.comm.backendThread.worker.beSendSQL.connect(self.onGetData)
    self.sqlCmd1 = f'SELECT view FROM docTypes WHERE docType LIKE "{docType}%"'
    self.sqlCmd2 = f'SELECT DISTINCT properties.key FROM properties JOIN main USING(id) WHERE main.type LIKE "{docType}%"'
    self.comm.uiSendSQL.emit([{'type':'get_df', 'cmd':self.sqlCmd1}])
    self.comm.uiSendSQL.emit([{'type':'get_df', 'cmd':self.sqlCmd2}])



  @Slot(str, pd.DataFrame)
  def onGetData(self, cmd:str, data:pd.DataFrame) -> None:
    """ Callback function to handle the received data
    Args:
      cmd (str): command that was sent
      data (pd.DataFrame): DataFrame containing table
    """
    if cmd == self.sqlCmd1:
      self.selectedList = data.values[0][0].split(',')
      self.selectedList = [i[1:] if i[0]=='.' else i for i in self.selectedList]
      self.allSet       = self.allSet.union(self.selectedList)
      self.paint()
    elif cmd == self.sqlCmd2:
      otherList = [i.split('.', 1) for i in data['key'].to_list()]
      otherDict = defaultdict(set)
      for k,v in otherList:
        otherDict[k].add(v)
      self.otherDict = {k:sorted(v) for k,v in otherDict.items()}
      self.other1.clear()
      self.other2.clear()
      self.other1.addItems(sorted(self.otherDict.keys()))
      self.other2.addItems(self.otherDict.get(self.other1.currentText(),[]))


  def paint(self) -> None:
    """ Paint the dialog with the current data """
    self.choicesW.clear()
    self.selectW.clear()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    self.selectW.addItems(self.selectedList)


  def execute(self, command:list[Any]) -> None:
    """
    Event if user clicks button in the center

    Args:
      command (list): list of commands
    """
    selectedLeft   = [i.text() for i in self.choicesW.selectedItems()]
    selectedRight  = [i.text() for i in self.selectW.selectedItems()]
    oldIndex, newIndex = -1, -1
    if command[0] is Command.ADD:
      self.selectedList += selectedLeft
    elif command[0] is Command.DELETE:
      self.selectedList = [i for i in self.selectedList if i not in selectedRight or i in ['name'] ]
    elif command[0] is Command.MOVE_UP  and len(selectedRight)==1:
      oldIndex = self.selectedList.index(selectedRight[0])
      if oldIndex>0:
        newIndex = oldIndex-1
    elif command[0] is Command.MOVE_DOWN and len(selectedRight)==1:
      oldIndex = self.selectedList.index(selectedRight[0])
      if oldIndex<len(self.selectedList)-1:
        newIndex = oldIndex+1
    else:
      logging.error('Menu unknown: %s',command, exc_info=True)
    #change content
    if oldIndex>-1 and newIndex>-1:
      self.selectedList.insert(newIndex, self.selectedList.pop(oldIndex))
    self.choicesW.clear()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    self.selectW.clear()
    self.selectW.addItems(self.selectedList)
    if oldIndex>-1 and newIndex>-1:
      self.selectW.setCurrentRow(newIndex)
    return

  def changeCB1(self, text:str) -> None:
    """ change content of 2nd combobox based on 1st combobox
    Args:
      text (str): text of 1st combobox
    """
    self.other2.clear()
    self.other2.addItems(self.otherDict.get(text,[]))
    return

  def changeCB2(self, idx:int) -> None:
    """ add entry to the right list
    Args:
      idx (int): index of 2nd combobox
    """
    newEntry = f'{self.other1.currentText()}.{self.other2.itemText(idx)}'
    if newEntry not in self.selectedList:
      self.selectedList.append(newEntry)
      self.paint()
    return


  def closeDialog(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      newList = [i if i in MAIN_ORDER+['tags','qrCodes'] or '.' in i else f'.{i}' for i in self.selectedList]
      self.comm.uiRequestTask.emit(Task.SEND_TBL_COLUMN, {'docType':self.docType, 'newList':newList})
      self.accept()
    elif btn.text().endswith('Help'):
      showMessage(self, 'Help on individual entry', tableHeaderHelp)
    else:
      print('dialogTableHeader: did not get a fitting btn ',btn.text())
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
  ADD       = 1
  DELETE    = 2
  MOVE_UP   = 3
  MOVE_DOWN = 4
  USE_TEXT  = 5
