"""A tab bar which keeps the project overview tab visually separate."""
from PySide6.QtCore import Slot
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QTabBar

class ProjectTabBar(QTabBar):
  """A tab bar which keeps the project overview tab visually separate."""

  _HOME_TAB_DATA = 'project-home'
  _HOME_TAB_GAP = 12

  def __init__(self, separatorColor: str) -> None:
    super().__init__()
    self._draggingHomeTab = False                                   # if the dragging action uses the home-tab
    self._separatorColor = QColor(separatorColor)
    self.setStyleSheet(f"QTabBar::tab:first {{ margin-right: {self._HOME_TAB_GAP}px; }}")
    self.tabMoved.connect(self.keepHomeTabFirst)

  def markHomeTab(self, index: int) -> None:
    """Mark the tab which must remain first in the tab bar."""
    self.setTabData(index, self._HOME_TAB_DATA)


  def paintEvent(self, event: QPaintEvent) -> None:
    """Draw a separator in the gap following the Home tab."""
    super().paintEvent(event)
    for index in range(self.count()):
      if self.tabData(index) == self._HOME_TAB_DATA:
        homeTabRect = self.tabRect(index)
        separatorX = homeTabRect.right() - self._HOME_TAB_GAP // 2
        painter = QPainter(self)
        separatorPen = QPen(self._separatorColor)
        separatorPen.setWidth(1)
        separatorPen.setDashPattern([1, 1])
        painter.setPen(separatorPen)
        painter.drawLine(separatorX, 4, separatorX, self.height() - 5)
        painter.end()
        return


  def mousePressEvent(self, event: QMouseEvent) -> None:
    """Remember whether a drag was initiated on the Home tab."""
    self._draggingHomeTab = self.tabData(self.tabAt(event.position().toPoint())) == self._HOME_TAB_DATA
    super().mousePressEvent(event)


  def mouseMoveEvent(self, event: QMouseEvent) -> None:
    """Allow table tabs to move, but never the Home tab."""
    if not self._draggingHomeTab:
      super().mouseMoveEvent(event)


  def mouseReleaseEvent(self, event: QMouseEvent) -> None:
    """End the potential Home-tab drag."""
    self._draggingHomeTab = False
    super().mouseReleaseEvent(event)


  @Slot(int, int)
  def keepHomeTabFirst(self, _: int, __: int) -> None:
    """Move Home back if another tab was dragged before it."""
    for index in range(self.count()):
      if self.tabData(index) == self._HOME_TAB_DATA:
        if index != 0:
          self.moveTab(index, 0)
        return
