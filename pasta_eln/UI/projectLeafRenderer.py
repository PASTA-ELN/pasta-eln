""" renders each leaf of project tree using QPaint """
import base64
import logging
from typing import Any
from PySide6.QtCore import QMargins, QModelIndex, QPoint, QRectF, QSize, Qt, Slot# pylint: disable=no-name-in-module
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QStaticText, QTextDocument# pylint: disable=no-name-in-module
from PySide6.QtSvg import QSvgRenderer                                     # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem    # pylint: disable=no-name-in-module
from .guiCommunicate import Communicate


class ProjectLeafRenderer(QStyledItemDelegate):
  """ renders each leaf of project tree using QPaint """
  def __init__(self, comm:Communicate) -> None:
    super().__init__()
    self.comm          = comm
    self.comm.leafChanged.connect(self.dataChanged)
    self.debugMode     = logging.root.level<logging.INFO
    self.widthImage    = self.comm.configuration['GUI']['imageWidthProject']
    self.widthContent  = self.comm.configuration['GUI']['widthContent']
    self.docTypeOffset = self.comm.configuration['GUI']['docTypeOffset']
    self.frameSize     = self.comm.configuration['GUI']['frameSize']
    self.maxHeight     = self.comm.configuration['GUI']['maxProjectLeafHeight']
    self.lineSep       = 20
    self.penDefault    = QPen(QColor(self.comm.palette.text))
    self.penHighlight  = QPen(QColor(self.comm.palette.primary))
    self.penHighlight.setWidth(2)
    self.docID         = ''
    self.index:None|QModelIndex = None

  def paint(self, painter:QPainter, option:QStyleOptionViewItem, index:QModelIndex) -> None:    # type: ignore
    """
    Paint this item
    - coordinates: left, top
    - COS top left

    Args:
      painter (QPainter): painter
      option (QStyleOptionViewItem): option incl. current coordinates
      index (QModelIndex): index
    """
    name = index.data(Qt.ItemDataRole.DisplayRole)
    data = index.data(Qt.ItemDataRole.UserRole+1)
    if not data or data['hierStack'] is None or self.comm is None:
      return
    docID   = data['hierStack'].split('/')[-1]
    painter.setPen(self.penDefault)
    x0, y0 = option.rect.topLeft().toTuple()                                      # type: ignore[attr-defined]
    widthContent = min(self.widthContent,  \
                       int((option.rect.bottomRight()-option.rect.topLeft()).toTuple()[0]/2) )# type: ignore[attr-defined]
    docTypeOffset = min(self.docTypeOffset, \
                        int((option.rect.bottomRight()-option.rect.topLeft()).toTuple()[0]/3.5) )# type: ignore[attr-defined]
    bottomRight2nd = option.rect.bottomRight()- QPoint(self.frameSize+1,self.frameSize)# type: ignore[attr-defined]
    painter.fillRect(option.rect.marginsRemoved(QMargins(2,6,4,0)),  self.comm.palette.leafShadow)# type: ignore[attr-defined]
    if data['docType'][0][0]=='x':
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.comm.palette.leafX)# type: ignore[attr-defined]
    else:
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.comm.palette.leafO)# type: ignore[attr-defined]
    # header
    y = self.lineSep/2
    docTypeText= '/'.join(data['docType'])
    if data['docType'][0][0]=='x':
      docTypeText = self.comm.docTypesTitles['x1']['title'].lower()[:-1]
    maxCharacter = int(docTypeOffset/7.5)
    nameText = name if len(name)<maxCharacter else f'...{name[-maxCharacter+3:]}'
    if not data['gui'][0]:                                                               #Only draw first line
      staticText = QStaticText(f'<strong>{nameText} (...)</strong>')
      staticText.setTextWidth(docTypeOffset)
      painter.drawStaticText(x0, y0+y, staticText)
      painter.drawStaticText(x0+docTypeOffset, y0+y, QStaticText(docTypeText))
      return
    hiddenText = '     \U0001F441' if self.comm.leafs.get(docID, {}).get('hidden', False) else ''
    staticText = QStaticText(f'<strong>{nameText} {hiddenText}</strong>')
    staticText.setTextWidth(docTypeOffset)
    painter.drawStaticText(x0, y0+y, staticText)
    painter.drawStaticText(x0+docTypeOffset, y0+y, QStaticText(docTypeText))
    if self.debugMode:
      painter.drawStaticText(x0+700, y0+y, QStaticText(data['hierStack']))
    textDoc = QTextDocument()
    textDoc.setMarkdown(self.comm.leafs.get(docID, {}).get('markdown',''))
    painter.translate(QPoint(x0-3, y0+y+15))
    self.drawTextDocument(painter, textDoc, int(self.maxHeight-6*self.frameSize))
    painter.translate(-QPoint(x0-3, y0+y+15))
    # right side
    if self.comm.leafs.get(docID,{}).get('content','') and not self.comm.leafs.get(docID,{}).get('image',''):
      textDoc = QTextDocument()
      textDoc.setMarkdown(self.comm.leafs.get(docID,{}).get('content',''))
      textDoc.setTextWidth(widthContent)
      width:int = textDoc.size().toTuple()[0]                                                   # type: ignore
      topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)# type: ignore[attr-defined]
      painter.translate(topLeftContent)
      self.drawTextDocument(painter, textDoc, int(self.maxHeight-3*self.frameSize))
      topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)# type: ignore[attr-defined]
      painter.translate(-topLeftContent)
    if self.comm.leafs.get(docID,{}).get('image',''):
      if self.comm.leafs.get(docID,{}).get('image','').startswith('data:image/'):
        pixmap = self.imageFromDoc(self.comm.leafs.get(docID,{}))
        width2nd = min(self.widthImage, pixmap.width()+self.frameSize)
        topLeft2nd     = option.rect.topRight()   - QPoint(width2nd+self.frameSize+1,-self.frameSize)# type: ignore[attr-defined]
        painter.drawPixmap(topLeft2nd, pixmap)
      elif self.comm.leafs.get(docID,{}).get('image','').startswith('<?xml'):
        topLeft2nd     = option.rect.topRight()   - QPoint(self.widthImage+self.frameSize+1,-self.frameSize)# type: ignore[attr-defined]
        image = QSvgRenderer(bytearray(self.comm.leafs.get(docID,{}).get('image',''), encoding='utf-8'))
        image.render(painter,    QRectF(topLeft2nd, bottomRight2nd))
    return


  def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex) -> QSize:                  # type: ignore
    """
    determine size of this leaf
    """
    if not index or not index.data(Qt.ItemDataRole.UserRole+1):
      return QSize()
    self.index = index
    hierStack = index.data(Qt.ItemDataRole.UserRole+1)['hierStack']
    if hierStack is None or self.comm is None:
      return QSize()
    if not index.data(Qt.ItemDataRole.UserRole+1)['gui'][0]:              # only show the headline, no details
      return QSize(400, self.lineSep*2)
    self.docID   = hierStack.split('/')[-1]
    if self.docID not in self.comm.leafs:
      self.comm.leafWidth = min(self.widthContent,
                                int((option.rect.bottomRight()-option.rect.topLeft()).toTuple()[0]/2) )# type: ignore[attr-defined]
      self.comm.commSendDoc.emit(self.docID, 'size')
    return self.comm.leafs.get(self.docID, {}).get('size', QSize(400,self.maxHeight))
    # if len(doc)<2:
    #   if len(self.comm.backend.db.getDoc(hierStack.split('/')[0], noError=True))>2:#only refresh if project still exists
    #     self.comm.changeProject.emit('','')
    #   return QSize()


  @Slot(str)
  def dataChanged(self, docID:str) -> None:
    """ Update the size of the leaf: emit signal
    Args:
      docID (str): document ID
    """
    if docID == self.docID:
      self.sizeHintChanged.emit(self.index)


  def drawTextDocument(self, painter:QPainter, textDoc:QTextDocument, yMax:int) -> None:
    """ Draw text document

    Args:
      painter (QPainter): painter
      textDoc (QTextDocument): text document
      yMax (int): maximum height of document in surrounding frame
    """
    width:int  = textDoc.size().toTuple()[0]                                                    # type: ignore
    height:int = textDoc.size().toTuple()[1]                                                    # type: ignore
    textDoc.drawContents(painter, QRectF(0, 0, width, yMax))
    if height > yMax+self.frameSize:
      painter.setPen(self.penHighlight)
      painter.drawLine(self.frameSize, yMax+self.frameSize, width-self.frameSize, yMax+self.frameSize)
      painter.setPen(self.penDefault)
    return


  def imageFromDoc(self, doc:dict[str,Any]) -> QPixmap:
    """ Create image from image in doc

    Args:
      doc (dict): document

    Returns:
      QPixmap: image
    """
    result = QPixmap()
    result.loadFromData(base64.b64decode(doc['image'][22:]))
    result = result.scaledToWidth(self.widthImage)
    if result.height()>self.maxHeight:
      result = result.scaledToHeight(self.maxHeight-self.frameSize*2)
    return result
