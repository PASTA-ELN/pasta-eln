"""Resizable image preview widget for item details"""
import logging
from PySide6.QtCore import QByteArray, QRect, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap, QResizeEvent
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel, QLayout, QSizePolicy


class ResizeImage(QLabel):
  """QLabel that displays a base64 image and automatically rescales it"""
  def __init__(self, data: str, layout: QLayout|None = None) -> None:
    """Initialize an image label from encoded raster or SVG data

    Args:
      data (str): Base64-encoded image data to display
      layout (QLayout | None): Optional layout that should receive this label
    """
    super().__init__()
    self.sourcePixmap = QPixmap()
    self._isSvg = False
    self._svgRenderer = None
    self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.setMinimumSize(50, 50)
    if data.startswith('data:image/'):
      try:
        byteArr = QByteArray.fromBase64(bytearray(data[22:] if data[21] == ',' else data[23:], encoding='utf-8'))
        imageW = QImage()
        imageType = data[11:15].upper()
        success = imageW.loadFromData(byteArr, format=imageType[:-1] if imageType.endswith(';') else imageType)
        if not success:
          logging.warning('Could not load image data with format %s', imageType)
          return
        self.sourcePixmap = QPixmap.fromImage(imageW)
        if layout is not None:
          layout.addWidget(self)
        self._updatePixmap()
      except Exception:
        logging.exception('Error processing base64-image')
    elif data.startswith('<?xml'):
      self._isSvg = True
      self._svgRenderer = QSvgRenderer(QByteArray(data.encode('utf-8')), self)
      if layout is not None:
        layout.addWidget(self)
      self._updatePixmap()
    elif len(data) > 2:
      logging.error('ResizeImage: %s', data[:50], exc_info=True)


  def resizeEvent(self, event: QResizeEvent) -> None:
    """Scale the preview after the widget size changes
      Args:
        event (QResizeEvent): Qt event being handled
    """
    super().resizeEvent(event)
    self._updatePixmap()


  def _updatePixmap(self) -> None:
    """Refresh the displayed pixmap using the currently stored image data"""
    if self._isSvg:
      self._renderSvg()
      return
    if self.sourcePixmap.isNull():
      return
    scaled = self.sourcePixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
    super().setPixmap(scaled)


  def _renderSvg(self) -> None:
    """Render the stored SVG into the label's current display size"""
    if self._svgRenderer is None or not self._svgRenderer.isValid():
      return
    size = self.size()
    if size.width() <= 0 or size.height() <= 0:
      return
    scaled = self._svgRenderer.defaultSize().scaled(size, Qt.AspectRatioMode.KeepAspectRatio)
    x = (size.width() - scaled.width()) // 2
    y = (size.height() - scaled.height()) // 2
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    self._svgRenderer.render(painter, QRect(x, y, scaled.width(), scaled.height()))
    painter.end()
    super().setPixmap(pixmap)
