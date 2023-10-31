""" MandatoryColumnDelegate  module used for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: mandatory_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
from typing import Union

from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QRect, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QRadioButton, QStyle, QStyleOptionButton, QStyleOptionViewItem, \
  QStyledItemDelegate, QWidget


class MandatoryColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the radio buttons for the mandatory column in ontology editor tables
  """

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
    Draws the mandatory radio button within the cell represented by index
    Args:
      painter (QPainter): Painter instance for painting the button.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns: None

    """
    widget = option.widget
    style = widget.style() if widget else QApplication.style()
    opt = QStyleOptionButton()
    radio_button = QRadioButton()
    opt.rect = QRect(option.rect.left() + option.rect.width() / 2 - 10,
                     option.rect.top(),
                     option.rect.width(),
                     option.rect.height())
    is_mandatory = bool(index.data(Qt.UserRole))  # type: ignore[arg-type]
    opt.state = QStyle.State_On \
      if is_mandatory \
      else QStyle.State_Off
    style.drawControl(QStyle.CE_RadioButton, opt, painter, radio_button)

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
    if event.type() == QEvent.MouseButtonRelease:
      model.setData(index, not bool(index.data(Qt.UserRole)), Qt.UserRole)  # type: ignore[arg-type]
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
    return None  # type: ignore[return-value]
