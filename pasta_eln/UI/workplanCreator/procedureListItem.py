from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import Label
from pasta_eln.UI.workplanCreator.workplanFunctions import getProcedureTags


class ProcedureListItem(QFrame):
  """

  """
  clicked = Signal()

  def __init__(self, comm: Communicate, procedure: str):
    super().__init__()
    self.comm = comm
    self.titleLabel = Label(procedure.replace("_", "_\u200B"), "h3")
    self.tagLabel = Label("", style="color:grey")

    self.clicked.connect(lambda p=procedure: self.comm.activeProcedureChanged.emit(p, None, None))

    # titleLabel
    # self.titleLabel.setWordWrap(True)
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
    self.titleLabel.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    # self.titleLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    # tagLabel
    tags = getProcedureTags(procedure, self.comm)
    tagString = ""
    for tag in tags:
      tagString += tag + ", "
    self.tagLabel.setText(tagString[:-2])
    # self.tagLabel.setWordWrap(True)
    self.tagLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.tagLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
    self.tagLabel.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    # style
    # self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    self.setStyleSheet("border: none")
    self.setToolTip(self.titleLabel.text() + "\n" + self.tagLabel.text())

    # layout
    self.layout = QVBoxLayout()
    # self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.setSpacing(0)
    self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    self.layout.addWidget(self.titleLabel)
    self.layout.addWidget(self.tagLabel)
    self.setLayout(self.layout)

  def mousePressEvent(self, event):
    self.clicked.emit()
    super().mousePressEvent(event)
