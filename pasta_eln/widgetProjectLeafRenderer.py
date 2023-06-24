""" renders each leaf of project tree using QPaint """
import base64, logging, re
from typing import Optional
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
    self.widthContent = 600   #TODO_P4 from config file
    self.lineSep = 20
    self.frameSize = 6
    self.maxHeight = 300
    self.penDefault:Optional[QPen] = None
    self.penHighlight              = QPen(QColor(getColor(self.comm.backend, 'primary')))
    self.penHighlight.setWidth(2)
    self.colorMargin1 = QColor(getColor(self.comm.backend, 'secondary')).darker(110)
    self.colorMargin2 = QColor(getColor(self.comm.backend, 'secondaryLight'))


  #TODO_P3 projectTree design: If folders and other items have boxes of slightly different brightness
  # (darker gray for the former and lighter for the latter), the project structure might be easier to understand. 
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
    if self.comm is None:
      return
    if self.penDefault is None:
      self.penDefault = QPen(painter.pen())
    x0, y0 = option.rect.topLeft().toTuple()
    topLeft2nd     = option.rect.topRight()   - QPoint(self.widthImage+self.frameSize+1,-self.frameSize)
    bottomRight2nd = option.rect.bottomRight()- QPoint(self.frameSize+1,self.frameSize)
    painter.fillRect(option.rect.marginsRemoved(QMargins(2,6,4,0)),  self.colorMargin1)
    painter.fillRect(option.rect.marginsRemoved(QMargins(-2,3,8,5)), self.colorMargin2)
    hierStack = index.data(Qt.DisplayRole) # type: ignore
    if hierStack is None:
      return
    docID   = hierStack.split('/')[-1]
    if docID.endswith(' -'):
      docID = docID[:-2]
      folded = True
    else:
      folded = False
    doc     = self.comm.backend.db.getDoc(docID)
    # header
    y = self.lineSep/2
    hiddenText = '     \U0001F441' if len([b for b in doc['-branch'] if False in b['show']])>0 else ''
    docTypeText= 'folder' if doc['-type'][0][0]=='x' else '/'.join(doc['-type'])
    nameText = doc['-name'] if len(doc['-name'])<55 else '...'+doc['-name'][-50:]
    painter.drawStaticText(x0, y0+y, QStaticText(nameText+hiddenText))
    painter.drawStaticText(x0+400, y0+y, QStaticText(docTypeText))
    if self.debugMode:
      painter.drawStaticText(x0+700, y0+y, QStaticText(index.data(Qt.DisplayRole)))  # type: ignore
    if folded:  #stop drawing after first line
      return
    # body
    width, height = -1, -1
    if '-tags' in doc and len(doc['-tags'])>0:
      y += self.lineSep
      tags = ['_curated_' if i=='_curated' else '#'+i for i in doc['-tags']]
      tags = ['\u2605'*int(i[2]) if i[:2]=='#_' else i for i in tags]
      painter.drawStaticText(x0, y0+y, QStaticText('Tags: '+' '.join(tags)))
    for key in doc:
      if key in _DO_NOT_RENDER_ or key[0] in ['-','_']:
        continue
      y += self.lineSep
      if isinstance(doc[key], str):
        if re.match(r'^[a-z\-]-[a-z0-9]{32}$',doc[key]) is None:  #normal text
          value = doc[key]
        elif self.comm is not None:                           #link
          table  = self.comm.backend.db.getView('viewDocType/'+key+'All')
          choices= [i for i in table if i['id']==doc[key]]
          if len(choices)==1:
            value = '\u260D '+choices[0]['value'][0]
          else:
            value = 'ERROR WITH LINK'
        painter.drawStaticText(x0, y0+y, QStaticText(key+': '+value))
      elif isinstance(doc[key], list):                         #list of qrCodes
        painter.drawStaticText(x0, y0+y, QStaticText(key+': '+', '.join(doc[key])))
    for textType in ['comment', 'content']:
      if textType in doc and (textType!='content' or not ('image' in doc and doc['image']!='')):
        textDoc = QTextDocument()
        text = doc[textType].replace('\n# ','\n### ').replace('\n## ','\n### ')
        text = '##'+text if text.startswith('# ') else text
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
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(doc['image'][22:]))
        pixmap = pixmap.scaledToWidth(self.widthImage)
        painter.drawPixmap(topLeft2nd, pixmap)
      elif doc['image'].startswith('<?xml'):
        image = QSvgRenderer(bytearray(doc['image'], encoding='utf-8'))
        image.render(painter,    QRectF(topLeft2nd, bottomRight2nd))
    return


  def sizeHint(self, option:QStyleOptionViewItem, index:QModelIndex) -> QSize:
    """
    determine size of this leaf
    """
    if index:
      hierStack = index.data(Qt.DisplayRole)  # type: ignore
      if hierStack is None:
        return QSize()
      docID   = hierStack.split('/')[-1]
      if docID.endswith(' -'):
        return QSize(400, self.lineSep*2)
      if self.comm is None:
        return QSize()
      doc = self.comm.backend.db.getDoc(docID)
      docKeys = doc.keys()
      height  = len([i for i in docKeys if not i in _DO_NOT_RENDER_ and i[0] not in ['-','_'] ])  #height in text lines
      height += 1 if '-tags' in docKeys and len(doc['-tags'])>0 else 0
      height  = (height+3) * self.lineSep
      if 'content' in docKeys:
        text = QTextDocument()
        text.setMarkdown(doc['content'])
        text.setTextWidth(self.widthContent)
        height = max(height, text.size().toTuple()[1]) +2*self.frameSize # type: ignore
      elif 'image' in docKeys:
        if doc['image'].startswith('data:image/'):
          pixmap = QPixmap()
          pixmap.loadFromData(base64.b64decode(doc['image'][22:]))
          pixmap = pixmap.scaledToWidth(self.widthImage)
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
    return QSize()

    #TODO_P3 design ProjectView: Currently, the comment is more highlighted than the title of an item due
    # to a larger and bolder font. It would make more sense though if the titles were bolder, larger and
    # thus more readable, while tags and comments are less highlighted.
    # !! Comments are not rendered perfectly: the end sucks, and I cannot blue a consistent blue line at end
    #  - rendering might not be the best option
