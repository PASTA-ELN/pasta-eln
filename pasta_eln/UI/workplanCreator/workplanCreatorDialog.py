from PySide6.QtWidgets import QApplication, QDialog, QGridLayout, QSplitter

from .centerMainWidget import CenterMainWidget
from .leftMainWidget import LeftMainWidget
from .rightMainWidget import RightMainWidget
from ..guiCommunicate import Communicate


class WorkplanCreatorDialog(QDialog):
  """
  The Top level Widget of the Workplan Creator Dialog. Containing the 3 Main Widgets:
  - LeftMainWidget: Displays list and search for choosing procedures
  - CenterMainWidget: Displays information and fill in Sample+Paramaters for chosen procedure
  - RightMainWidget: Displays Workplan and export-button
  """

  def __init__(self, comm: Communicate):
    super().__init__()

    # Configure Backend / Storage
    self.comm = comm

    # Widget that Displays list and search for choosing procedures
    self.leftMainWidget = LeftMainWidget(self.comm)

    # Widget that Displays information and fill in Sample+Paramaters for chosen procedure
    self.centerMainWidget = CenterMainWidget(self.comm)

    # Widget that Displays Workplan and export-button
    self.rightMainWidget = RightMainWidget(self.comm)

    # splitter to resize each column
    self.splitter = QSplitter(handleWidth=5)
    self.splitter.addWidget(self.leftMainWidget)
    self.splitter.setStretchFactor(0, 1)
    self.splitter.addWidget(self.centerMainWidget)
    self.splitter.setStretchFactor(1, 1)
    self.splitter.addWidget(self.rightMainWidget)
    self.splitter.setStretchFactor(2, 1)

    # style
    if self.comm.projectID:
      self.setWindowTitle("Workplan Creator - Current Project:" + self.comm.projectID)
    else:
      self.setWindowTitle("Workplan Creator - Current Project: None/All")
    screen = QApplication.primaryScreen().availableGeometry()
    self.resize(int(screen.width() * 0.75), int(screen.height() * 0.75))

    # layout
    self.layout = QGridLayout()
    self.layout.addWidget(self.splitter, 0, 0)
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(self.layout)
