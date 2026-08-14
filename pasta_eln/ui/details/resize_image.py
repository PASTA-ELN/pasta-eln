"""Resizable image preview widget for item details."""
import logging
from PySide6.QtCore import QByteArray, QRect, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap, QResizeEvent
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel, QLayout, QSizePolicy


class ResizeImage(QLabel):
  """QLabel that displays a base64 image and automatically rescales it."""
  def __init__(self, data: str, layout: QLayout|None = None) -> None:
    super().__init__()
    self._sourcePixmap = QPixmap()
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
        success = imageW.loadFromData(byteArr, format=imageType[:-1] if imageType.endswith(';') else imageType)# type: ignore[arg-type]
        if not success:
          logging.warning('Could not load image data with format %s', imageType)
          return
        self._sourcePixmap = QPixmap.fromImage(imageW)
        if layout is not None:
          layout.addWidget(self)
        self._updatePixmap()
      except Exception as error:
        logging.warning('Error processing base64-image %s', error)
    elif data.startswith('<?xml'):
      self._isSvg = True
      self._svgRenderer = QSvgRenderer(QByteArray(data.encode('utf-8')), self)
      if layout is not None:
        layout.addWidget(self)
      self._updatePixmap()
    elif len(data) > 2:
      logging.error('ResizeImage: %s', data[:50], exc_info=True)

  def resizeEvent(self, event: QResizeEvent) -> None:
    """Scale the preview after the widget size changes."""
    super().resizeEvent(event)
    self._updatePixmap()

  def _updatePixmap(self) -> None:
    if self._isSvg:
      self._renderSvg()
      return
    if self._sourcePixmap.isNull():
      return
    scaled = self._sourcePixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
    super().setPixmap(scaled)

  def _renderSvg(self) -> None:
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

  def setSourcePixmap(self, pixmap: QPixmap) -> None:
    """Replace the source image."""
    self._sourcePixmap = pixmap
    self._updatePixmap()

  def sourcePixmap(self) -> QPixmap:
    """Return the original image."""
    return self._sourcePixmap
