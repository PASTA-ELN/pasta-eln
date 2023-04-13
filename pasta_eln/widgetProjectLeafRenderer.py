""" renders each leaf of project tree using QPaint """
import base64, logging
from PySide6.QtCore import Qt, QSize, QPoint, QMargins, QRectF# pylint: disable=no-name-in-module
from PySide6.QtGui import QStaticText, QPixmap, QTextDocument, QColor # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QStyledItemDelegate             # pylint: disable=no-name-in-module
from PySide6.QtSvg import QSvgRenderer
from pasta_eln.style import getColor                        # pylint: disable=no-name-in-module

_DO_NOT_RENDER_ = ['image','content','metaVendor','metaUser','shasum','comment']

class ProjectLeafRenderer(QStyledItemDelegate):
  """ renders each leaf of project tree using QPaint """
  def __init__(self):
    super().__init__()
    self.lineSep = 20 #TODO_P5 addToConfig
    self.debugMode = True
    self.comm = None
    self.width = -1


  def setCommunication(self, comm):
    """
    Set communication path

    Args:
      comm (Communicate): communication path
    """
    self.comm = comm
    self.width = self.comm.backend.configuration['GUI']['imageWidthProject']
    return


  def paint(self, painter, option, index):
    """
    Paint this item
    - coordinates: left, top
    - COS top left

    Args:
      painter (QPainter): painter
      option (QStyleOptionViewItem): option incl. current coordinates
      index (QModelIndex): index
    """
    xOffset, yOffset = option.rect.topLeft().toTuple()
    topLeft2nd = option.rect.topRight()-QPoint(self.width,-2)
    docID   = index.data(Qt.DisplayRole).split('/')[-1]
    if docID.endswith(' -'):
      docID = docID[:-2]
      folded = True
    else:
      folded = False
    doc     = self.comm.backend.db.getDoc(docID)
    painter.fillRect(option.rect.marginsRemoved(QMargins(2,6,4,0)),QColor.fromString(getColor(self.comm.backend, 'secondary')).darker(150))
    painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), QColor.fromString(getColor(self.comm.backend, 'secondaryLight')))
    if 'image' in doc and doc['image']!='' and not folded:
      if doc['image'].startswith('data:image/'):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(doc['image'][22:]))
        pixmap = pixmap.scaledToWidth(self.width-8)
        painter.drawPixmap(topLeft2nd, pixmap)
      elif doc['image'].startswith('<?xml'):
        image = QSvgRenderer(bytearray(doc['image'], encoding='utf-8'))
        image.render(painter,    QRectF(topLeft2nd, option.rect.bottomRight()))
    elif 'content' in doc and not folded:
      text = QTextDocument()
      text.setMarkdown(doc['content'])
      painter.translate(topLeft2nd)
      text.drawContents(painter)
      painter.translate(-topLeft2nd)
    yOffset += self.lineSep/2
    hiddenText = '     \U0001F441' if len([b for b in doc['-branch'] if False in b['show']])>0 else ''
    painter.drawStaticText(xOffset, yOffset, QStaticText(doc['-name']+hiddenText))
    if self.debugMode:
      painter.drawStaticText(xOffset+500, yOffset, QStaticText(index.data(Qt.DisplayRole))) #doc['_id']
    if '-tags' in doc and len(doc['-tags'])>0:
      yOffset += self.lineSep
      tags = ['cur\u2605ted' if i=='_curated' else '#'+i for i in doc['-tags']]
      tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
      painter.drawStaticText(xOffset, yOffset, QStaticText('Tags: '+' '.join(tags)))
    for key in doc:
      if key in _DO_NOT_RENDER_ or key[0] in ['-','_']:
        continue
      yOffset += self.lineSep
      if isinstance(doc[key], str):
        painter.drawStaticText(xOffset, yOffset, QStaticText(key+': '+doc[key]))
      else:
        logging.info('Do not know how to paint: '+docID+': '+str(key))
    if 'comment' in doc and not folded:
      text = QTextDocument()
      text.setMarkdown(doc['comment'].strip())
      painter.translate(QPoint(xOffset-3, yOffset+15))
      text.drawContents(painter)
      painter.translate(-QPoint(xOffset-3, yOffset+15))
    return


  def sizeHint(self, option, index):
    """
    determine size of this leaf
    """
    if index:
      docID   = index.data(Qt.DisplayRole).split('/')[-1]
      if docID.endswith(' -'):
        docID = docID[:-2]
        folded = True
      else:
        folded = False
      doc = self.comm.backend.db.getDoc(docID)
      docKeys = doc.keys()
      height  = len([i for i in docKeys if not i in _DO_NOT_RENDER_ and i[0] not in ['-','_'] ])  #height in text lines
      height  = (height+3) * self.lineSep
      if 'comment' in doc.keys() and not folded:
        text = QTextDocument()
        text.setMarkdown(self.comm.backend.db.getDoc(docID)['comment'].strip())
        cutOff = 30 if text.size().toTuple()[1]>30 else 10
        height += text.size().toTuple()[1]-cutOff
      if 'image' in docKeys and not folded:
        if doc['image'].startswith('data:image/'):
          try:
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(doc['image'][22:]))
            pixmap = pixmap.scaledToWidth(self.width)
            height = pixmap.height()
          except:
            print("**Exception in Renderer.sizeHint") #TODO_P5 if successful in Aug2023: remove
        else:
          height = int(self.width*3/4)
      if 'content' in docKeys and not folded:
        text = QTextDocument()
        text.setMarkdown(self.comm.backend.db.getDoc(docID)['content'])
        height = text.size().toTuple()[1]
      return QSize(400, height)
    return QSize()
