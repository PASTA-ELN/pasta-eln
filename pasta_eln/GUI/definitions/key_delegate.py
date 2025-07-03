""" NameColumnDelegate module used for the table views """
from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget


class KeyDelegate(QStyledItemDelegate):
  """
  Delegate for creating the line edit with lookup icon for the iri column in data hierarchy editor tables
  """
  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index:  QModelIndex | QPersistentModelIndex) -> QWidget:
    """
    Creates the line edit

    Args:
      parent (QWidget): Parent table view
      option (QStyleOptionViewItem): Style option for the cell represented by index
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index

    Returns: QLineEdit widget
    """
    return QWidget(parent)
