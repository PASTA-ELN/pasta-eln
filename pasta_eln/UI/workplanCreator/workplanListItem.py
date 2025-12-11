import qdarktheme
import qtawesome
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QMimeData, QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import Label
from pasta_eln.miscTools import makeStringWrappable


class WorkplanListItem(QFrame):
  clicked = Signal()
  dragStartPos = QPoint()

  def __init__(self, comm: Communicate, procedureID: str, sample: str, parameters: dict[str, str], rightMainWidget):
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.rightMainWidget = rightMainWidget
    self.procedureID = procedureID
    self.title = self.storage.getProcedureTitle(self.procedureID)
    self.sample = sample
    self.parameters = parameters
    # Widgets
    self.titleLabel = Label("", "h3")
    self.deleteButton = QPushButton("")
    self.header = QHBoxLayout()
    self.tagLabel = Label("", style=f"color: {self.comm.palette.getThemeColor('foreground', 'disabled')};")  # self.comm.palette.get('secondaryText', 'color')
    self.sampleLabel = Label("")
    self.frame = QFrame()

    self.clicked.connect(lambda: self.comm.activeProcedureChanged.emit(self.procedureID, self.sample, self.parameters, self))
    self.clicked.emit()
    self.setAcceptDrops(True)

    # deleteButton
    self.deleteButton.setIcon(qtawesome.icon("ei.remove"))
    #self.deleteButton.setIconSize(QSize(10, 10))
    self.deleteButton.setFixedSize(16, 16)
    self.deleteButton.setContentsMargins(0,0,0,0)
    self.deleteButton.clicked.connect(self._onDeleteClicked)
    self.deleteButton.setStyleSheet("border:none;")

    # titleLabel
    # add an invisible char every 25 chars for Wordwrapping
    self.titleLabel.setText(makeStringWrappable(self.title))
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setWordWrap(True)
    self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    # header
    self.header.setContentsMargins(0,0,0,0)
    self.header.addWidget(self.titleLabel)
    self.header.addWidget(self.deleteButton, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

    # tagLabel
    tagString = ""
    for tag in self.storage.getProcedureTags(procedureID):
      # add an invisible char every 25 chars for Wordwrapping
      tag = makeStringWrappable(tag)
      tagString += tag + ", "
    self.tagLabel.setText(tagString[:-2])
    self.tagLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.tagLabel.setWordWrap(True)

    # sampleLabel
    # add an invisible char every 25 chars for Wordwrapping
    self.sampleLabel.setText("Sample: " + makeStringWrappable(self.sample))
    self.sampleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.sampleLabel.setWordWrap(True)

    # framelayout
    self.frameLayout = QVBoxLayout()
    self.frameLayout.addLayout(self.header)
    self.frameLayout.addWidget(self.tagLabel)
    self.frameLayout.addWidget(self.sampleLabel)

    # frame
    self.frame.setFrameShape(QFrame.Shape.Panel)
    self.frame.setCursor(Qt.CursorShape.PointingHandCursor)
    self.frame.setLayout(self.frameLayout)

    # arrow
    icon = qtawesome.icon("ph.arrow-down").pixmap(30, 30)
    self.arrow = QLabel(pixmap=icon)

    # style
    self.defaultCSS = f"""
        WorkplanListItem{{
          border-color: transparent;
          border-width: 2px;
        }}
        QFrame[highlight="true"] {{
          background-color:{self.comm.palette.getThemeColor("primary", "selection.background")};
        }}
        QFrame[highlight="true"] QLabel{{
          color: {self.comm.palette.getThemeColor("background", "base")};
        }}"""
    self.setStyleSheet(self.defaultCSS)


    # layout
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.frame)
    self.layout.addWidget(self.arrow, alignment=Qt.AlignmentFlag.AlignHCenter)
    self.layout.setSpacing(0)
    self.layout.setContentsMargins(0,0,0,0)
    self.setLayout(self.layout)

  def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
      self.dragStartPos = event.pos()
      self.clicked.emit()
    super().mousePressEvent(event)

  def updateParameter(self, text, parameter):
    self.parameters[parameter] = text

  def updateSample(self, text):
    self.sample = text
    self.sampleLabel.setText("Sample: " + makeStringWrappable(self.sample))

  def highlight(self):
    self.frame.setProperty("highlight", True)
    self.setStyleSheet(self.defaultCSS)

  def lowlight(self):
    self.frame.setProperty("highlight", False)
    self.setStyleSheet(self.defaultCSS)

  def _onDeleteClicked(self):
    self.deleteLater()

  def mouseMoveEvent(self, event):
    if not event.buttons() == Qt.MouseButton.LeftButton:
      return
    if (event.pos() - self.dragStartPos).manhattanLength() < QApplication.startDragDistance():
      return
    pixmap = QPixmap(self.frame.size())
    self.frame.render(pixmap)
    drag = QDrag(self)
    mimeData = QMimeData()

    drag.setMimeData(mimeData)
    drag.setPixmap(pixmap)
    drag.setHotSpot(event.pos())
    drag.exec(Qt.DropAction.MoveAction)

  def dragEnterEvent(self, event):
    event.acceptProposedAction()

  def dragMoveEvent(self, event):
    midheight = self.height() // 2
    if event.position().y() < midheight:
      self.setStyleSheet(self.defaultCSS + f"""
        WorkplanListItem{{
        border-top-color: {self.comm.palette.getThemeColor("primary", "base")};}}""")
    else:
      self.setStyleSheet(self.defaultCSS + f"""
        WorkplanListItem{{
        border-bottom-color: {self.comm.palette.getThemeColor("primary", "base")};}}""")

  def dragLeaveEvent(self, event):
    self.setStyleSheet(self.defaultCSS)

  def dropEvent(self, event):
    if isinstance(event.source(), WorkplanListItem):
      droppedItem: WorkplanListItem = event.source()
    else:
      return
    self.setStyleSheet("")
    parentLayout = self.parentWidget().layout()
    selfidx = parentLayout.indexOf(self)
    midheight = self.height() // 2
    if event.position().y() < midheight:
      self.rightMainWidget.addProcedure(droppedItem.procedureID, droppedItem.sample, droppedItem.parameters, selfidx)
    else:
      self.rightMainWidget.addProcedure(droppedItem.procedureID, droppedItem.sample, droppedItem.parameters, selfidx+1)
    droppedItem._onDeleteClicked()
    event.acceptProposedAction()
