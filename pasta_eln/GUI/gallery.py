from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QScrollArea, QGridLayout, QPushButton)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, Signal, QByteArray
from PySide6.QtSvgWidgets import QSvgWidget

IMG_SIZE = 300

class ClickableImage(QLabel):
  clicked = Signal(str)
  doubleClicked = Signal(str)

  def __init__(self, image_id):
    super().__init__()
    self.image_id = image_id

  def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.clicked.emit(self.image_id)

  def mouseDoubleClickEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.doubleClicked.emit(self.image_id)



class ClickableSvgButton(QPushButton):
  doubleClicked = Signal(str)

  def __init__(self, image_id):
    super().__init__()
    self.image_id = image_id
    self.setFixedSize(200, 200)
    self.setStyleSheet("border: none;")

  def mouseDoubleClickEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.doubleClicked.emit(self.image_id)



class ImageGallery(QWidget):
  def __init__(self, comm):
    super().__init__()
    self.comm = comm
    layout = QVBoxLayout(self)
    scrollArea = QScrollArea(self)
    scrollArea.setWidgetResizable(True)
    scrollContent = QWidget()
    self.gridL = QGridLayout(scrollContent)
    scrollArea.setWidget(scrollContent)
    layout.addWidget(scrollArea)

  def updateGrid(self, model) -> None:
    row, col = 0, 0
    for idx in range(model.rowCount()):
      docID = model.itemFromIndex(model.index(idx,0)).accessibleText()
      image = self.comm.backend.db.getDoc(docID)['image']
      if image.startswith('<?xml version="1.0"'):
        # Wrap QSvgWidget in a Clickable subclass of QPushButton
        button = ClickableSvgButton(docID)
        button.setFixedSize(IMG_SIZE, IMG_SIZE)
        button.setStyleSheet("border: none;")  # Hide button border
        svgWidget = QSvgWidget()
        svgWidget.renderer().load(bytearray(image, encoding='utf-8'))
        if svgWidget.height()>svgWidget.width():
          svgWidget.setMaximumSize(int(float(svgWidget.width())/float(svgWidget.height())*IMG_SIZE-4) ,IMG_SIZE-4)
        else:
          svgWidget.setMaximumSize(IMG_SIZE-4, int(float(svgWidget.height())/float(svgWidget.width())*IMG_SIZE-4))
        layout = QVBoxLayout(button)
        layout.addWidget(svgWidget)
        layout.setAlignment(Qt.AlignCenter)
        button.clicked.connect(lambda id=docID: self.imageClicked(id))
        button.doubleClicked.connect(self.image2Clicked)
        self.gridL.addWidget(button, row, col)
      else:  # PNG et al
        byteArr = QByteArray.fromBase64(bytearray(image[22:] if image[21]==',' else image[23:], encoding='utf-8'))
        imageW = QImage()
        imageType = image[11:15].upper()
        imageW.loadFromData(byteArr, format=imageType[:-1] if imageType.endswith(';') else imageType) #type: ignore[arg-type]
        pixmap = QPixmap.fromImage(imageW).scaled(IMG_SIZE, IMG_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label = ClickableImage(docID)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.clicked.connect(self.imageClicked)
        label.doubleClicked.connect(self.image2Clicked)
        self.gridL.addWidget(label, row, col)
      # end of loop
      col += 1
      if col >= 4:
        col = 0
        row += 1
    return

  def imageClicked(self, docID):
    self.comm.changeDetails.emit(docID)

  def image2Clicked(self, docID):
    doc = self.comm.backend.db.getDoc(docID)
    self.comm.formDoc.emit(doc)
