""" OntologyTableViewModel Generic module used for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_attachments_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
# import logging
import logging
from typing import Union, Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QPersistentModelIndex, Slot
from PySide6.QtWidgets import QWidget


class OntologyTableViewModel(QAbstractTableModel):
  """
  Abstracted data-model base for the ontology table views
  """

  def __init__(self,
               parent: Union[QWidget | None] = None):
    """
    Initialize the data model representing attachments from ontology document in the database
    Args:
      parent (QWidget): Parent view or widget
    """
    super().__init__(parent)
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
    self.data_set: list[dict[Any, Any]] | Any = []
    self.data_name_map: dict[int, str] = {}
    self.header_values: list[str] = []
    self.columns_count = 0

  def hasChildren(self, parent: Union[QModelIndex, QPersistentModelIndex] = ...) -> bool:  # type: ignore[assignment]
    """
    Returns whether the model has children
    Args:
      parent (Union[QModelIndex, QPersistentModelIndex]): Parent index

    Returns: False since it's a tree view model

    """
    return False  # Since it's a table model, the children are not supported

  def headerData(self,
                 section: int,
                 orientation: Qt.Orientation,
                 role: int = Qt.ItemDataRole) -> Any:  # type: ignore[assignment]
    """
    Returns the header data from self.header_values
    Args:
      section (int): Index section of the table header
      orientation (Qt.Orientation): Orientation of the table header
      role (int): Display role for the table

    Returns (Any): The header name for the column represented by the section index

    """
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self.header_values[section].capitalize()
    return super().headerData(section, orientation, role)

  def update(self,
             updated_table_data: list[dict[Any, Any]] | Any) -> None:
    """
    Updating the table data model
    Args:
      updated_table_data (dict): Newly set data model

    Returns: None

    """
    self.logger.info("Table Data updated..")
    self.data_set = updated_table_data
    self.layoutChanged.emit()

  def rowCount(self,
               parent: Union[QModelIndex, QPersistentModelIndex] = ...) -> int:  # type: ignore[assignment]
    """
    Returns the row count for the table under the given parent
    Args:
      parent (Union[QModelIndex, QPersistentModelIndex]): Parent index

    Returns (int): Row count

    """
    return len(self.data_set) \
      if self.data_set \
      else 0

  def columnCount(self,
                  parent: Union[QModelIndex, QPersistentModelIndex] = ...) -> int:  # type: ignore[assignment]
    """
    Returns the column count for the table under the given parent
    Args:
      parent (Union[QModelIndex, QPersistentModelIndex]): Parent index

    Returns (int): Column count

    """
    return self.columns_count

  def setData(self,
              index: Union[QModelIndex, QPersistentModelIndex],
              value: Any,
              role: int = Qt.ItemDataRole) -> bool:  # type: ignore[assignment]
    """
    Sets the data for the table cell represented by the index. The data is set only for the below cases
     - EditRole: When the data in the cell is edited via line edit
     - UserRole: When the cell contains radio button and is set via required_column_delegate
    Args:
      index (Union[QModelIndex, QPersistentModelIndex]): Index with row & column representing the table cell
      value (Any): The updated value from the table view
      role (int): Role for which the data is set

    Returns (bool): True when data is set, otherwise false

    """
    if index.isValid() and role in (Qt.EditRole, Qt.UserRole):
      row_index = index.row()
      column = self.data_name_map.get(index.column())
      self.data_set[row_index][column] = value
      self.dataChanged.emit(index, index, role)
      return True
    return False

  def data(self,
           index: Union[QModelIndex, QPersistentModelIndex],
           role: int = Qt.ItemDataRole) -> Any:  # type: ignore[assignment]
    """
    Gets the data from the table cell represented by the index. Data is only retrieved for the following roles:
    - DisplayRole: When the table needs to be displayed
    - EditRole: When the data in the cell is edited via line edit
    - UserRole: When the cell contains radio button and is set via required_column_delegate
    Args:
      index (Union[QModelIndex, QPersistentModelIndex]): Index of the respective table cell to retrieve data
      role (int): Role for the data operation.

    Returns (Any): String data representation if available, otherwise null-string/None

    """
    if (index.isValid() and
        role in (Qt.DisplayRole, Qt.EditRole, Qt.UserRole)):
      row = index.row()
      column = index.column()
      return self.data_set[row].get(self.data_name_map.get(column))
    else:
      return None

  def flags(self,
            index: Union[QModelIndex, QPersistentModelIndex]) -> Qt.ItemFlags:
    """
    Flags required for the table cell
    Args:
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index

    Returns (Qt.ItemFlags): The combinations of flags for the cell represented by the index

    """
    if index.isValid():
      return (Qt.ItemIsEditable  # type: ignore[operator]
              | Qt.ItemIsSelectable
              | Qt.ItemIsEnabled)
    return None  # type: ignore[return-value]

  @Slot(int)
  def delete_data(self, position: int) -> None:
    """
    Slot invoked to delete the data from data set at the specific position
    Args:
      position (int): Position of the data to be deleted from the data set

    Returns: None

    """
    try:
      data_deleted = self.data_set.pop(position)
    except IndexError:
      self.logger.warning("Invalid position: {%s}", position)
      return None
    self.logger.info("Deleted (row: {%s}, data: {%s})...", position, data_deleted)
    self.layoutChanged.emit()
    return None

  @Slot(int)
  def re_order_data(self,
                    position: int) -> None:
    """
    Slot invoked to re-order the data position in the data set. Data at the position: row will be moved above in the set
    Args:
      position (int): Position of the data to be shifted up.

    Returns: None

    """
    try:
      data_to_be_pushed = self.data_set.pop(position)
    except IndexError:
      self.logger.warning("Invalid position: {%s}", position)
      return None
    shift_position = position - 1
    shift_position = max(shift_position, 0)
    self.data_set.insert(shift_position, data_to_be_pushed)
    self.logger.info("Reordered the data, Actual position: {%s}, "
                     "New Position: {%s}, "
                     "data: {%s})", position,
                     shift_position,
                     data_to_be_pushed)
    self.layoutChanged.emit()
    return None

  def add_data_row(self) -> None:
    """
    Add an empty row to the table data set
    Returns: None

    """
    if self.data_set is not None:
      self.logger.info("Added new row...")
      self.data_set.insert(len(self.data_set), {})
      self.layoutChanged.emit()
    return None
