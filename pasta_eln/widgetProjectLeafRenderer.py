import base64
from PySide6.QtCore import Qt, QSize, QPoint, QMargins, QRectF
from PySide6.QtGui import QStaticText, QPixmap, QBrush
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtSvg import QSvgRenderer

_DO_NOT_RENDER_ = ['image','content','metaVendor','metaUser','shasum']

class ProjectLeafRenderer(QStyledItemDelegate):
  def setCommunication(self, comm):
    """
    Set communication path

    Args:
      comm (Communicate): communication path
    """
    self.comm = comm
    self.lineSep = 20
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
    topLeft2nd = option.rect.topRight()-QPoint(self.width,0)
    docID   = index.data(Qt.DisplayRole)
    doc     = self.comm.backend.db.getDoc(docID)
    painter.fillRect(option.rect.marginsRemoved(QMargins(0,2,0,2)), Qt.lightGray)
    if 'image' in doc and doc['image']!='':
      if doc['image'].startswith('data:image/'):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(doc['image'][22:]))
        pixmap = pixmap.scaledToWidth(self.width)
        painter.drawPixmap(topLeft2nd, pixmap)
      elif doc['image'].startswith('<?xml'):
        image = QSvgRenderer(bytearray(doc['image'], encoding='utf-8'))
        image.render(painter, QRectF(topLeft2nd, option.rect.bottomRight()))
    elif 'content' in doc:
      print('Implement content')
    yOffset += self.lineSep/2
    painter.drawStaticText(xOffset, yOffset, QStaticText(doc['-name']))
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
        print("cannot paint ",docID, key)


  def sizeHint(self, option, index):
    """
    determine size of this leaf
    """
    if index:
      docID   = index.data(Qt.DisplayRole)
      docKeys = self.comm.backend.db.getDoc(docID).keys()
      height  = len([i for i in docKeys if not i in _DO_NOT_RENDER_ and i[0] not in ['-','_'] ])  #height in text lines
      height  = (height+3) * self.lineSep
      if 'image' in docKeys:
        height = int(self.width*3/4)
      return QSize(400, height)

