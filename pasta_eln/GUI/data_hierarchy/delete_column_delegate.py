""" DeleteColumnDelegate for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: delete_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union
import qtawesome as qta
from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QSize, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QPushButton, QStyle, QStyledItemDelegate, QStyleOption, QStyleOptionButton,
                               QStyleOptionViewItem, QWidget)
from .utility_functions import is_click_within_bounds


class DeleteColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the delete icon for the delete column in the data hierarchy table views
  """
  def __init__(self) -> None:
    """ Constructor """
    super().__init__()


  def paint(self,
            painter: QPainter,
            option: QStyleOption,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Draws the delete button within the cell represented by index
    Args:
      painter (QPainter): Painter instance for painting the button.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.
    """
    indexName = index.model().index(index.row(), 0)
    if not indexName.data() or indexName.data() in ['name','tags','comment']:
      return
    button = QPushButton()
    opt = QStyleOptionButton()
    opt.state = QStyle.StateFlag.State_Active | QStyle.StateFlag.State_Enabled  # type: ignore[attr-defined]
    opt.rect = option.rect                                                      # type: ignore[attr-defined]
    opt.icon = qta.icon('fa5s.trash', scale_factor=1.0)                         # type: ignore[attr-defined]
    opt.iconSize = QSize(15, 15)                                                # type: ignore[attr-defined]
    QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, opt, painter, button)
    return


  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    """
    Disable the editor for the delete column by simply returning None
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.
    """
    return None  # type: ignore[return-value]


  def editorEvent(self,
                  event: QEvent,
                  model: QAbstractItemModel,
                  option: QStyleOptionViewItem,
                  index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    """
    In case of click detected within the cell represented by index, the respective delete signal is emitted
    Args:
      event (QEvent): The editor event information.
      model (QAbstractItemModel): Model data representing the table view.
      option (QStyleOptionViewItem): QStyleOption for the table cell.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns (bool): True if deleted otherwise False
    """
    indexName = index.model().index(index.row(), 0)
    if indexName.data() and indexName.data() not in ['name','tags','comment'] and \
        is_click_within_bounds(event, option) and isinstance(index, QModelIndex):
      index.model().removeRow(index.row())
      return True
    return False
