#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_props_tableview_data_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union, Any

import PySide6.QtCore
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QPersistentModelIndex, Slot


class OntologyPropsTableViewModel(QAbstractTableModel):
  """
  Data-model for the ontology table view
  """

  def __init__(self, parent=None, *args):
    """
    Initialize the data model representing the Ontology document in CouchDB
    Args:
      parent:
      *args:
    """
    super().__init__(parent)
    self.props_data_set = None
    self.data_name_map = {
      0: "name",
      1: "query",
      2: "list",
      3: "link",
      4: "required",
      5: "unit",
      6: "delete",
      7: "re-order"
    }
    self.header_values = list(self.data_name_map.values())
    self.columns_count = len(self.header_values)

  def headerData(self, section: int, orientation: PySide6.QtCore.Qt.Orientation, role: int = ...) -> Any:
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self.header_values[section]
    return super().headerData(section, orientation, role)

  def update(self, ontology_props):
    """

    Args:
        ontology_props:

    Returns:

    """
    print('Updating Model')
    self.props_data_set = ontology_props
    self.layoutChanged.emit()
    print('Database : {0}'.format(self.props_data_set))

  def rowCount(self, parent=QModelIndex()):
    return len(self.props_data_set)

  def columnCount(self, parent=QModelIndex()):
    return self.columns_count

  def setData(self, index: Union[PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex], value: Any,
              role: int = ...) -> bool:
    if role == Qt.EditRole or role == PySide6.QtCore.Qt.UserRole:
      prop_row_index = index.row()
      prop = self.data_name_map.get(index.column())
      self.props_data_set[prop_row_index][prop] = value
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
      value = self.props_data_set[row].get(self.data_name_map.get(column))
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
    data_deleted = self.props_data_set[row]
    self.props_data_set.pop(row)
    print(f"Deleted (row: {row}, data: {data_deleted})")
    self.layoutChanged.emit()

  @Slot(int)
  def re_order_data(self, row):
    """

    Args:


    Returns:

    """
    data_to_be_pushed = self.props_data_set.pop(row)
    shift_position = row - 1
    shift_position = shift_position if shift_position > 0 else 0
    self.props_data_set.insert(shift_position, data_to_be_pushed)
    print(f"Reorder (row: {row}, newPos: {shift_position}, data: {data_to_be_pushed})")
    self.layoutChanged.emit()

  def add_data_row(self):
    self.props_data_set.insert(len(self.props_data_set), {})
    self.layoutChanged.emit()
