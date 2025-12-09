import qdarktheme
from PySide6.QtGui import QPalette
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import Label
from pasta_eln.miscTools import makeStringWrappable


class WorkplanListItem(QFrame):
  clicked = Signal()

  def __init__(self, comm: Communicate, procedureID: str, sample: str, parameters: dict[str, str]):
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.procedureID = procedureID
    self.title = self.storage.getProcedureTitle(self.procedureID)
    self.titleLabel = Label("", "h3")
    self.tagLabel = Label("", style=f"color: {self.comm.palette.getThemeColor('foreground', 'disabled')};")  # self.comm.palette.get('secondaryText', 'color')
    self.sample = sample
    self.sampleLabel = Label("")
    self.parameters = parameters

    self.clicked.connect(lambda: self.comm.activeProcedureChanged.emit(self.procedureID, self.sample, self.parameters, self))
    self.clicked.emit()

    # titleLabel
    # add an invisible char every 25 chars for Wordwrapping
    self.titleLabel.setText(makeStringWrappable(self.title))
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setWordWrap(True)

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

    # style
    self.setFrameShape(QFrame.Shape.Panel)
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    #self.setToolTip(self.titleLabel.text() + "\n" + self.tagLabel.text() + "\n" + self.sampleLabel.text())

    # layout
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.titleLabel)
    self.layout.addWidget(self.tagLabel)
    self.layout.addWidget(self.sampleLabel)
    self.setLayout(self.layout)

  def mousePressEvent(self, event):
    self.clicked.emit()
    super().mousePressEvent(event)

  def updateParameter(self, text, parameter):
    self.parameters[parameter] = text

  def updateSample(self, text):
    self.sample = text

  def highlight(self):
    color = self.comm.palette.getThemeColor("primary", "selection.background")
    textcolor = self.comm.palette.getThemeColor("background", "base")
    self.setStyleSheet(f"""
    background-color:{color};
    color: {textcolor};""")

  def lowlight(self):
    self.setStyleSheet("")
