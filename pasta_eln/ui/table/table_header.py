"""Dialog for choosing and ordering the columns displayed in a document list."""
from collections import defaultdict
from enum import Enum, auto
import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QListWidget, QVBoxLayout, QWidget
from pasta_eln.backend_worker.sqlite import MAIN_ORDER
from pasta_eln.backend_worker.worker import Task
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import SPACE, Button, ButtonStyle


class TableHeader(QDialog):
  """Choose the stored list columns for one document type."""

  def __init__(self, comm: Communicate, docType: str) -> None:
    super().__init__()
    self.comm = comm
    self.docType = docType
    self.available = {column.removeprefix('.') for column in MAIN_ORDER} | {'tags', 'qrCodes'}
    self.selected: list[str] = []
    self.propertyGroups: dict[str, list[str]] = {}
    self.viewQuery = f'SELECT view FROM docTypes WHERE docType LIKE "{docType}%"'
    self.propertiesQuery = (
        f'SELECT DISTINCT properties.key FROM properties JOIN main USING(id) '
        f'WHERE main.type LIKE "{docType}%"'
    )

    self.setWindowTitle('Select list columns')
    self.setMinimumWidth(600)
    layout = QVBoxLayout(self)
    layout.setContentsMargins(SPACE.M, SPACE.M, SPACE.M, SPACE.M)
    layout.setSpacing(SPACE.S)
    listsLayout = QHBoxLayout()
    layout.addLayout(listsLayout)

    self.availableList = QListWidget()
    self.availableList.setMinimumHeight(250)
    listsLayout.addWidget(self.availableList)

    controls = QVBoxLayout()
    listsLayout.addLayout(controls)
    self.buttons = []
    for label, command in (('Add →', Command.ADD), ('← Remove', Command.REMOVE),
                           ('Move up', Command.MOVE_UP), ('Move down', Command.MOVE_DOWN)):
      self.buttons.append(Button(label, self, command))
      controls.addWidget(self.buttons[-1])
    controls.addStretch()

    self.selectedList = QListWidget()
    listsLayout.addWidget(self.selectedList)

    propertyLayout = QHBoxLayout()
    layout.addLayout(propertyLayout)
    self.propertyGroup = QComboBox()
    self.propertyGroup.currentTextChanged.connect(self.updatePropertyNames)
    propertyLayout.addWidget(self.propertyGroup)
    self.propertyName = QComboBox()
    self.propertyName.activated.connect(self.addProperty)
    propertyLayout.addWidget(self.propertyName)

    footer = QHBoxLayout()
    footer.addStretch()
    Button('Cancel', self, Command.CANCEL, footer)
    Button('Save', self, Command.SAVE, footer, style=ButtonStyle.HIGHLIGHTED)
    footerWidget = QWidget()
    footerWidget.setLayout(footer)
    layout.addWidget(footerWidget)

    self.comm.backendThread.worker.beSendSQL.connect(self.onGetData)
    self.comm.uiSendSQL.emit([{'type': 'get_df', 'cmd': self.viewQuery}])
    self.comm.uiSendSQL.emit([{'type': 'get_df', 'cmd': self.propertiesQuery}])


  @Slot(str, pd.DataFrame)
  def onGetData(self, query: str, data: pd.DataFrame) -> None:
    """Receive the saved view or the available custom properties."""
    if query == self.viewQuery and not data.empty:
      value = data.iloc[0, 0]
      self.selected = [column.removeprefix('.') for column in value.split(',')] if value else ['name']
      self.available.update(self.selected)
      self.paint()
    elif query == self.propertiesQuery and not data.empty:
      groups: defaultdict[str, set[str]] = defaultdict(set)
      for key in data['key'].to_list():
        if '.' in key:
          group, name = key.split('.', 1)
          groups[group].add(name)
      self.propertyGroups = {group: sorted(names) for group, names in groups.items()}
      self.propertyGroup.addItems(sorted(self.propertyGroups))
      self.updatePropertyNames(self.propertyGroup.currentText())


  def paint(self) -> None:
    """Refresh both column lists."""
    self.availableList.clear()
    self.availableList.addItems(sorted(self.available.difference(self.selected)))
    self.selectedList.clear()
    self.selectedList.addItems(self.selected)


  def execute(self, command:'Command') -> None:
    """Handle a column-selection command."""
    if command is Command.ADD:
      self.selected.extend(item.text() for item in self.availableList.selectedItems())
      self.paint()
    elif command is Command.REMOVE:
      remove = {item.text() for item in self.selectedList.selectedItems()}
      self.selected = [column for column in self.selected if column not in remove or column == 'name']
      self.paint()
    elif command is Command.MOVE_UP:
      row = self.selectedList.currentRow()
      if row > 0:
        self.selected[row - 1], self.selected[row] = self.selected[row], self.selected[row - 1]
        self.paint()
        self.selectedList.setCurrentRow(row - 1)
    elif command is Command.MOVE_DOWN:
      row = self.selectedList.currentRow()
      if 0 <= row < len(self.selected) - 1:
        self.selected[row + 1], self.selected[row] = self.selected[row], self.selected[row + 1]
        self.paint()
        self.selectedList.setCurrentRow(row + 1)
    elif command is Command.CANCEL:
      self.reject()
    elif command is Command.SAVE:
      self.save()


  def updatePropertyNames(self, group: str) -> None:
    """Update the property names for the selected group"

    Args:
      group (str): The selected group name
    """
    self.propertyName.clear()
    self.propertyName.addItems(self.propertyGroups.get(group, []))


  def addProperty(self, index: int) -> None:
    """Add the selected property to the list"

    Args:
      index (int): The index of the property to add
    """
    if name:= self.propertyName.itemText(index):
      column = f'{self.propertyGroup.currentText()}.{name}'
      if column not in self.selected:
        self.selected.append(column)
        self.paint()


  def save(self) -> None:
    """Persist the selected column order and close the dialog."""
    mainColumns = set(MAIN_ORDER) | {'tags', 'qrCodes'}
    columns = [column if column in mainColumns or '.' in column else f'.{column}' for column in self.selected]
    self.comm.uiRequestTask.emit(Task.SEND_TBL_COLUMN, {'docType': self.docType, 'newList': columns})
    self.accept()


  def done(self, result: int) -> None:
    """Cleanup on dialog close

    Args:
      result (int): The result of the dialog
    """
    try:
      self.comm.backendThread.worker.beSendSQL.disconnect(self.onGetData)
    except (RuntimeError, TypeError):
      pass
    super().done(result)


class Command(Enum):
  """Commands available in the column-selection dialog."""
  ADD = auto()
  REMOVE = auto()
  MOVE_UP = auto()
  MOVE_DOWN = auto()
  SAVE = auto()
  CANCEL = auto()
