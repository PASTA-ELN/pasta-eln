""" renders each leaf of project tree using QPaint """
import base64, logging
from typing import Any
from PySide6.QtCore import Qt, QSize, QPoint, QMargins, QRectF, QModelIndex# pylint: disable=no-name-in-module
from PySide6.QtGui import QStaticText, QPixmap, QTextDocument, QPainter, QColor, QPen # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem # pylint: disable=no-name-in-module
from PySide6.QtSvg import QSvgRenderer                        # pylint: disable=no-name-in-module
from ..guiCommunicate import Communicate
from ..stringChanges import markdownEqualizer
from ..guiStyle import addDocDetails, CSS_STYLE
from ..fixedStringsJson import defaultDataHierarchyNode

DO_NOT_RENDER = ['image','content','metaVendor','metaUser','shasum','type','branch','gui','dateCreated',
                 'dateModified','id','user','name','comment','externalId','client']

class ProjectLeafRenderer(QStyledItemDelegate):
  """ renders each leaf of project tree using QPaint """
  def __init__(self, comm:Communicate) -> None:
    super().__init__()
    self.comm          = comm
    self.debugMode     = logging.root.level<logging.INFO
    self.widthImage    = self.comm.backend.configuration['GUI']['imageWidthProject']
    self.widthContent  = self.comm.backend.configuration['GUI']['widthContent']
    self.docTypeOffset = self.comm.backend.configuration['GUI']['docTypeOffset']
    self.frameSize     = self.comm.backend.configuration['GUI']['frameSize']
    self.maxHeight     = self.comm.backend.configuration['GUI']['maxProjectLeafHeight']
    self.lineSep       = 20
    self.penDefault    = QPen(QColor(self.comm.palette.text))
    self.penHighlight  = QPen(QColor(self.comm.palette.primary))
    self.penHighlight.setWidth(2)

  def paint(self, painter:QPainter, option:QStyleOptionViewItem, index:QModelIndex) -> None:                 # type: ignore
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
    x0, y0 = option.rect.topLeft().toTuple()                                                                  # type: ignore[attr-defined]
    widthContent = min(self.widthContent,  \
                       int((option.rect.bottomRight()-option.rect.topLeft()).toTuple()[0]/2) )                # type: ignore[attr-defined]
    docTypeOffset = min(self.docTypeOffset, \
                        int((option.rect.bottomRight()-option.rect.topLeft()).toTuple()[0]/3.5) )             # type: ignore[attr-defined]
    bottomRight2nd = option.rect.bottomRight()- QPoint(self.frameSize+1,self.frameSize)                       # type: ignore[attr-defined]
    painter.fillRect(option.rect.marginsRemoved(QMargins(2,6,4,0)),  self.comm.palette.leafShadow)            # type: ignore[attr-defined]
    if data['docType'][0][0]=='x':
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.comm.palette.leafX)         # type: ignore[attr-defined]
    else:
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.comm.palette.leafO)        # type: ignore[attr-defined]
    # header
    y = self.lineSep/2
    docTypeText= '/'.join(data['docType'])
    if data['docType'][0][0]=='x':
      docTypeText = self.comm.backend.db.dataHierarchy('x1', 'title')[0].lower()[:-1]
    maxCharacter = int(docTypeOffset/7.5)
    nameText = name if len(name)<maxCharacter else f'...{name[-maxCharacter+3:]}'
    if not data['gui'][0]:  #Only draw first line
      staticText = QStaticText(f'<strong>{nameText}</strong>')
      #TODO GUI add quick get hidden from database: add show to sqlite.getView/hierarchy then to getHierarchy an then project and then it should appear here as true/false
      staticText.setTextWidth(docTypeOffset)
      painter.drawStaticText(x0, y0+y, staticText)
      painter.drawStaticText(x0+docTypeOffset, y0+y, QStaticText(docTypeText))
      return
    # details = body
    doc     = self.comm.backend.db.getDoc(docID)
    if doc['type'][0] not in self.comm.backend.db.dataHierarchy('', ''):
      dataHierarchyNode = defaultDataHierarchyNode
    else:
      dataHierarchyNode = self.comm.backend.db.dataHierarchy(doc['type'][0], 'meta')
    if len(doc)<2:
      print(f'**ERROR cannot read docID: {docID}')
      logging.error('LeafRenderer: Cannot read docID %s',docID)
      return
    hiddenText = ('     \U0001F441' if [b for b in doc['branch'] if False in b['show']] else '')
    staticText = QStaticText(f'<strong>{nameText} {hiddenText}</strong>')
    staticText.setTextWidth(docTypeOffset)
    painter.drawStaticText(x0, y0+y, staticText)
    painter.drawStaticText(x0+docTypeOffset, y0+y, QStaticText(docTypeText))
    if self.debugMode:
      painter.drawStaticText(x0+700, y0+y, QStaticText(data['hierStack']))
    width, height = -1, -1
    for key in doc:
      if key in DO_NOT_RENDER:
        continue
      text = addDocDetails(self, None, key, doc[key], dataHierarchyNode)
      if text.startswith(CSS_STYLE):
        textDoc = QTextDocument()
        textDoc.setHtml(text)
        _, height = textDoc.size().toTuple() # type: ignore
        painter.translate(QPoint(x0-3, y0+y+15))
        textDoc.drawContents(painter)
        painter.translate(-QPoint(x0-3, y0+y+15))
        y += height
      else:
        for line in text.split('\n'):
          if line:
            y += self.lineSep
            painter.drawStaticText(x0, y0+y, QStaticText(line))
    for textType in ('comment', 'content'):
      if textType in doc and not doc[textType]:
        continue
      if textType in doc and (textType != 'content' or 'image' not in doc or doc['image'] == ''):
        textDoc = QTextDocument()
        textDoc.setMarkdown(markdownEqualizer(doc[textType]))
        if textType == 'comment':
          textDoc.setTextWidth(bottomRight2nd.toTuple()[0]-x0-widthContent-2*self.frameSize)
          width, height = textDoc.size().toTuple() # type: ignore
          painter.translate(QPoint(x0-3, y0+y+15))
          yMax = int(self.maxHeight-2*self.frameSize-y-15)
        else:
          textDoc.setTextWidth(widthContent)
          width, height = textDoc.size().toTuple() # type: ignore
          topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)           # type: ignore[attr-defined]
          painter.translate(topLeftContent)
          yMax = int(self.maxHeight-3*self.frameSize)
          y = 0
        textDoc.drawContents(painter, QRectF(0, 0, width, yMax))
        if y+height > self.maxHeight-2*self.frameSize:
          painter.setPen(self.penHighlight)
          painter.drawLine(self.frameSize, yMax+self.frameSize, width-self.frameSize, yMax+self.frameSize)
          painter.setPen(self.penDefault)
        if textType == 'comment':
          painter.translate(-QPoint(x0-3, y0+y+15))
        else:
          topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)           # type: ignore[attr-defined]
          painter.translate(-topLeftContent)
    if 'image' in doc and doc['image']!='':
      if doc['image'].startswith('data:image/'):
        pixmap = self.imageFromDoc(doc)
        width2nd = min(self.widthImage, pixmap.width()+self.frameSize)
        topLeft2nd     = option.rect.topRight()   - QPoint(width2nd+self.frameSize+1,-self.frameSize)        # type: ignore[attr-defined]
        painter.drawPixmap(topLeft2nd, pixmap)
      elif doc['image'].startswith('<?xml'):
        topLeft2nd     = option.rect.topRight()   - QPoint(self.widthImage+self.frameSize+1,-self.frameSize) # type: ignore[attr-defined]
        image = QSvgRenderer(bytearray(doc['image'], encoding='utf-8'))
        image.render(painter,    QRectF(topLeft2nd, bottomRight2nd))
    return


  def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex) -> QSize:                               # type: ignore
    """
    determine size of this leaf
    """
    if not index or not index.data(Qt.ItemDataRole.UserRole+1):
      return QSize()
    hierStack = index.data(Qt.ItemDataRole.UserRole+1)['hierStack']
    if hierStack is None or self.comm is None:
      return QSize()
    if not index.data(Qt.ItemDataRole.UserRole+1)['gui'][0]:
      return QSize(400, self.lineSep*2)
    docID   = hierStack.split('/')[-1]
    doc = self.comm.backend.db.getDoc(docID)
    if len(doc)<2:
      if len(self.comm.backend.db.getDoc(hierStack.split('/')[0]))>2: #only refresh when project still exists
        self.comm.changeProject.emit('','')
      return QSize()
    widthContent = min(self.widthContent,  \
                       int((option.rect.bottomRight()-option.rect.topLeft()).toTuple()[0]/2) )               # type: ignore[attr-defined]
    height = 0
    if doc['type'][0] not in self.comm.backend.db.dataHierarchy('', ''):
      dataHierarchyNode = defaultDataHierarchyNode
    else:
      dataHierarchyNode = self.comm.backend.db.dataHierarchy(doc['type'][0], 'meta')
    for key in doc:
      if key in DO_NOT_RENDER:
        continue
      text = addDocDetails(self, None, key, doc[key], dataHierarchyNode)
      if text.startswith(CSS_STYLE):
        textDoc = QTextDocument()
        textDoc.setHtml(text)
        _, heightDoc = textDoc.size().toTuple() # type: ignore
        height += int(heightDoc/self.lineSep)
      elif text:
        height += text.count('\n')+1
    height  = (height+3) * self.lineSep
    if 'content' in doc:
      text = QTextDocument()
      text.setMarkdown(doc['content'])
      text.setTextWidth(widthContent)
      height = max(height, text.size().toTuple()[1]) +2*self.frameSize # type: ignore
    elif 'image' in doc:
      if doc['image'].startswith('data:image/'):
        pixmap = self.imageFromDoc(doc)
        height = max(height, pixmap.height())+2*self.frameSize
      else:
        height = max(height, int(self.widthImage*3/4))+2*self.frameSize
    elif 'comment' in doc.keys() and doc['comment']:
      text = QTextDocument()
      comment = doc['comment']
      text.setMarkdown(comment.strip())
      text.setTextWidth(widthContent)
      height += text.size().toTuple()[1] # type: ignore
      height -= 25
    else:
      height -= 25
    return QSize(400, min(height, self.maxHeight))


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
