from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import Label


class WorkPlanListItem(QFrame):
  clicked = Signal()

  def __init__(self, comm: Communicate, title: str, tags: list[str], sample: str, parameters: dict[str, str]):
    super().__init__()
    self.comm = comm
    self.titleLabel = Label(title, "h3")
    tagString = ""
    for tag in tags:
      tagString += tag + ", "
    self.tagLabel = Label(tagString[:-2], style="color: grey")  # self.comm.palette.get('secondaryText', 'color')
    self.sample = sample
    self.sampleLabel = Label("Sample: " + self.sample)
    self.parameters = parameters

    self.clicked.connect(lambda: self.comm.activeProcedureChanged.emit(title, sample, parameters))

    # titleLabel
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.titleLabel.setWordWrap(True)

    # tagLabel
    self.tagLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    # self.tagLabel.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

    # sampleLabel
    self.sampleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    # self.sampleLabel.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

    # style
    self.setFrameShape(QFrame.Shape.StyledPanel)
    self.setFrameShadow(QFrame.Shadow.Raised)
    self.setStyleSheet("background-color: white")
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
