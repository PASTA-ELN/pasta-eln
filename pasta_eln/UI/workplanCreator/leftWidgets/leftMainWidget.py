from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLineEdit, QScrollArea, QSizePolicy, QVBoxLayout

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label
from pasta_eln.UI.workplanCreator.leftWidgets.procedureList import ProcedureList


class LeftMainWidget(QFrame):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm

    # Style
    self.setFrameShape(QFrame.Shape.StyledPanel)
    #self.setFrameShadow(QFrame.Shadow.Raised)

    # headerLabel
    self.headerLabel = Label("Choose Procedures", "h1")

    # searchbar
    self.searchbar = QLineEdit(clearButtonEnabled=True)

    # seperator
    self.seperator = HSeperator()

    # procedureList + scrollarea
    self.procedureList = ProcedureList(self.comm)
    scrollarea = QScrollArea(widgetResizable=True)
    scrollarea.setContentsMargins(0, 0, 0, 0)
    scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scrollarea.setWidget(self.procedureList)

    # layout
    self.layout = QVBoxLayout()
    self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    self.layout.addWidget(self.headerLabel)
    self.layout.addWidget(self.searchbar)
    self.layout.addWidget(self.seperator)
    self.layout.addWidget(scrollarea)
    self.setLayout(self.layout)
