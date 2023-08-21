#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: delete_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QEvent, QAbstractItemModel, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QPushButton, QWidget, QStyleOptionViewItem, QStyleOptionButton, \
  QStyle, QApplication

from pasta_eln.ontology_configuration.utility_functions import is_click_within_bounds


class DeleteColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the delete icon for the delete column in property table
  """
  delete_clicked_signal = Signal(int, int)

  def __init__(self):
    """
      Constructor
    """
    super().__init__()

  def paint(self, painter: QPainter, option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    button = QPushButton()
    opt = QStyleOptionButton()
    opt.state = QStyle.State_Active | QStyle.State_Enabled
    opt.rect = option.rect
    opt.text = "Delete"
    button.setDisabled(False)
    QApplication.style().drawControl(QStyle.CE_PushButton, opt, painter, button)

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    return None

  def editorEvent(self, event: QEvent, model: QAbstractItemModel,
                  option: QStyleOptionViewItem,
                  index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    if is_click_within_bounds(event, option):
      self.delete_clicked_signal.emit(index.row(), index.column())
    return True
