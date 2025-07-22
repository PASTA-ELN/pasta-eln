""" renders each leaf of project tree using QPaint """
import base64
import logging
from typing import Any
from PySide6.QtCore import QMargins, QModelIndex, QPoint, QRectF, QSize, Qt# pylint: disable=no-name-in-module
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QStaticText, QTextDocument# pylint: disable=no-name-in-module
from PySide6.QtSvg import QSvgRenderer                                     # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem    # pylint: disable=no-name-in-module
from ..fixedStringsJson import DO_NOT_RENDER, defaultDataHierarchyNode
from .guiCommunicate import Communicate
from ..textTools.handleDictionaries import doc2markdown
from ..textTools.stringChanges import markdownEqualizer


class ProjectLeafRenderer(QStyledItemDelegate):
  """ renders each leaf of project tree using QPaint """
  def __init__(self, comm:Communicate) -> None:
    super().__init__()
    self.comm          = comm
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
    # details = body
    doc     = {'name':'test','type':['-'], 'branch':[{'show':[True]}]}#TODO self.comm.backend.db.getDoc(docID)
    if not doc:
      return
    dataHierarchyNode = []  #TODO
    # if doc['type'][0] not in self.comm.backend.db.dataHierarchy('', ''): #TODO use other type in hierarchy
    #   dataHierarchyNode = defaultDataHierarchyNode
    # else:
    #   dataHierarchyNode = self.comm.backend.db.dataHierarchy(doc['type'][0], 'meta')
    if len(doc)<2:
      logging.error('LeafRenderer: Cannot read docID %s',docID)
      return
    hiddenText = ('     \U0001F441' if [b for b in doc['branch'] if False in b['show']] else '')
    staticText = QStaticText(f'<strong>{nameText} {hiddenText}</strong>')
    staticText.setTextWidth(docTypeOffset)
    painter.drawStaticText(x0, y0+y, staticText)
    painter.drawStaticText(x0+docTypeOffset, y0+y, QStaticText(docTypeText))
    if self.debugMode:
      painter.drawStaticText(x0+700, y0+y, QStaticText(data['hierStack']))
    textDoc = QTextDocument()
    textDoc.setMarkdown(doc2markdown(doc, DO_NOT_RENDER, dataHierarchyNode, self))
    painter.translate(QPoint(x0-3, y0+y+15))
    self.drawTextDocument(painter, textDoc, int(self.maxHeight-6*self.frameSize))
    painter.translate(-QPoint(x0-3, y0+y+15))
    # right side
    if 'content' in doc and doc['content'] and ('image' not in doc or not doc['image']):
      textDoc = QTextDocument()
      textDoc.setMarkdown(markdownEqualizer(doc['content']))
      textDoc.setTextWidth(widthContent)
      width:int = textDoc.size().toTuple()[0]                                                   # type: ignore
      topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)# type: ignore[attr-defined]
      painter.translate(topLeftContent)
      self.drawTextDocument(painter, textDoc, int(self.maxHeight-3*self.frameSize))
      topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)# type: ignore[attr-defined]
      painter.translate(-topLeftContent)
    if 'image' in doc and doc['image']:
      if doc['image'].startswith('data:image/'):
        pixmap = self.imageFromDoc(doc)
        width2nd = min(self.widthImage, pixmap.width()+self.frameSize)
        topLeft2nd     = option.rect.topRight()   - QPoint(width2nd+self.frameSize+1,-self.frameSize)# type: ignore[attr-defined]
        painter.drawPixmap(topLeft2nd, pixmap)
      elif doc['image'].startswith('<?xml'):
        topLeft2nd     = option.rect.topRight()   - QPoint(self.widthImage+self.frameSize+1,-self.frameSize)# type: ignore[attr-defined]
        image = QSvgRenderer(bytearray(doc['image'], encoding='utf-8'))
        image.render(painter,    QRectF(topLeft2nd, bottomRight2nd))
    return


  def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex) -> QSize:                  # type: ignore
    """
    determine size of this leaf
    """
    if not index or not index.data(Qt.ItemDataRole.UserRole+1):
      return QSize()
    hierStack = index.data(Qt.ItemDataRole.UserRole+1)['hierStack']
    if hierStack is None or self.comm is None:
      return QSize()
    if not index.data(Qt.ItemDataRole.UserRole+1)['gui'][0]:              # only show the headline, no details
      return QSize(400, self.lineSep*2)
    docID   = hierStack.split('/')[-1]
    if docID not in self.comm.leafSizes:
      #TODO
      pass
    return self.comm.leafSizes.get(docID, QSize(400,self.maxHeight))

    #TODO move to comm
    # doc = self.comm.backend.db.getDoc(docID, noError=True)# No error plotted if doc not found: ..
    # # ... after deleting project, its items cannot be found and it would give many false negatives
    # if len(doc)<2:
    #   if len(self.comm.backend.db.getDoc(hierStack.split('/')[0], noError=True))>2:#only refresh if project still exists
    #     self.comm.changeProject.emit('','')
    #   return QSize()
    # widthContent = min(self.widthContent,  \
    #                    int((option.rect.bottomRight()-option.rect.topLeft()).toTuple()[0]/2) )# type: ignore[attr-defined]
    # if doc['type'][0] not in self.comm.backend.db.dataHierarchy('', ''):
    #   dataHierarchyNode = defaultDataHierarchyNode
    # else:
    #   dataHierarchyNode = self.comm.backend.db.dataHierarchy(doc['type'][0], 'meta')
    # textDoc = QTextDocument()
    # textDoc.setMarkdown(doc2markdown(doc, DO_NOT_RENDER, dataHierarchyNode, self))
    # textDoc.setTextWidth(widthContent)
    # heightDetails = int(textDoc.size().toTuple()[1])+self.frameSize+20                          # type: ignore
    # heightRightSide = -1
    # if 'content' in doc:
    #   textDoc.setMarkdown(doc['content'])
    #   heightRightSide = int(textDoc.size().toTuple()[1])                                        # type: ignore
    # elif 'image' in doc and doc['image']:
    #   if doc['image'].startswith('data:image/'):
    #     pixmap = self.imageFromDoc(doc)
    #     heightRightSide = pixmap.height()+2*self.frameSize
    #   else:
    #     heightRightSide = int(self.widthImage*3/4+2*self.frameSize)
    # return QSize(400, min(max(heightDetails,heightRightSide), self.maxHeight))


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
