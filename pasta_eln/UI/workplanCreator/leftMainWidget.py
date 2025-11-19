from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLineEdit, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label
from pasta_eln.UI.workplanCreator.procedureListItem import ProcedureListItem
from pasta_eln.UI.workplanCreator.workplanFunctions import getDBProcedures, getProcedureTitle


class LeftMainWidget(QFrame):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.procedures = []

    # Style
    self.setFrameShape(QFrame.Shape.StyledPanel)
    self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    # self.setFrameShadow(QFrame.Shadow.Raised)

    # headerLabel
    self.headerLabel = Label("Choose Procedures", "h1")

    # searchbar
    self.searchbar = QLineEdit(clearButtonEnabled=True)

    # seperator
    self.seperator = HSeperator()

    # procedureList
    self.procedureList = QWidget()
    self.comm.storageUpdated.connect(self.updateProcedures)
    self.procedureListLayout = QVBoxLayout()
    self.procedureListLayout.setContentsMargins(0, 0, 0, 0)
    self.procedureListLayout.setSpacing(0)
    self.procedureList.setLayout(self.procedureListLayout)

    # scrollarea
    scrollarea = QScrollArea(widgetResizable=True)
    scrollarea.setContentsMargins(0, 0, 0, 0)
    scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scrollarea.setWidget(self.procedureList)

    # layout
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.headerLabel)
    self.layout.addWidget(self.searchbar)
    self.layout.addWidget(self.seperator)
    self.layout.addWidget(scrollarea)
    self.setLayout(self.layout)

  def updateProcedures(self):
    """

    """
    self.procedures = getDBProcedures(self.comm)
    # Layout leeren
    while self.procedureListLayout.count():
      item = self.procedureListLayout.takeAt(0)
      widget = item.widget()
      if widget:
        widget.deleteLater()

    for procedure in self.procedures:
      listItem = ProcedureListItem(self.comm, getProcedureTitle(procedure, self.comm))
      self.procedureListLayout.addWidget(listItem)
      self.procedureListLayout.addWidget(HSeperator())
    if not self.procedures:
      self.procedureListLayout.addWidget(Label("No Procedures found.", "h1", style="color: grey;"))
    self.procedureListLayout.addStretch(1)
