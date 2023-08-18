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
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRect
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
    button = QRadioButton()
    button.setChecked(True)
    opt = QStyleOptionButton()
    opt.state = QStyle.State_Active | QStyle.State_Selected
    opt.rect = QRect(option.rect.left() + option.rect.width() / 2 - 5,
                     option.rect.top(),
                     option.rect.width(),
                     option.rect.height())
    QApplication.style().drawControl(QStyle.CE_RadioButton, opt, painter, button)

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    return None

  def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem,
                           index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    editor.setGeometry(option.rect)


