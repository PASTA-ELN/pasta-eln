"""A Qt table model that exposes a pandas DataFrame to a QTableView."""
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt


class PandasTableModel(QAbstractTableModel):
  """
  A Qt table model that exposes a pandas DataFrame to a QTableView.

  This model provides a read-only interface to a pandas DataFrame,
  mapping rows/columns directly to the underlying DataFrame structure
  without copying data.

  Attributes:
      _df (pd.DataFrame): The underlying pandas DataFrame.
  """

  def __init__(self, df: pd.DataFrame):
    super().__init__()
    self._df = df

  def rowCount(self, parent=None):
    return self._df.shape[0]

  def columnCount(self, parent=None):
    return self._df.shape[1]

  def data(self, index, role=Qt.ItemDataRole.DisplayRole):
    if not index.isValid():
      return None

    if role == Qt.ItemDataRole.DisplayRole:
      return str(self._df.iat[index.row(), index.column()])

    return None

  def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
    if role != Qt.ItemDataRole.DisplayRole:
      return None

    if orientation == Qt.Orientation.Horizontal:
      return str(self._df.columns[section])

    return str(self._df.index[section])
