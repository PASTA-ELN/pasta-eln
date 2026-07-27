"""A Qt table model that exposes a pandas DataFrame to a QTableView."""
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt, Signal
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

  def __init__(self, df: pd.DataFrame):
    super().__init__()
    self._df = df
    self._checkedRows = [False] * len(self._df)

  def rowCount(self, parent=None):
    return self._df.shape[0]

  def columnCount(self, parent=None):
    return self._df.shape[1] + 1  # +1 for checkbox-column

  def data(self, index, role=Qt.ItemDataRole.DisplayRole):
    if not index.isValid():
      return None

    # Handle a Checkbox-Column as column 0
    if index.column() == 0:
      if role == Qt.ItemDataRole.CheckStateRole:
        return Qt.CheckState.Checked if self._checkedRows[index.row()] else Qt.CheckState.Unchecked
      if role == Qt.ItemDataRole.DisplayRole:
        return ""
      return None

    if role == Qt.ItemDataRole.DisplayRole:
      return str(self._df.iat[index.row(), index.column() - 1])

    return None

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemFlag.NoItemFlags

    baseFlags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    # Checkbox column is checkable
    if index.column() == 0:
      return baseFlags | Qt.ItemFlag.ItemIsUserCheckable
    return baseFlags

  def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
    # When a row is checked, this method is called and updates the object.
    if index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
      checked = value == Qt.CheckState.Checked.value
      self._checkedRows[index.row()] = checked
      self.rowCheckChanged.emit(index.row(), checked)
      self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
      return True
    return False

  def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
    if role != Qt.ItemDataRole.DisplayRole:
      return None

    if orientation == Qt.Orientation.Horizontal:
      if section == 0:
        return ""
      return str(self._df.columns[section - 1])

    return str(self._df.index[section])

  def checkedRows(self):
    """
    Returns: self._checkedRows
    """
    return self._checkedRows

  def checkRow(self, row, checked):
    """
    Setter for self._checkedRows
    """
    self._checkedRows[row] = checked
    index = self.index(row, 0)
    self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

  @override
  def sort(self, column: int, order: Qt.SortOrder) -> None:
    if column == 0:
      # ignore the first column (checkboxes) maybe implement later
      return

    self.layoutAboutToBeChanged.emit()

    ascending = (
      order == Qt.SortOrder.AscendingOrder
    )
    dfColumn = self._df.columns[column - 1]
    sortedDF = self._df.sort_values(by=dfColumn, ascending=ascending)
    self._checkedRows = [self._checkedRows[i] for i in sortedDF.index]
    self.layoutChanged.emit()
