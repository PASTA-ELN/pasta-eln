from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import Label


class WorkplanListItem(QFrame):
  clicked = Signal()

  def __init__(self, comm: Communicate, procedureID: str, sample: str, parameters: dict[str, str]):
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.procedureID = procedureID
    self.title = self.storage.getProcedureTitle(self.procedureID)
    self.titleLabel = Label(self.title.replace("_", "_\u200B"), "h3")
    self.tagLabel = Label("", style="color: grey")  # self.comm.palette.get('secondaryText', 'color')
    self.sample = sample
    self.sampleLabel = Label("Sample: " + self.sample)
    self.parameters = parameters

    self.clicked.connect(lambda: self.comm.activeProcedureChanged.emit(procedureID, sample, parameters))

    # titleLabel
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
    self.titleLabel.setWordWrap(True)

    # tagLabel
    tagString = ""
    for tag in self.storage.getProcedureTags(procedureID):
      tagString += tag + ", "
    self.tagLabel.setText(tagString[:-2])
    self.tagLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.tagLabel.setWordWrap(True)

    # sampleLabel
    self.sampleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.sampleLabel.setWordWrap(True)

    # style
    self.setFrameShape(QFrame.Shape.StyledPanel)
    self.setFrameShadow(QFrame.Shadow.Raised)
    #self.setStyleSheet("background-color: white")
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    self.setToolTip(self.titleLabel.text() + "\n" + self.tagLabel.text() + "\n" + self.sampleLabel.text())

    # layout
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.titleLabel)
    self.layout.addWidget(self.tagLabel)
    self.layout.addWidget(self.sampleLabel)
    self.setLayout(self.layout)

  def mousePressEvent(self, event):
    self.clicked.emit()
    super().mousePressEvent(event)
