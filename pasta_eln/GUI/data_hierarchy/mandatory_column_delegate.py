""" MandatoryColumnDelegate  module used for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: mandatory_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Union
from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QRect
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QRadioButton, QStyle, QStyledItemDelegate, QStyleOptionButton,
                               QStyleOptionViewItem, QWidget)


class MandatoryColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the radio buttons for the mandatory column in data hierarchy editor tables
  """
  def paint(self,
            painter: QPainter,
            option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Draws the mandatory radio button within the cell represented by index
    Args:
      painter (QPainter): Painter instance for painting the button.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns: None

    """
    indexName = index.model().index(index.row(), 0)
    if not indexName.data():
      return
    widget = option.widget                                                        # type: ignore[attr-defined]
    style = widget.style() if widget else QApplication.style()
    opt = QStyleOptionButton()
    radio_button = QRadioButton()
    option_rect = option.rect                                                     # type: ignore[attr-defined]
    opt.rect = QRect(option_rect.left() + option_rect.width() / 2 - 10,           # type: ignore[attr-defined]
                     option_rect.top(),
                     option_rect.width(),
                     option_rect.height())
    indexName = index.model().index(index.row(), 0)
    isMandatory = index.data()=='T' and indexName.data()
    opt.state = QStyle.StateFlag.State_On if isMandatory else QStyle.StateFlag.State_Off# type: ignore[attr-defined]
    style.drawControl(QStyle.ControlElement.CE_RadioButton, opt, painter, radio_button)


  def editorEvent(self,
                  event: QEvent,
                  model: QAbstractItemModel,
                  option: QStyleOptionViewItem,
                  index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    """
    In case of mouse click event, the model data is toggled for the respective table cell index
    Args:
      event (QEvent): The editor event information.
      model (QAbstractItemModel): Model data representing the table view.
      option (QStyleOptionViewItem): QStyleOption for the table cell.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns (bool): True/False
    """
    if event.type() == QEvent.Type.MouseButtonRelease:
      indexName = model.index(index.row(), 0)
      if indexName.data():
        isMandatory = index.data()=='T'
        model.setData(index, '' if isMandatory else 'T')                        # invert mandatory after click
    return super().editorEvent(event, model, option, index)


  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    """
    Disable the editor for the whole mandatory column by simply returning None
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: None
    """
    return None                                                                   # type: ignore[return-value]
