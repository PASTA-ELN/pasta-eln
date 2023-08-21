#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: required_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union

import PySide6.QtCore
import PySide6.QtWidgets

from PySide6.QtGui import QPainter
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QEvent, QAbstractItemModel, QRect
from PySide6.QtWidgets import QStyledItemDelegate, QRadioButton, QWidget, QStyleOptionViewItem, QStyleOptionButton, \
  QStyle, QApplication


class RequiredColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the radio buttons for the required column in property table
  """

  def __init__(self):
    """
      Constructor
    """
    super().__init__()

  def paint(self, painter: QPainter, option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    widget = option.widget
    style = widget.style() if widget else QApplication.style()
    opt = QStyleOptionButton()
    opt.rect = QRect(option.rect.left() + option.rect.width() / 2 - 5,
                     option.rect.top(),
                     option.rect.width(),
                     option.rect.height())
    opt.state |= QStyle.State_On if bool(index.data(PySide6.QtCore.Qt.UserRole)) else QStyle.State_Off
    style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)

  def editorEvent(self, event: QEvent, model: QAbstractItemModel,
                  option: QStyleOptionViewItem,
                  index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    if event.type() == QEvent.MouseButtonRelease:
      model.setData(index, not bool(index.data(PySide6.QtCore.Qt.UserRole)), PySide6.QtCore.Qt.UserRole)
    return super().editorEvent(event, model, option, index)

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    return None

  def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem,
                           index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    editor.setGeometry(option.rect)
