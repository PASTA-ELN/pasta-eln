"""Reusable delegate for icon buttons embedded in table cells."""
from collections.abc import Callable
from typing import TypeAlias
import qtawesome as qta
from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QObject, QPersistentModelIndex, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QPushButton, QStyle, QStyledItemDelegate, QStyleOptionButton,
                               QStyleOptionViewItem, QWidget)
from .data_hierarchy.utility_functions import isClickWithinBounds

CellIndex: TypeAlias = QModelIndex | QPersistentModelIndex
IsVisible: TypeAlias = Callable[[QModelIndex], bool]
OnClick: TypeAlias = Callable[[QAbstractItemModel, QModelIndex], None]


class IconButtonDelegate(QStyledItemDelegate):
  """Paint an icon button and invoke a supplied action when it is clicked."""

  def __init__(self, icon: str, isVisible: IsVisible, onClick: OnClick, parent: QObject | None = None) -> None:
    super().__init__(parent)
    self.icon = icon
    self.isVisible = isVisible
    self.onClick = onClick
    self.button = QPushButton()

  def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: CellIndex) -> None:
    """Draw the configured button when the row supports its action."""
    if not self.isVisible(index):                                                     # type: ignore[arg-type]
      return
    buttonOption = QStyleOptionButton()
    buttonOption.state = QStyle.StateFlag.State_Active | QStyle.StateFlag.State_Enabled
    buttonOption.rect = option.rect
    buttonOption.icon = qta.icon(self.icon, scale_factor=1.0)
    buttonOption.iconSize = QSize(15, 15)
    QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, buttonOption, painter, self.button)

  def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: CellIndex) -> QWidget:
    """Icon buttons do not create in-place editors."""
    return None                                                                   # type: ignore[return-value]

  def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem,
                  index: CellIndex) -> bool:
    """Run the configured action for clicks inside a visible button cell."""
    if self.isVisible(index):                                                         # type: ignore[arg-type]
      if not isClickWithinBounds(event, option):
        return False
      self.onClick(model, index)                                                      # type: ignore[arg-type]
      return True
    return False
