""" RequiredColumnDelegate  module used for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: required_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QEvent, QAbstractItemModel, QRect, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QStyleOptionButton, \
  QStyle, QApplication


class RequiredColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the radio buttons for the required column in ontology editor tables
  """

  def __init__(self) -> None:
    """
      Constructor
    """
    super().__init__()
    self.logger = logging.getLogger(__name__ + "." + self.__class__.__name__)

  def paint(self,
            painter: QPainter,
            option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Draws the required radio button within the cell represented by index
    Args:
      painter (QPainter): Painter instance for painting the button.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns: None

    """
    widget = option.widget
    style = widget.style() if widget else QApplication.style()
    opt = QStyleOptionButton()
    opt.rect = QRect(option.rect.left() + option.rect.width() / 2 - 5,
                     option.rect.top(),
                     option.rect.width(),
                     option.rect.height())
    opt.state = QStyle.State_On \
      if index.data(Qt.UserRole) == 'True' \
      else QStyle.State_Off
    style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)

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
      model.setData(index, str(not index.data(Qt.UserRole) == 'True'), Qt.UserRole)
    return super().editorEvent(event, model, option, index)

  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    """
    Disable the editor for the whole required column by simply returning None
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: None

    """
    return None
