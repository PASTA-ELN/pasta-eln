""" ReorderColumnDelegate for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: reorder_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Union

from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QSize, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QPushButton, QStyle, QStyleOptionButton, QStyleOptionViewItem, \
  QStyledItemDelegate, QWidget

from .utility_functions import is_click_within_bounds


class ReorderColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the icons for the re-order column in the data hierarchy editor tables
  """
  re_order_signal = Signal(int)

  def __init__(self) -> None:
    """
      Constructor
    """
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

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

    Returns: None

    """
    button = QPushButton()
    opt = QStyleOptionButton()
    opt.state = QStyle.StateFlag.State_Active | QStyle.StateFlag.State_Enabled  # type: ignore[attr-defined]
    opt.rect = option.rect  # type: ignore[attr-defined]
    opt.icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp)  # type: ignore[attr-defined]
    opt.iconSize = QSize(15, 15)  # type: ignore[attr-defined]
    QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, opt, painter, button)

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

    Returns: None

    """
    return None  # type: ignore[return-value]

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
    if is_click_within_bounds(event, option):
      row = index.row()
      self.logger.info("Re-order signal emitted for the position: {%s} in the table..", row)
      self.re_order_signal.emit(row)
      return True
    return False
