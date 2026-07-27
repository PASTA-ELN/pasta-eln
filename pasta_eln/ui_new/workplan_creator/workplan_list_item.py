"""Item inside the list of the rightMainWidget."""
from typing import Protocol
import qtawesome
from PySide6.QtCore import QMimeData, QPoint, Qt, Signal
from PySide6.QtGui import QDrag, QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, QDropEvent, QMouseEvent, QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout
from pasta_eln.misc_tools import makeStringWrappable
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Label


class WorkplanContainer(Protocol):
  """Operations a list item needs from its containing workplan widget."""

  def addProcedure(self, procedureID: str, sample: str, parameters: dict[str, str], at: int | None = None) -> None:
    """Add a procedure to the workplan at an optional position."""


class WorkplanListItem(QFrame):
  """
  Item inside the list of the rightMainWidget.
  """
  clicked = Signal()
  dragStartPos = QPoint()

  def __init__(self, comm: Communicate, procedureID: str, sample: str, parameters: dict[str, str],
               rightMainWidget: WorkplanContainer) -> None:
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.rightMainWidget = rightMainWidget
    self.procedureID = procedureID
    self.title = self.storage.getProcedureTitle(self.procedureID)
    self.sample = sample
    self.parameters = parameters
    # Widgets
    self.titleLabel = Label('', 'h3')
    self.deleteButton = QPushButton('')
    self.header = QHBoxLayout()
    self.tagLabel = Label('')
    self.sampleLabel = Label('')
    self.frame = QFrame()

    self.clicked.connect(
      lambda: self.comm.activeProcedureChanged.emit(self.procedureID, self.sample, self.parameters, self))
    self.clicked.emit()
    self.setAcceptDrops(True)

    # deleteButton
    self.deleteButton.setIcon(qtawesome.icon('ei.remove'))
    self.deleteButton.setFixedSize(16, 16)
    self.deleteButton.setContentsMargins(0, 0, 0, 0)
    self.deleteButton.clicked.connect(self._onDeleteClicked)
    self.deleteButton.setStyleSheet('border:none;')

    # titleLabel
    # add an invisible char every 25 chars for Wordwrapping
    self.titleLabel.setText(makeStringWrappable(self.title))
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setWordWrap(True)
    self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    # header
    self.header.setContentsMargins(0, 0, 0, 0)
    self.header.addWidget(self.titleLabel)
    self.header.addWidget(self.deleteButton, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

    # tagLabel
    tagString = ''
    for tag in self.storage.getProcedureTags(procedureID):
      # add an invisible char every 25 chars for Wordwrapping
      tag = makeStringWrappable(tag)
      tagString += tag + ', '
    self.tagLabel.setText(tagString[:-2])
    self.tagLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.tagLabel.setWordWrap(True)

    # sampleLabel
    # add an invisible char every 25 chars for Wordwrapping
    self.sampleLabel.setText('Sample: ' + makeStringWrappable(self.sample))
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
    icon = qtawesome.icon('ph.arrow-down').pixmap(30, 30)
    self.arrow = QLabel(pixmap=icon)

    # style
    self.defaultCSS = f"""
        WorkplanListItem{{
          border-color: transparent;
          border-width: 2px;
        }}
        QFrame[highlight="true"] {{
          background-color:{self.comm.palette.getThemeColor("primary", "base")};
        }}
        QFrame[highlight="true"] QLabel{{
          color: {self.comm.palette.getThemeColor("background", "base")};
        }}"""
    self.setStyleSheet(self.defaultCSS)

    # layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.addWidget(self.frame)
    self.mainLayout.addWidget(self.arrow, alignment=Qt.AlignmentFlag.AlignHCenter)
    self.mainLayout.setSpacing(0)
    self.mainLayout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(self.mainLayout)

  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Override Event to simulate click and Position of potential drag start.
    """
    if event.button() == Qt.MouseButton.LeftButton:
      self.dragStartPos = event.pos()
      self.clicked.emit()
    super().mousePressEvent(event)

  def updateParameter(self, text: str, parameter: str) -> None:
    """
    Setter of the value (text) for the given parameter
    """
    self.parameters[parameter] = text

  def updateSample(self, text: str) -> None:
    """
    Setter for the Sample. updates sampleLabel, too.
    """
    self.sample = text
    self.sampleLabel.setText('Sample: ' + makeStringWrappable(self.sample))

  def highlight(self) -> None:
    """
    Updates the Style of this Item to highlight it
    """
    self.frame.setProperty('highlight', True)
    self.setStyleSheet(self.defaultCSS)

  def lowlight(self) -> None:
    """
    Updates the Style of this Item to reset the highlight
    """
    self.frame.setProperty('highlight', False)
    self.setStyleSheet(self.defaultCSS)

  def _onDeleteClicked(self) -> None:
    """
    Deletes this widget.
    """
    self.hide()
    self.deleteLater()

  def mouseMoveEvent(self, event: QMouseEvent) -> None:
    """
    Override event to implement drag and drop
    """
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

  def dragEnterEvent(self, event: QDragEnterEvent) -> None:
    """
    Override event to accept drops
    """
    event.acceptProposedAction()

  def dragMoveEvent(self, event: QDragMoveEvent) -> None:
    """
    Override event to visualize drag and drop indicators
    """
    midheight = self.height() // 2
    if event.position().y() < midheight:
      self.setStyleSheet(self.defaultCSS + f"""
        WorkplanListItem{{
        border-top-color: {self.comm.palette.getThemeColor("primary", "base")};}}""")
    else:
      self.setStyleSheet(self.defaultCSS + f"""
        WorkplanListItem{{
        border-bottom-color: {self.comm.palette.getThemeColor("primary", "base")};}}""")

  def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
    """
    Override event to remove drag and drop indicators
    """
    self.setStyleSheet(self.defaultCSS)

  def dropEvent(self, event: QDropEvent) -> None:
    """
    Override event to implement drag and drop
    """
    droppedItem = event.source()
    if not isinstance(droppedItem, WorkplanListItem):
      return
    self.setStyleSheet('')
    parentWidget = self.parentWidget()
    parentLayout = parentWidget.layout() if parentWidget is not None else None
    if parentLayout is None:
      event.ignore()
      return
    selfidx = parentLayout.indexOf(self)
    midheight = self.height() // 2
    if event.position().y() < midheight:
      self.rightMainWidget.addProcedure(droppedItem.procedureID, droppedItem.sample, droppedItem.parameters, selfidx)
    else:
      self.rightMainWidget.addProcedure(droppedItem.procedureID, droppedItem.sample, droppedItem.parameters,
                                        selfidx + 1)
    droppedItem._onDeleteClicked()                                          # pylint: disable=protected-access
    event.acceptProposedAction()
