""" ReorderColumnDelegate for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: reorder_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import webbrowser
from typing import Union
import qtawesome as qta
from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QPushButton, QStyle, QStyledItemDelegate, QStyleOptionButton,
                               QStyleOptionViewItem, QWidget)
from ..data_hierarchy.utility_functions import is_click_within_bounds


class LinkOnlineDelegate(QStyledItemDelegate):
  """
  Delegate for creating the icons for the re-order column in the data hierarchy editor tables
  """
  def __init__(self, parent = ...):
    super().__init__(parent)
    self.button = QPushButton()

  def paint(self,
            painter: QPainter,
            option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Draws the re-order button within the cell represented by index
    Args:
      painter (QPainter): Painter instance for painting the button.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index
    """
    link = index.model().index(index.row(), 2).data()
    if not link or 'http' not in link or '://' not in link:
      return
    opt = QStyleOptionButton()
    opt.state = QStyle.StateFlag.State_Active | QStyle.StateFlag.State_Enabled    # type: ignore[attr-defined]
    opt.rect = option.rect                                                        # type: ignore[attr-defined]
    opt.icon = qta.icon('mdi.earth-arrow-right', scale_factor=1.0)                # type: ignore[attr-defined]
    opt.iconSize = QSize(15, 15)                                                  # type: ignore[attr-defined]
    QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, opt, painter, self.button)
    return


  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    """
    Disable the editor for the whole re-order column by simply returning None
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.
    """
    return None                                                                   # type: ignore[return-value]


  def editorEvent(self,
                  event: QEvent,
                  model: QAbstractItemModel,
                  option: QStyleOptionViewItem,
                  index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    """
    In case of mouse click event, the re_order_signal is emitted for the respective table cell position
    Args:
      event (QEvent): The editor event information.
      model (QAbstractItemModel): Model data representing the table view.
      option (QStyleOptionViewItem): QStyleOption for the table cell.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns (bool): True/False
    """
    indexName = index.model().index(index.row(), 2)
    if is_click_within_bounds(event, option):
      webbrowser.open(indexName.data().split(', ')[0])
      return True
    return False
