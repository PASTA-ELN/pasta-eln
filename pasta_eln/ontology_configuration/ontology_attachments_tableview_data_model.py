#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_attachments_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union, Any

import PySide6.QtCore
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QPersistentModelIndex, Slot


class OntologyAttachmentsTableViewModel(QAbstractTableModel):
  """
  Data-model for the ontology attachments table view
  """

  def __init__(self, parent=None):
    """
    Initialize the data model representing attachments from ontology document in the database
    Args:
      parent:
    """
    super().__init__(parent)
    self.attachments_data_set = None
    self.data_name_map = {
      0: "name",
      1: "link",
      2: "delete",
      3: "re-order"
    }
    self.header_values = list(self.data_name_map.values())
    self.columns_count = len(self.header_values)

  def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self.header_values[section]
    return super().headerData(section, orientation, role)

  def update(self, ontology_type_attachments: str):
    """

    Args:
        ontology_type_attachments (str):

    Returns:

    """
    print('Updating Model')
    self.attachments_data_set = ontology_type_attachments
    self.layoutChanged.emit()
    print('Database : {0}'.format(self.attachments_data_set))

  def rowCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = ...) -> int:
    return len(self.attachments_data_set)

  def columnCount(self, parent: Union[QModelIndex, QPersistentModelIndex] = ...) -> int:
    return self.columns_count
  def setData(self, index: Union[QModelIndex, QPersistentModelIndex], value: Any,
              role: int = ...) -> bool:
    if role == Qt.EditRole or role == PySide6.QtCore.Qt.UserRole:
      prop_row_index = index.row()
      prop = self.data_name_map.get(index.column())
      self.attachments_data_set[prop_row_index][prop] = value
      self.dataChanged.emit(index, index, role)
      return True
    return False

  def data(self, index: Union[QModelIndex, QPersistentModelIndex],
           role: int = ...) -> Any:
    if (index.isValid()
        and (role == Qt.DisplayRole
             or role == Qt.EditRole
             or role == PySide6.QtCore.Qt.UserRole)):
      row = index.row()
      column = index.column()
      value = self.attachments_data_set[row].get(self.data_name_map.get(column))
      return str(value if value else '')
    else:
      return None

  def flags(self, index):
    return (Qt.ItemIsEditable
            | Qt.ItemIsSelectable
            | Qt.ItemIsEnabled)

  @Slot(int, int)
  def delete_data(self, row, column):
    """

    Args:


    Returns:

    """
    data_deleted = self.attachments_data_set[row]
    self.attachments_data_set.pop(row)
    print(f"Deleted (row: {row}, data: {data_deleted})")
    self.layoutChanged.emit()

  @Slot(int)
  def re_order_data(self, row):
    """

    Args:


    Returns:

    """
    data_to_be_pushed = self.attachments_data_set.pop(row)
    shift_position = row - 1
    shift_position = shift_position if shift_position > 0 else 0
    self.attachments_data_set.insert(shift_position, data_to_be_pushed)
    print(f"Reorder (row: {row}, newPos: {shift_position}, data: {data_to_be_pushed})")
    self.layoutChanged.emit()

  def add_data_row(self):
    self.attachments_data_set.insert(len(self.attachments_data_set), {})
    self.layoutChanged.emit()
