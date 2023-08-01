""" renders each leaf of project tree using QPaint """
import base64, logging, re
from typing import Optional, Any
from PySide6.QtCore import Qt, QSize, QPoint, QMargins, QRectF, QModelIndex# pylint: disable=no-name-in-module
from PySide6.QtGui import QStaticText, QPixmap, QTextDocument, QPainter, QColor, QPen # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem # pylint: disable=no-name-in-module
from PySide6.QtSvg import QSvgRenderer                        # pylint: disable=no-name-in-module
from .communicate import Communicate
from .style import getColor

_DO_NOT_RENDER_ = ['image','content','metaVendor','metaUser','shasum','comment']

class ProjectLeafRenderer(QStyledItemDelegate):
  """ renders each leaf of project tree using QPaint """
  def __init__(self, comm:Communicate) -> None:
    super().__init__()
    self.comm = comm
    self.debugMode = logging.root.level<logging.INFO
    self.widthImage = self.comm.backend.configuration['GUI']['imageWidthProject']
    self.widthContent = self.comm.backend.configuration['GUI']['widthContent']
    self.docTypeOffset = self.comm.backend.configuration['GUI']['docTypeOffset']
    self.frameSize = self.comm.backend.configuration['GUI']['frameSize']
    self.maxHeight = self.comm.backend.configuration['GUI']['maxProjectLeafHeight']
    self.lineSep = 20
    self.penDefault:Optional[QPen] = None
    self.penHighlight              = QPen(QColor(getColor(self.comm.backend, 'primary')))
    self.penHighlight.setWidth(2)
    self.colorMargin1 = QColor(getColor(self.comm.backend, 'secondary')).darker(110)
    self.colorMargin2 = QColor(getColor(self.comm.backend, 'secondaryLight'))


  def paint(self, painter:QPainter, option:QStyleOptionViewItem, index:QModelIndex) -> None:
    """
    Paint this item
    - coordinates: left, top
    - COS top left

    Args:
      painter (QPainter): painter
      option (QStyleOptionViewItem): option incl. current coordinates
      index (QModelIndex): index
    """
    hierStack = index.data(Qt.DisplayRole) # type: ignore
    if hierStack is None or self.comm is None:
      return
    docID   = hierStack.split('/')[-1]
    if docID.endswith(' -'):
      docID = docID[:-2]
      folded = True
    else:
      folded = False
    doc     = self.comm.backend.db.getDoc(docID)
    if len(doc)<2:
      print(f'**ERROR cannot read docID: {docID}')
      logging.error('LeafRenderer: Cannot read docID %s',docID)
      return
    # GUI
    if self.penDefault is None:
      self.penDefault = QPen(painter.pen())
    x0, y0 = option.rect.topLeft().toTuple()
    topLeft2nd     = option.rect.topRight()   - QPoint(self.widthImage+self.frameSize+1,-self.frameSize)
    bottomRight2nd = option.rect.bottomRight()- QPoint(self.frameSize+1,self.frameSize)
    painter.fillRect(option.rect.marginsRemoved(QMargins(2,6,4,0)),  self.colorMargin1)
    if doc['-type'][0][0]=='x':
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.colorMargin2.darker(102))
    else:
      painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.colorMargin2.lighter(210))
    # header
    y = self.lineSep/2
    hiddenText = ('     \U0001F441' if [b for b in doc['-branch'] if False in b['show']] else '')
    docTypeText= 'folder' if doc['-type'][0][0]=='x' else '/'.join(doc['-type'])
    nameText = doc['-name'] if len(doc['-name'])<55 else '...'+doc['-name'][-50:]
    staticText = QStaticText(f'<strong>{nameText}{hiddenText}</strong>')
    staticText.setTextWidth(self.docTypeOffset)
    painter.drawStaticText(x0, y0+y, staticText)
    painter.drawStaticText(x0+self.docTypeOffset, y0+y, QStaticText(docTypeText))
    if self.debugMode:
      painter.drawStaticText(x0+700, y0+y, QStaticText(index.data(Qt.DisplayRole)))  # type: ignore
    if folded:  #stop drawing after first line
      return
    # body
    width, height = -1, -1
    if '-tags' in doc and len(doc['-tags'])>0:
      y += self.lineSep
      tags = ['_curated_' if i=='_curated' else f'#{i}' for i in doc['-tags']]
      tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
      painter.drawStaticText(x0, y0+y, QStaticText('Tags: '+' '.join(tags)))
    for key in doc:
      if key in _DO_NOT_RENDER_ or key[0] in ['-','_']:
        continue
      y += self.lineSep
      if isinstance(doc[key], str):
        if re.match(r'^[a-z\-]-[a-z0-9]{32}$',doc[key]) is None:  #normal text
          value = doc[key]
        elif self.comm is not None:                     #link
          table = self.comm.backend.db.getView(f'viewDocType/{key}All')
          choices= [i for i in table if i['id']==doc[key]]
          if len(choices)==1:
            value = '\u260D '+choices[0]['value'][0]
          else:
            value = 'ERROR WITH LINK'
        painter.drawStaticText(x0, y0+y, QStaticText(f'{key}: {value}'))
      elif isinstance(doc[key], list):                     #list of qrCodes
        painter.drawStaticText(x0, y0+y, QStaticText(f'{key}: ' + ', '.join(doc[key])))
    for textType in ['comment', 'content']:
      if textType in doc and (textType != 'content' or 'image' not in doc or doc['image'] == ''):
        textDoc = QTextDocument()
        text = doc[textType].replace('\n# ','\n### ').replace('\n## ','\n### ')
        text = f'##{text}' if text.startswith('# ') else text
        textDoc.setMarkdown(text.strip())
        if textType == 'comment':
          textDoc.setTextWidth(bottomRight2nd.toTuple()[0]-x0-self.widthContent-2*self.frameSize)
          width, height = textDoc.size().toTuple() # type: ignore
          painter.translate(QPoint(x0-3, y0+y+15))
          yMax = int(self.maxHeight-2*self.frameSize-y-15)
        else:
          textDoc.setTextWidth(self.widthContent)
          width, height = textDoc.size().toTuple() # type: ignore
          topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)
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
          topLeftContent = option.rect.topRight() - QPoint(width+self.frameSize-2,-self.frameSize)
          painter.translate(-topLeftContent)
    if 'image' in doc and doc['image']!='':
      if doc['image'].startswith('data:image/'):
        pixmap = self.imageFromDoc(doc)
        painter.drawPixmap(topLeft2nd, pixmap)
      elif doc['image'].startswith('<?xml'):
        image = QSvgRenderer(bytearray(doc['image'], encoding='utf-8'))
        image.render(painter,    QRectF(topLeft2nd, bottomRight2nd))
    return


  def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex) -> QSize:
    # sourcery skip: de-morgan, merge-assign-and-aug-assign
    """
    determine size of this leaf
    """
    if not index:
      return QSize()
    hierStack = index.data(Qt.DisplayRole)  # type: ignore
    if hierStack is None or self.comm is None:
      return QSize()
    docID   = hierStack.split('/')[-1]
    if docID.endswith(' -'):
      return QSize(400, self.lineSep*2)
    doc = self.comm.backend.db.getDoc(docID)
    if len(doc)<2:
      self.comm.changeProject.emit('','')  #TODO_P4 redraw/reread only part of the tree
      return QSize()
    docKeys = doc.keys()
    height  = len([i for i in docKeys if not i in _DO_NOT_RENDER_ and i[0] not in ['-','_'] ])  #height in text lines
    height += 1 if '-tags' in docKeys and len(doc['-tags']) > 0 else 0
    height  = (height+3) * self.lineSep
    if 'content' in docKeys:
      text = QTextDocument()
      text.setMarkdown(doc['content'])
      text.setTextWidth(self.widthContent)
      height = max(height, text.size().toTuple()[1]) +2*self.frameSize # type: ignore
    elif 'image' in docKeys:
      if doc['image'].startswith('data:image/'):
        pixmap = self.imageFromDoc(doc)
        height = max(height, pixmap.height())+2*self.frameSize
      else:
        height = max(height, int(self.widthImage*3/4))+2*self.frameSize
    elif 'comment' in doc.keys() and len(doc['comment'])>0:
      text = QTextDocument()
      comment = doc['comment']
      text.setMarkdown(comment.strip())
      text.setTextWidth(self.widthContent)
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
    return result
