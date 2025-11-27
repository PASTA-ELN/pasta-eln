from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import Label


class ProcedureListItem(QFrame):
  """

  """
  clicked = Signal()

  def __init__(self, comm: Communicate, procedureID: str):
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.procedureID = procedureID
    self.title = self.storage.getProcedureTitle(self.procedureID)
    self.tags = self.storage.getProcedureTags(self.procedureID)
    self.titleLabel = Label("", "h3")
    self.tagLabel = Label("", style="color:grey")

    self.clicked.connect(lambda p=procedureID: self.comm.activeProcedureChanged.emit(p, None, None))

    # titleLabel
    self.titleLabel.setText(self.title.replace("_", "_\u200B", ))
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
    self.titleLabel.setWordWrap(True)

    # tagLabel
    tagString = ""
    for tag in self.tags:
      tagString += tag + ", "
    self.tagLabel.setText(tagString[:-2])
    self.tagLabel.setWordWrap(True)
    self.tagLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    # style
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    self.setStyleSheet("border: none")
    self.setToolTip(self.titleLabel.text() + "\n" + self.tagLabel.text())

    # layout
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.titleLabel)
    self.layout.addWidget(self.tagLabel)
    self.setLayout(self.layout)

  def mousePressEvent(self, event):
    self.clicked.emit()
    super().mousePressEvent(event)
