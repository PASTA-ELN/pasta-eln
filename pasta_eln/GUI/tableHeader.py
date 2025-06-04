""" Table Header dialog: change which columns are shown and in which order """
from enum import Enum
from typing import Any
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLineEdit, QListWidget,  # pylint: disable=no-name-in-module
                               QVBoxLayout)
from ..fixedStringsJson import tableHeaderHelp
from ..guiCommunicate import Communicate
from ..guiStyle import IconButton, showMessage, widgetAndLayout
from ..miscTools import restart
from ..sqlite import MAIN_ORDER


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
    self.comm = comm
    self.docType = docType
    self.db = self.comm.backend.db
    self.selectedList = self.db.dataHierarchy(docType,'view')
    self.allSet = set(MAIN_ORDER)
    #clean it
    self.allSet       = {i[1:] if i[0]=='.' else i for i in self.allSet}
    self.selectedList = [i[1:] if i[0]=='.' else i for i in self.selectedList]
    self.allSet       = self.allSet.union(self.selectedList)

    # GUI elements
    self.setWindowTitle('Select table headers')
    self.setMinimumWidth(600)
    mainL = QVBoxLayout(self)
    _, bodyL = widgetAndLayout('H', mainL)
    _, leftL = widgetAndLayout('V', bodyL, spacing='m')
    self.choicesW = QListWidget()
    self.choicesW.addItems(list(self.allSet.difference(self.selectedList)))
    leftL.addWidget(self.choicesW)
    self.inputLine = QLineEdit()
    self.inputLine.setStyleSheet(self.comm.palette.get('secondaryText', 'color'))
    leftL.addWidget(self.inputLine)
    _, centerL = widgetAndLayout('V', bodyL)
    IconButton('fa5s.angle-right',        self, [Command.ADD],      centerL, 'add to right')
    IconButton('fa5s.angle-left',         self, [Command.DELETE],   centerL, 'delete from right')
    IconButton('fa5s.angle-up',           self, [Command.MOVE_UP],  centerL, 'move up')
    IconButton('fa5s.angle-down',         self, [Command.MOVE_UP],  centerL, 'move down')
    IconButton('fa5s.angle-double-right', self, [Command.USE_TEXT], centerL, 'use text field')
    self.selectW = QListWidget()
    self.selectW.addItems(self.selectedList)
    bodyL.addWidget(self.selectW)
    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Help)
    buttonBox.clicked.connect(self.closeDialog)
    mainL.addWidget(buttonBox)


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
    elif command[0] is Command.USE_TEXT and self.inputLine.text()!='':
      self.selectedList += [self.inputLine.text()]
      self.allSet.add(self.inputLine.text())
    else:
      print('**ERROR tableHeader menu unknown:',command)
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


  def closeDialog(self, btn:IconButton) -> None:
    """ save selectedList to configuration and exit """
    if btn.text().endswith('Cancel'):
      self.reject()
    elif btn.text().endswith('Save'):
      self.selectedList = [f'.{i}' if i not in MAIN_ORDER and '.' not in i else i for i in self.selectedList]
      self.db.dataHierarchyChangeView(self.docType, self.selectedList)
      restart()
    elif btn.text().endswith('Help'):
      showMessage(self, 'Help on individual entry', tableHeaderHelp)
    else:
      print('dialogTableHeader: did not get a fitting btn ',btn.text())
    return


class Command(Enum):
  """ Commands used in this file """
  ADD       = 1
  DELETE    = 2
  MOVE_UP   = 3
  MOVE_DOWN = 4
  USE_TEXT  = 5
