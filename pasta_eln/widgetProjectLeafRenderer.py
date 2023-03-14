import base64
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QStaticText, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate

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
    # super().paint(painter, option, index)  #only call if want to draw default for testing
    topLeft = option.rect.topLeft().toTuple()
    docID   = index.data(Qt.DisplayRole)
    doc     = self.comm.backend.db.getDoc(docID)
    painter.drawStaticText(topLeft[0], topLeft[1], QStaticText(doc['-name']))
    if 'image' in doc and doc['image']!='' and doc['image'].startswith('data:image/'):
      pixmap = QPixmap()
      pixmap.loadFromData(base64.b64decode(doc['image'][22:]))
      pixmap = pixmap.scaledToWidth(self.width)
      painter.drawPixmap(option.rect.topRight()-QPoint(self.width,0), pixmap)
    yOffset = 0
    if '-tags' in doc and len(doc['-tags'])>0:
      yOffset += self.lineSep
      painter.drawStaticText(topLeft[0], topLeft[1]+yOffset, QStaticText('Tags: '+' '.join(doc['-tags'])))
    for key in doc:
      if key in _DO_NOT_RENDER_ or key[0] in ['-','_']:
        continue
      yOffset += self.lineSep
      if isinstance(doc[key], str):
        painter.drawStaticText(topLeft[0], topLeft[1]+yOffset, QStaticText(key+': '+doc[key]))
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
      height  = (height+1) * self.lineSep
      if 'image' in docKeys:
        height = int(self.width*3/4)
      return QSize(400, height+self.lineSep*2)

