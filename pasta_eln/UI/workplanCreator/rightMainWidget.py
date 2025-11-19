import qtawesome
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label
from pasta_eln.UI.workplanCreator.workplanListItem import WorkPlanListItem


class RightMainWidget(QFrame):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.headerLabel = Label("Current Workplan", 'h1')
    self.nameEdit = QLineEdit(placeholderText="Enter name of Workplan", clearButtonEnabled=True, frame=False)
    self.workplanWidget = QWidget()
    self.workplanLayout = QVBoxLayout()

    self.comm.addProcedure.connect(self.addProcedure)

    # Workplanlayout
    self.workplanLayout.setSpacing(0)
    self.workplanLayout.setContentsMargins(0, 0, 0, 0)
    self.workplanWidget.setLayout(self.workplanLayout)

    # Style
    self.setFrameShape(QFrame.Shape.StyledPanel)
    self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    # layout
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.headerLabel)
    self.layout.addWidget(self.nameEdit)
    self.layout.addWidget(HSeperator())
    self.layout.addWidget(self.workplanWidget)
    self.layout.addStretch(1)
    self.setLayout(self.layout)

  def addProcedure(self, title: str, tags: list[str], sample: str, procedures: dict[str, str]):
    listItem = WorkPlanListItem(self.comm, title, tags, sample, procedures)
    self.workplanLayout.addWidget(listItem)
    icon = qtawesome.icon("ei.arrow-down").pixmap(30, 30).scaled(10, 30, Qt.AspectRatioMode.IgnoreAspectRatio,
                                                                 Qt.TransformationMode.SmoothTransformation)
    self.workplanLayout.addWidget(QLabel(pixmap=icon), alignment=Qt.AlignmentFlag.AlignHCenter)
