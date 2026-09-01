"""Graphics item representing one document in a relationship view."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import QRectF, Signal, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject

RADIUS = 24

class NodeItem(QGraphicsObject):
  """Selectable circular document node for the relationship scene."""
  clicked = Signal(str)

  def __init__(self, docID: str, color: QColor) -> None:
    """Create a node identified by ``docID`` and filled with ``color``.

    Args:
      docID: Document identifier represented by this node.
      color: Fill colour used when painting the node.
    """
    super().__init__()
    self.docID = docID
    self.color = color
    self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
    self.setCursor(Qt.CursorShape.PointingHandCursor)

  def boundingRect(self) -> QRectF:
    """Return the node's painted bounds."""
    return QRectF(-RADIUS - 1, -RADIUS - 1, 2 * RADIUS + 2, 2 * RADIUS + 2)

  def paint(self, painter: QPainter, _option: Any, _widget: Any = None) -> None:
    """Paint the node circle.

    Args:
      painter: Painter used to draw the node.
    """
    painter.setBrush(self.color)
    painter.setPen(QPen(QColor('#404040'), 1.0))
    painter.drawEllipse(QRectF(-RADIUS, -RADIUS, 2 * RADIUS, 2 * RADIUS))

  def mousePressEvent(self, event: Any) -> None:
    """Emit the single-click signal and pass the event to Qt.

    Args:
      event: Mouse event supplied by Qt.
    """
    self.clicked.emit(self.docID)
    super().mousePressEvent(event)
