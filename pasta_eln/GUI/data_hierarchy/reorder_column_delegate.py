""" ReorderColumnDelegate for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: reorder_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union
import qtawesome as qta
from pandas import DataFrame
from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QSize, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QPushButton, QStyle, QStyledItemDelegate, QStyleOptionButton,
                               QStyleOptionViewItem, QWidget)
from .utility_functions import is_click_within_bounds


class ReorderColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the icons for the re-order column in the data hierarchy editor tables
  """
  re_order_signal = Signal(int)

  def __init__(self, df:DataFrame, group:str) -> None:
    """
      Constructor

    Args:
      df (DataFrame): pandas dataframe containing the entire schema
      group (str): string of this group/class
    """
    super().__init__()
    self.df = df
    self.group = group


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
    if index.row()>=len(self.df[self.df['class']==self.group]):
      return
    button = QPushButton()
    opt = QStyleOptionButton()
    opt.state = QStyle.StateFlag.State_Active | QStyle.StateFlag.State_Enabled  # type: ignore[attr-defined]
    opt.rect = option.rect                                                      # type: ignore[attr-defined]
    opt.icon = qta.icon('fa5s.arrow-up', scale_factor=1.0)                      # type: ignore[attr-defined]
    opt.iconSize = QSize(15, 15)                                                # type: ignore[attr-defined]
    QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, opt, painter, button)
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
      self.re_order_signal.emit(index.row())
      return True
    return False
