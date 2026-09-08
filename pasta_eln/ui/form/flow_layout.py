"""Wrapping layout used for the form's tag controls"""
from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem


class FlowLayout(QLayout):
  """A simple flow layout that wraps tags into multiple rows"""
  def __init__(self, spacing:int=-1):
    """Initialize an empty wrapping layout with the requested spacing

    Args:
      spacing (int): Gap, in pixels, between adjacent layout items; ``-1`` uses Qt's default
    """
    super().__init__(None)
    self.itemList:list[QLayoutItem] = []
    if spacing >= 0:
      self.setSpacing(spacing)

  def addItem(self, item:QLayoutItem) -> None:
    """Add an item to the layout
      Args:
        item (QLayoutItem): layout or model item being handled
    """
    self.itemList.append(item)

  def count(self) -> int:
    """Return the number of items in the layout
      Returns:
        int: Number of items in the layout
    """
    return len(self.itemList)

  def itemAt(self, index:int) -> QLayoutItem|None:
    """Return the item at ``index`` when it exists
      Args:
        index (int): model index associated with the event
      Returns:
        QLayoutItem | None: Layout item at the requested index, if present
    """
    return self.itemList[index] if 0 <= index < len(self.itemList) else None

  def takeAt(self, index:int) -> QLayoutItem:
    """Remove and return the item at ``index``
      Args:
        index (int): model index associated with the event
      Returns:
        QLayoutItem: Removed layout item
    """
    return self.itemList.pop(index) if 0 <= index < len(self.itemList) else QLayoutItem()

  def expandingDirections(self) -> Qt.Orientation:
    """Do not request expansion in either direction
      Returns:
        Qt.Orientation: Supported layout expansion directions
    """
    return Qt.Orientations(0)                                                     # type: ignore[attr-defined]

  def hasHeightForWidth(self) -> bool:
    """Report that layout height depends on width
      Returns:
        bool: Whether layout height depends on width
    """
    return True

  def heightForWidth(self, width:int) -> int:
    """Calculate the needed height at ``width``
      Args:
        width (int): available width
      Returns:
        int: Required layout height for the given width
    """
    return self._doLayout(QRect(0, 0, width, 0), True)

  def setGeometry(self, rect:QRect) -> None:
    """Lay out items within ``rect``
      Args:
        rect (QRect): available layout rectangle
    """
    super().setGeometry(rect)
    self._doLayout(rect, False)

  def sizeHint(self) -> QSize:
    """Return the minimum size as the preferred size
      Returns:
        QSize: Preferred layout size
    """
    return self.minimumSize()

  def minimumSize(self) -> QSize:
    """Return the combined minimum size of all items
      Returns:
        QSize: Minimum layout size
    """
    size = QSize()
    for item in self.itemList:
      size = size.expandedTo(item.sizeHint())
    margins:tuple[int,int,int,int] = self.getContentsMargins()                      # type: ignore[assignment]
    size += QSize(margins[0] + margins[2], margins[1] + margins[3])
    return size

  def _doLayout(self, rect:QRect, testOnly:bool) -> int:
    """Lay out items and return the required height
      Args:
        rect (QRect): available layout rectangle
        testOnly (bool): whether to calculate layout without applying it
      Returns:
        int: Required layout height
    """
    margins:tuple[int,int,int,int] = self.getContentsMargins()                      # type: ignore[assignment]
    effective = rect.adjusted(margins[0], margins[1], -margins[2], -margins[3])
    x = effective.x()
    y = effective.y()
    lineHeight = 0
    spacingX = self.spacing()
    spacingY = self.spacing()
    for item in self.itemList:
      itemSize = item.sizeHint()
      nextX = x + itemSize.width() + spacingX
      if nextX - spacingX > effective.x() + effective.width() and lineHeight > 0:
        x = effective.x()
        y += lineHeight + spacingY
        lineHeight = 0
        nextX = x + itemSize.width() + spacingX
      if not testOnly:
        item.setGeometry(QRect(QPoint(x, y), itemSize))
      x = nextX
      lineHeight = max(lineHeight, itemSize.height())
    return y + lineHeight + margins[3] - rect.y()
