""" NameColumnDelegate module used for the table views """
from typing import Any
from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit, QStyledItemDelegate, QStyleOptionViewItem, QWidget


class NameColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the line edit with lookup icon for the iri column in data hierarchy editor tables
  """
  def __init__(self, parent:Any = ...):
    super().__init__(parent)
    self.res = QLineEdit(parent)
    self.res.setValidator(QRegularExpressionValidator(r'[a-z][a-z0-9]+'))

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
    if index.data() in ['name','tags','comment']:
      return QWidget(parent)
    return self.res


  def destroyEditor(self, editor:QWidget, index:QModelIndex | QPersistentModelIndex) -> None:
    """ destroy the line editor

    Args:
      editor (QWidget): Parent table view
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index
    """
    if index.row()+1==index.model().rowCount():
      index.model().insertRow(index.model().rowCount())
      index.model().layoutChanged.emit()
    super().destroyEditor(editor, index)
    return
