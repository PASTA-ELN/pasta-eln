""" renders each leaf of project tree using QPaint """
import base64
import logging
from typing import Any
from PySide6.QtCore import (QAbstractItemModel, QEvent, QMargins, QModelIndex, QPersistentModelIndex, QPoint, QRect,
                            QRectF, QSize, Qt, Signal, Slot)
from PySide6.QtGui import QMouseEvent, QPainter, QPen, QPixmap, QStaticText, QTextDocument
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QAbstractItemView, QStyle, QStyledItemDelegate, QStyleOptionViewItem
from ...fixed_strings_json import DO_NOT_RENDER, defaultDataHierarchyNode
from ...text_tools.handle_dictionaries import doc2markdown
from ...text_tools.string_changes import markdownEqualizer
from ..gui_communicate import Communicate

FRAME_SIZE = 6
MIN_CONTENT_WIDTH = 240
MENU_BUTTON_SIZE = 24
MENU_BUTTON_MARGIN = 12

def layoutWidths(availableWidth:int) -> tuple[int, int, int]:
  """Return adaptive content, image, and document-type widths
  Args:
    availableWidth (int): total size of leaf / item
  Returns:
    (int, int, int): width of content and image, as well as offset of docType behind name
  """
  #                   MIN                    MAX
  widthContent  = max(MIN_CONTENT_WIDTH, min(600, availableWidth // 2))
  widthImage    = max(180,               min(400, availableWidth // 4))
  docTypeOffset = max(250,               min(500, availableWidth // 3))
  return widthContent, widthImage, docTypeOffset


class ProjectLeafRenderer(QStyledItemDelegate):
  """ ONE Renderer for all leafs of project tree using QPaint """
  contextMenuRequested = Signal(QModelIndex, QPoint)

  def __init__(self, parent:QAbstractItemView, comm:Communicate) -> None:
    """ Initialize the ProjectLeafRenderer

    Args:
      parent (QAbstractItemView): parent widget
      comm (Communication): communication layer
    """
    super().__init__(parent)
    self.comm               = comm
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetDoc)
    self.debugMode          = logging.root.level<logging.INFO
    self.maxHeight          = self.comm.configuration['GUI']['projectItemHeight']
    self.lineSep            = 20
    self.penDefault         = QPen(self.comm.palette.text)
    self.penHighlight       = QPen(self.comm.palette.primary)
    self.penHighlight.setWidth(2)
    self.leafWidth          = -1
    self.docs:dict[str,Any] = {}   # docID: {'size':QSize, 'markdown':str, 'hidden':bool, 'index':QModelIndex}


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
    data = index.data(Qt.ItemDataRole.UserRole+1)
    if not data or data['hierStack'] is None or self.comm is None:
      return
    docID   = data['hierStack'].split('/')[-1]
    name = self.docs.get(docID, {}).get('name','') or index.data(Qt.ItemDataRole.DisplayRole)
    docType = self.docs.get(docID, {}).get('type',[]) or data['docType']
    painter.setPen(self.penDefault)
    x0, y0 = option.rect.topLeft().toTuple()
    widthContent, widthImage, docTypeOffset = layoutWidths(option.rect.width())
    bottomRight2nd = option.rect.bottomRight()- QPoint(FRAME_SIZE+1,FRAME_SIZE)
    painter.fillRect(option.rect.marginsRemoved(QMargins(2,6,4,0)),  self.comm.palette.leafShadow)
    if docType[0][0]=='x':
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.comm.palette.leafX)
    else:
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.comm.palette.leafO)
    # header
    y = self.lineSep//2
    docTypeText= '/'.join(docType)
    if docType[0][0]=='x':
      docTypeText = self.comm.docTypesTitles['x1']['title'].lower()[:-1]
    maxCharacter = int(docTypeOffset/7.5)
    nameText = name if len(name)<maxCharacter else f'...{name[-maxCharacter+3:]}'
    if not data['gui'][0]:                                                               #Only draw first line
      staticText = QStaticText(f'<strong>{nameText} (...)</strong>')
      staticText.setTextWidth(docTypeOffset)
      painter.drawStaticText(x0, y0+y, staticText)
      painter.drawStaticText(x0+docTypeOffset, y0+y, QStaticText(docTypeText))
      self.paintMenuButton(painter, option)
      return
    hiddenText = '     \U0001F441' if self.docs.get(docID, {}).get('hidden', False) else ''
    staticText = QStaticText(f'<strong>{nameText} {hiddenText}</strong>')
    staticText.setTextWidth(docTypeOffset)
    secondaryText = docTypeText
    secondaryText += f" | {data['hierStack']}" if self.debugMode and len(data['hierStack'])<72 else \
                     f" | ...{data['hierStack'][-76:]}" if self.debugMode else ''
    painter.drawStaticText(x0, y0+y, staticText)
    painter.drawStaticText(x0+docTypeOffset, y0+y, QStaticText(secondaryText))
    textDoc = QTextDocument()
    textDoc.setMarkdown(self.docs.get(docID, {}).get('markdown',''))
    painter.translate(QPoint(x0-3, y0+y+15))
    self.drawTextDocument(painter, textDoc, int(self.maxHeight-6*FRAME_SIZE))
    painter.translate(-QPoint(x0-3, y0+y+15))
    # right side
    if self.docs.get(docID, {}).get('content','') and not self.docs.get(docID, {}).get('image',''):
      textDoc = QTextDocument()
      textDoc.setMarkdown(self.docs.get(docID, {}).get('content',''))
      textDoc.setTextWidth(widthContent)
      width = int(textDoc.size().toTuple()[0])
      topLeftContent = option.rect.topRight() - QPoint(width+FRAME_SIZE-2,-FRAME_SIZE)
      painter.translate(topLeftContent)
      self.drawTextDocument(painter, textDoc, int(self.maxHeight-3*FRAME_SIZE))
      topLeftContent = option.rect.topRight() - QPoint(width+FRAME_SIZE-2,-FRAME_SIZE)
      painter.translate(-topLeftContent)
    if self.docs.get(docID, {}).get('image',''):
      if self.docs.get(docID, {}).get('image','').startswith('data:image/'):
        pixmap = self.imageFromDoc({'image':self.docs.get(docID, {}).get('image','')})
        width2nd = min(widthImage, pixmap.width()+FRAME_SIZE)
        topLeft2nd     = option.rect.topRight()   - QPoint(width2nd+FRAME_SIZE+1,-FRAME_SIZE)
        painter.drawPixmap(topLeft2nd, pixmap)
      elif self.docs.get(docID, {}).get('image','').startswith('<?xml'):
        topLeft2nd     = option.rect.topRight()   - QPoint(widthImage+FRAME_SIZE+1,-FRAME_SIZE)
        image = QSvgRenderer(bytearray(self.docs.get(docID, {}).get('image',''), encoding='utf-8'))
        image.render(painter,    QRectF(topLeft2nd, bottomRight2nd))
    self.paintMenuButton(painter, option)
    return

  def paintMenuButton(self, painter:QPainter, option:QStyleOptionViewItem) -> None:
    """Paint a compact overflow button that exposes the item's context menu.

    Args:
      painter (QPainter): painter
      option (QStyleOptionViewItem): option
    """
    if not option.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver):
      return
    buttonRect = QRect(option.rect.right() - MENU_BUTTON_SIZE - MENU_BUTTON_MARGIN,
                       option.rect.top() + MENU_BUTTON_MARGIN,
                       MENU_BUTTON_SIZE, MENU_BUTTON_SIZE)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(option.palette.base())
    painter.drawRoundedRect(buttonRect, 4, 4)
    painter.setPen(self.comm.palette.primary)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawText(buttonRect, Qt.AlignmentFlag.AlignCenter, '\N{VERTICAL ELLIPSIS}')
    painter.restore()


  def editorEvent(self, event:QEvent, model:QAbstractItemModel, option:QStyleOptionViewItem,
                  index:QModelIndex | QPersistentModelIndex) -> bool:
    """Open the item's context menu when its overflow button is clicked.

    Args:
      event (QEvent): event
      model (QAbstractItemModel): model
      option (QStyleOptionViewItem): option
      index (QModelIndex): index

    Returns:
      bool: True if the event was handled, False otherwise
    """
    if (event.type() != QEvent.Type.MouseButtonRelease or not isinstance(event, QMouseEvent)
        or event.button() != Qt.MouseButton.LeftButton):
      return super().editorEvent(event, model, option, index)
    if option.widget is None:
      return False
    buttonRect = QRect(option.rect.right() - MENU_BUTTON_SIZE - MENU_BUTTON_MARGIN,
                       option.rect.top() + MENU_BUTTON_MARGIN,
                       MENU_BUTTON_SIZE, MENU_BUTTON_SIZE)
    if not buttonRect.contains(event.position().toPoint()):
      return super().editorEvent(event, model, option, index)
    self.contextMenuRequested.emit(index, option.widget.mapToGlobal(event.position().toPoint()))
    return True


  def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex | QPersistentModelIndex) -> QSize:
    """ Determine size of this leaf

    Args:
      option (QStyleOptionViewItem): option
      index (QModelIndex | QPersistentModelIndex): index

    Returns:
      QSize: size of this leaf
    """
    if not index or not index.data(Qt.ItemDataRole.UserRole+1):
      return QSize()
    hierStack = index.data(Qt.ItemDataRole.UserRole+1)['hierStack']
    if hierStack is None or self.comm is None:
      return QSize()
    if not index.data(Qt.ItemDataRole.UserRole+1)['gui'][0]:              # only show the headline, no details
      return QSize(400, self.lineSep*2)
    docID   = hierStack.split('/')[-1]
    if docID not in self.docs:
      self.leafWidth = layoutWidths(option.rect.width())[0]
      self.docs[docID] = {'size':QSize(400, 30), 'markdown':'', 'hidden':False, 'index':index}
      self.comm.uiRequestDoc.emit(docID)
    return self.docs[docID].get('size', QSize(400,self.maxHeight))


  @Slot(str)
  def onGetDoc(self, doc:dict[str,Any]) -> None:
    """ Slot to handle the document received from backend
    Args:
      doc (dict): document
    """
    guiStyle = self.comm.configuration['GUI']
    if not doc or doc['id'] not in self.docs:
      return
    logging.debug('Renderer: onGetDoc %s %s %s', doc['id'], doc.get('type',[]), doc.get('hierStack',''))
    # ... after deleting project, its items cannot be found and it would give many false negatives
    if doc['type'][0] not in self.comm.docTypesTitles:
      dataHierarchyNode = defaultDataHierarchyNode
    else:
      dataHierarchyNode = self.comm.dataHierarchyNodes[doc['type'][0]]
    textDoc = QTextDocument()
    markdownStr = doc2markdown(doc, DO_NOT_RENDER, dataHierarchyNode, self)
    textDoc.setMarkdown(markdownStr)
    textDoc.setTextWidth(self.leafWidth)
    _, widthImage, _ = layoutWidths(max(self.leafWidth * 2, MIN_CONTENT_WIDTH * 2))
    heightDetails = int(textDoc.size().toTuple()[1])+FRAME_SIZE+20
    heightRightSide = -1
    if 'content' in doc:
      textDoc.setMarkdown(doc['content'])
      heightRightSide = int(textDoc.size().toTuple()[1])
    elif 'image' in doc and doc['image']:
      if doc['image'].startswith('data:image/'):
        pixmap = self.imageFromDoc(doc)
        heightRightSide = pixmap.height()+2*FRAME_SIZE
      else:
        heightRightSide = int(widthImage*3/4+2*FRAME_SIZE)
    self.docs[doc['id']]['size']    = QSize(400, min(max(heightDetails,heightRightSide), guiStyle['projectItemHeight']))
    self.docs[doc['id']]['hidden']  = any(b for b in doc['branch'] if False in b['show'])
    self.docs[doc['id']]['markdown']= markdownStr
    self.docs[doc['id']]['name']    = doc['name']
    self.docs[doc['id']]['type'] = doc['type']
    self.docs[doc['id']]['content'] = markdownEqualizer(doc['content']) if 'content' in doc else ''
    self.docs[doc['id']]['image']   = doc.get('image','')
    self.sizeHintChanged.emit(self.docs[doc['id']]['index'])


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
    if height > yMax+FRAME_SIZE:
      painter.setPen(self.penHighlight)
      painter.drawLine(FRAME_SIZE, yMax+FRAME_SIZE, width-FRAME_SIZE, yMax+FRAME_SIZE)
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
    result = result.scaledToWidth(layoutWidths(max(self.leafWidth * 2, MIN_CONTENT_WIDTH * 2))[1])
    if result.height()>self.maxHeight:
      result = result.scaledToHeight(self.maxHeight-FRAME_SIZE*2)
    return result
