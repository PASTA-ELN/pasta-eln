#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_attachments_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Union, Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QPersistentModelIndex, Slot
from PySide6.QtWidgets import QWidget


class OntologyTableViewModel(QAbstractTableModel):
  """
  Abstracted data-model base for the ontology table views
  """

  def __init__(self,
               parent: QWidget = None):
    """
    Initialize the data model representing attachments from ontology document in the database
    Args:
      parent (QWidget): Parent view or widget
    """
    super().__init__(parent)
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)
    self.data_set = None
    self.data_name_map = {}
    self.header_values = None
    self.columns_count = None

  def headerData(self,
                 section: int,
                 orientation: Qt.Orientation,
                 role: int = ...) -> Any:
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
             updated_table_data: dict):
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
               parent: Union[QModelIndex, QPersistentModelIndex] = ...) -> int:
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
                  parent: Union[QModelIndex, QPersistentModelIndex] = ...) -> int:
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
              role: int = ...) -> bool:
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
    if role == Qt.EditRole or role == Qt.UserRole:
      prop_row_index = index.row()
      prop = self.data_name_map.get(index.column())
      self.data_set[prop_row_index][prop] = value
      self.dataChanged.emit(index, index, role)
      return True
    return False

  def data(self,
           index: Union[QModelIndex, QPersistentModelIndex],
           role: int = ...) -> Any:
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
    if (index.isValid()
        and (role == Qt.DisplayRole
             or role == Qt.EditRole
             or role == Qt.UserRole)):
      row = index.row()
      column = index.column()
      value = self.data_set[row].get(self.data_name_map.get(column))
      return str(value if value else '')
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
    return (Qt.ItemIsEditable
            | Qt.ItemIsSelectable
            | Qt.ItemIsEnabled)

  @Slot(int)
  def delete_data(self, position: int):
    """
    Slot invoked to delete the data from data set at the specific position
    Args:
      position (int): Position of the data to be deleted from the data set

    Returns: None

    """
    data_deleted = self.data_set[position]
    self.data_set.pop(position)
    self.logger.info(f"Deleted (row: {position}, data: {data_deleted})...")
    self.layoutChanged.emit()

  @Slot(int)
  def re_order_data(self,
                    position: int):
    """
    Slot invoked to re-order the data position in the data set. Data at the position: row will be moved above in the set
    Args:
      position (int): Position of the data to be shifted up.

    Returns: None

    """
    data_to_be_pushed = self.data_set.pop(position)
    shift_position = position - 1
    shift_position = shift_position if shift_position > 0 else 0
    self.data_set.insert(shift_position, data_to_be_pushed)
    self.logger.info(f"Reordered the data, Actual position: {position}, "
                     f"New Position: {shift_position}, "
                     f"data: {data_to_be_pushed})")
    self.layoutChanged.emit()

  def add_data_row(self):
    """
    Add an empty row to the table data set
    Returns: None

    """
    self.logger.info(f"Added new row...")
    self.data_set.insert(len(self.data_set), {})
    self.layoutChanged.emit()
