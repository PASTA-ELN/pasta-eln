"""A Qt table model that exposes a pandas DataFrame to a QTableView."""
from typing import Any
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt, Signal
from typing_extensions import override


class PandasTableModel(QAbstractTableModel):
  """
  A Qt table model that exposes a pandas DataFrame to a QTableView.

  This model provides a read-only interface to a pandas DataFrame,
  mapping rows/columns directly to the underlying DataFrame structure
  without copying data.

  Attributes:
      _df (pd.DataFrame): The underlying pandas DataFrame.
  """
  rowCheckChanged = Signal(int, bool)

  def __init__(self, df: pd.DataFrame, documentIds: list[str] | None = None) -> None:
    """ Initializes a new PandasTableModel
    Args:
      df (pd.DataFrame): The dataframe to display.
      documentIds (list[str] | None): A list of document IDs
    """
    super().__init__()
    self.df          = df
    self.checkedRows = [False] * len(self.df)
    self.documentIds = documentIds or ['']*len(self.df)


  def rowCount(self, _: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
    """ Returns the number of rows in the table.
    Returns:
      int: The number of rows in the table.
    """
    return self.df.shape[0]


  def columnCount(self, _: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
    """ Returns the number of columns in the table.
    Returns:
      int: The number of columns in the table.
    """
    return self.df.shape[1] + 1                                                       # +1 for checkbox-column


  def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
    """ Returns the data for the given index and role.
    Args:
      index (QModelIndex | QPersistentModelIndex): The index.
      role (int, optional): The role.
        Defaults to Qt.ItemDataRole.DisplayRole.
    Returns:
      Any: The data.
    """
    if not index.isValid():
      return None
    # Handle a Checkbox-Column as column 0
    if index.column() == 0:
      if role == Qt.ItemDataRole.CheckStateRole:
        return Qt.CheckState.Checked if self.checkedRows[index.row()] else Qt.CheckState.Unchecked
      return '' if role == Qt.ItemDataRole.DisplayRole else None
    # Other columns
    if role == Qt.ItemDataRole.DisplayRole:
      return str(self.df.iat[index.row(), index.column() - 1])
    return None


  def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
    """ Returns the flags for the given index.
    Args:
      index (QModelIndex | QPersistentModelIndex): The index.
    Returns:
      Qt.ItemFlag: The flags.
    """
    if not index.isValid():
      return Qt.ItemFlag.NoItemFlags
    baseFlags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    # Checkbox column is checkable
    if index.column() == 0:
      return baseFlags | Qt.ItemFlag.ItemIsUserCheckable
    return baseFlags


  def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any,
              role: int = Qt.ItemDataRole.EditRole) -> bool:
    """ Set the data for the given index and role.
    Args:
      index (QModelIndex | QPersistentModelIndex): The index.
      value (Any): The value.
      role (int, optional): The role.
        Defaults to Qt.ItemDataRole.EditRole.
    Returns:
      bool: True if the data was set successfully, False otherwise.
    """
    # When a row is checked, this method is called and updates the object.
    if index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
      checked = value == Qt.CheckState.Checked.value
      self.checkedRows[index.row()] = checked
      self.rowCheckChanged.emit(index.row(), checked)
      self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
      return True
    return False


  def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
    """ Returns the header data for the given section and orientation.
    Args:
      section (int): The section.
      orientation (Qt.Orientation): The orientation.
      role (int, optional): The role.
        Defaults to Qt.ItemDataRole.DisplayRole.
    Returns:
      Any: The header data.
    """
    if role != Qt.ItemDataRole.DisplayRole:
      return None
    if orientation == Qt.Orientation.Horizontal:
      return '' if section == 0 else str(self.df.columns[section - 1])
    return str(self.df.index[section])


  def checkRow(self, row: int, checked: bool) -> None:
    """
    Setter for self.checkedRows
    Args:
      row (int): The row index.
      checked (bool): Whether the row should be checked.
    """
    self.checkedRows[row] = checked
    index = self.index(row, 0)
    self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])


  @override
  def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
    """ Sorts the table by the given column and order.
    Args:
      column (int): The column to sort by.
      order (Qt.SortOrder): The order to sort by. Defaults to Qt.SortOrder.AscendingOrder.
    """
    if column == 0:
      # ignore the first column (checkboxes) maybe implement later
      return
    self.layoutAboutToBeChanged.emit()
    ascending = order == Qt.SortOrder.AscendingOrder
    dfColumn = self.df.columns[column - 1]
    sortedDF = self.df.sort_values(by=dfColumn, ascending=ascending)
    self.checkedRows = [self.checkedRows[i] for i in sortedDF.index]
    self.documentIds = [self.documentIds[i] for i in sortedDF.index]
    self.df = sortedDF.reset_index(drop=True)
    self.layoutChanged.emit()
