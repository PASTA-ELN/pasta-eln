""" NameColumnDelegate module used for the table views """
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Signal
from PySide6.QtWidgets import QLineEdit, QStyledItemDelegate, QStyleOptionViewItem, QWidget


class NameColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the line edit with lookup icon for the iri column in data hierarchy editor tables
  """
  add_row_signal = Signal()

  def __init__(self) -> None:
    super().__init__()
    self.numRows = -1


  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index:  QModelIndex | QPersistentModelIndex) -> QWidget:
    """
    Creates the line edit with lookup icon for the iri column cell represented by index
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: QLineEdit widget
    """
    lineEdit = QLineEdit(parent)
    return lineEdit


  def destroyEditor(self, editor, index):
    if index.row()==self.numRows:
        self.add_row_signal.emit()
    return super().destroyEditor(editor, index)