#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: delete_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QEvent, QAbstractItemModel, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QPushButton, QWidget, QStyleOptionViewItem, QStyleOptionButton, \
  QStyle, QApplication

from pasta_eln.ontology_configuration.utility_functions import is_click_within_bounds


class DeleteColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the delete icon for the delete column in the ontology table views
  """
  delete_clicked_signal = Signal(
    int)  # Signal to inform the delete button click with the position in the table as the parameter

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
    Draws the delete button within the cell represented by index
    Args:
      painter (QPainter): Painter instance for painting the button.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: None

    """
    button = QPushButton()
    opt = QStyleOptionButton()
    opt.state = QStyle.State_Active | QStyle.State_Enabled
    opt.rect = option.rect
    opt.text = "Delete"
    QApplication.style().drawControl(QStyle.CE_PushButton, opt, painter, button)

  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Disable the editor for the delete column by simply returning None
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: None

    """
    return None

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
    if is_click_within_bounds(event, option):
      row = index.row()
      self.logger.info(f"Delete signal emitted for the position: {row}")
      self.delete_clicked_signal.emit(row)
      return True
    return False
