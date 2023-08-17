#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_tableview_datamodel.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union, Any

import PySide6.QtCore
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QPersistentModelIndex, QObject


class OntologyTableViewModel(QAbstractTableModel):
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
    self.db = None
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
    self.columns_count = 8

  def headerData(self, section: int, orientation: PySide6.QtCore.Qt.Orientation, role: int = ...) -> Any:
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self.header_values[section]
    return super().headerData(section, orientation, role)

  def update(self, ontology_structure_prop):
    """

    Args:
        ontology_structure_prop:

    Returns:

    """
    print('Updating Model')
    self.db = ontology_structure_prop
    print('Database : {0}'.format(self.db))

  def rowCount(self, parent=QModelIndex()):
    return len(self.db)

  def columnCount(self, parent=QModelIndex()):
    return self.columns_count

  def setData(self, index: Union[PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex], value: Any,
              role: int = ...) -> bool:
    if role == Qt.EditRole:
      prop_row_index = index.row()
      prop = self.data_name_map.get(index.column())
      self.db[prop_row_index][prop] = value
      self.dataChanged.emit(index, index, [Qt.EditRole])
      return True
    return False

  def data(self, index: Union[QModelIndex, QPersistentModelIndex],
           role: int = ...) -> Any:
    if  index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
      row = index.row()
      column = index.column()
      value = self.db[row].get(self.data_name_map.get(column))
      return str(value if value else '')
    else:
      return None

  def flags(self, index):
    return (Qt.ItemIsEditable
            | Qt.ItemIsSelectable
            | Qt.ItemIsEnabled)
