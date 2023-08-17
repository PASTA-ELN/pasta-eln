#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_tableview_datamodel.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QStandardItemModel


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
    self.data_name_map = { 0:"name", 1:"query", 2:"list"}

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
    return 6

  def data(self, index, role=Qt.DisplayRole):
    if role == Qt.DisplayRole:
      i = index.row()
      j = index.column()
      return str(self.db[i].get(self.data_name_map.get(j)))
    else:
      return None

  def flags(self, index):
    return (Qt.ItemIsEnabled
            | Qt.ItemIsEditable
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsDropEnabled
            | Qt.ItemIsSelectable
            | Qt.ItemIsAutoTristate
            | Qt.ItemIsUserCheckable
            | Qt.ItemIsUserTristate)
