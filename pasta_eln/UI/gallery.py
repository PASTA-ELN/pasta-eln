""" Displays a scrollable grid of images (PNG, JPG, SVG) """
import logging
from typing import Any
from PySide6.QtCore import QByteArray, Qt, Signal, Slot
from PySide6.QtGui import QImage, QMouseEvent, QPixmap, QStandardItemModel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QGridLayout, QPushButton, QScrollArea, QVBoxLayout, QWidget
from .guiCommunicate import Communicate

IMG_SIZE = 300

class ClickableFrame(QPushButton):
  """
  A QPushbutton subclass that emits signals when clicked or double-clicked
  """
  clicked = Signal(str)
  doubleClicked = Signal(str)

  def __init__(self, docID: str):
    """
    Initialize

    Args:
      docID: The unique identifier for the image
    """
    super().__init__()
    self.docID = docID
    self.setFixedSize(IMG_SIZE, IMG_SIZE)
    self.setStyleSheet('border: none;')


  def mousePressEvent(self, event:QMouseEvent) -> None:
    """
    Handles mouse press events. Emits 'clicked' signal on left-button press

    Args:
      event: The QMouseEvent
    """
    if event.button() == Qt.LeftButton:                                           # type: ignore[attr-defined]
      self.clicked.emit(self.docID)
    return


  def mouseDoubleClickEvent(self, event:QMouseEvent) -> None:
    """
    Handles mouse double-click events. Emits 'doubleClicked' signal on left-button double-click

    Args:
      event: The QMouseEvent
    """
    if event.button() == Qt.LeftButton:                                           # type: ignore[attr-defined]
      self.doubleClicked.emit(self.docID)
    return


class ImageGallery(QWidget):
  """
  A widget that displays a scrollable grid of images (PNG, JPG, SVG)
  Images can be clicked or double-clicked to trigger actions
  """
  def __init__(self, comm:Communicate):
    """
    Initializes the ImageGallery

    Args:
      comm: The communication object used to interact with the backend and other UI components
    """
    super().__init__()
    self.comm = comm
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)
    self.data:dict[str,tuple[int,int]] = {}
    self.model:QStandardItemModel | None = None
    layout = QVBoxLayout(self)
    scrollArea = QScrollArea(self)
    scrollArea.setWidgetResizable(True)
    scrollContent = QWidget()
    self.gridL = QGridLayout(scrollContent)
    scrollArea.setWidget(scrollContent)
    layout.addWidget(scrollArea)

  def updateGrid(self, model:QStandardItemModel) -> None:
    """
    Args:
      model: The data model containing information about the images to display
             The first column of each row is expected to have an 'accessibleText'
    """
    self.data = {}
    self.model = model
    row, col = 0, 0
    for idx in range(self.model.rowCount()):
      docID = model.itemFromIndex(model.index(idx,0)).accessibleText()
      self.data[docID] = (row, col)
      col += 1
      if col >= 4:                                                                        # Assuming 4 columns
        col = 0
        row += 1
    # Clear existing widgets from the grid
    while self.gridL.count():
      child = self.gridL.takeAt(0)
      if child.widget():
        child.widget().deleteLater()
    return


  @Slot(dict)
  def onGetData(self, doc:dict[str,Any]) -> None:
    """
    Populates or updates the image grid based on the provided model

    Clears the existing grid and then iterates through the model to fetch
    and display images. It handles both SVG and raster image formats (like PNG, JPG)

    Args:
      doc (dict[str, Any]): A dictionary containing the document data.
    """
    if 'id' in doc and doc['id'] in self.data:
      if not doc or 'image' not in doc:
        # Handle cases where image data might be missing or malformed
        logging.warning('Image data not found or malformed for docID: %s', doc['id'])
        return
      image = doc['image']
      row, col = self.data[doc['id']]

      if image.startswith('<?xml version="1.0"'):
        # Wrap QSvgWidget in a Clickable subclass of QPushButton
        button = ClickableFrame(doc['id'])
        button.setFixedSize(IMG_SIZE, IMG_SIZE)
        svgWidget = QSvgWidget()
        svgWidget.renderer().load(bytearray(image, encoding='utf-8'))
        # Calculate aspect ratio for SVG
        svg_width = svgWidget.renderer().defaultSize().width()
        svg_height = svgWidget.renderer().defaultSize().height()

        if svg_width == 0 or svg_height == 0:                                         # Avoid division by zero
          new_width, new_height = IMG_SIZE -4, IMG_SIZE -4
        elif svg_height > svg_width:
          new_width = int(float(svg_width) / float(svg_height) * (IMG_SIZE - 4))
          new_height = IMG_SIZE - 4
        else:
          new_width = IMG_SIZE - 4
          new_height = int(float(svg_height) / float(svg_width) * (IMG_SIZE - 4))
        svgWidget.setMaximumSize(new_width, new_height)

        layout = QVBoxLayout(button)
        layout.addWidget(svgWidget)
        layout.setAlignment(Qt.AlignCenter)                                       # type: ignore[attr-defined]
        button.clicked.connect(lambda checked=False, docID=doc['id']: self.imageClicked(docID))
        button.doubleClicked.connect(self.image2Clicked)
        self.gridL.addWidget(button, row, col)
      elif 'base64,' in image:                                               # Basic check for base64 data URI
        try:
          header, base64_data = image.split(',', 1)
          # Extract image type from header (e.g., "data:image/png;base64")
          img_type_part = header.split(';')[0].split('/')[-1]
          imageType = img_type_part.upper()

          byteArr = QByteArray.fromBase64(bytearray(base64_data, encoding='utf-8'))
          imageW = QImage()
          # Ensure format string is clean (e.g. PNG, JPEG)
          fmt = imageType.replace(';', '')
          if imageW.loadFromData(byteArr, format=fmt):
            pixmap = QPixmap.fromImage(imageW).scaled(IMG_SIZE,IMG_SIZE,Qt.KeepAspectRatio,Qt.SmoothTransformation)# type: ignore[attr-defined]
            button = ClickableFrame(doc['id'])
            button.setIcon(pixmap)
            button.setAlignment(Qt.AlignCenter)                                   # type: ignore[attr-defined]
            button.clicked.connect(self.imageClicked)
            button.doubleClicked.connect(self.image2Clicked)
            self.gridL.addWidget(button, row, col)
          else:
            logging.warning('Could not load image data for docID: %s with format %s', doc['id'], fmt)
        except Exception as e:
          logging.warning('Error processing image for docID %s: %s', doc['id'], e)
      else:
        logging.warning('Image for docID is not in expected base64 format. %s', doc['id'])
    return


  def imageClicked(self, docID:str) -> None:
    """
    Handles single-click events on an image

    Args:
      docID: The unique identifier of the clicked image/document
    """
    self.comm.changeDetails.emit(docID)
    return


  def image2Clicked(self, docID:str) -> None:
    """
    Handles double-click events on an image

    Args:
      docID: The unique identifier of the double-clicked image/document
    """
    self.comm.formDoc.emit({'id':docID})
    return
