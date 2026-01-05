"""
The Top level Widget of the Workplan Creator Dialog. Containing the 3 Main Widgets:
  - LeftMainWidget: Displays list and search for choosing procedures
  - CenterMainWidget: Displays information and fill in Sample+Parameters for chosen procedure
  - RightMainWidget: Displays Workplan and export-button
"""
from PySide6.QtWidgets import QApplication, QDialog, QGridLayout, QSplitter

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.workplanCreator.centerMainWidget import CenterMainWidget
from pasta_eln.UI.workplanCreator.leftMainWidget import LeftMainWidget
from pasta_eln.UI.workplanCreator.rightMainWidget import RightMainWidget


class WorkplanCreatorDialog(QDialog):
  """
  The Top level Widget of the Workplan Creator Dialog. Containing the 3 Main Widgets:
  - LeftMainWidget: Displays list and search for choosing procedures
  - CenterMainWidget: Displays information and fill in Sample+Parameters for chosen procedure
  - RightMainWidget: Displays Workplan and export-button
  """

  def __init__(self, comm: Communicate, displayWorkplan: dict = None):
    super().__init__()

    # Configure Backend / Storage
    self.comm = comm

    # Widget that Displays list and search for choosing procedures
    self.leftMainWidget = LeftMainWidget(self.comm)

    # Widget that Displays information and fill in Sample+Parameters for chosen procedure
    self.centerMainWidget = CenterMainWidget(self.comm)

    # Widget that Displays Workplan and export-button
    self.rightMainWidget = RightMainWidget(self.comm, displayWorkplan)

    # splitter to resize each column
    self.splitter = QSplitter(handleWidth=3)
    self.splitter.addWidget(self.leftMainWidget)
    self.splitter.setStretchFactor(0, 1)
    self.splitter.addWidget(self.centerMainWidget)
    self.splitter.setStretchFactor(1, 1)
    self.splitter.addWidget(self.rightMainWidget)
    self.splitter.setStretchFactor(2, 1)

    # style
    if self.comm.projectID:
      self.comm.backendThread.worker.beSendDoc.connect(self._onGetProjectDoc)
      self.comm.uiRequestDoc.emit(self.comm.projectID)
    else:
      self.setWindowTitle("Workplan Creator")
    screen = QApplication.primaryScreen().availableGeometry()
    self.resize(int(screen.width() * 0.75), int(screen.height() * 0.75))

    # layout
    self.layout = QGridLayout()
    self.layout.addWidget(self.splitter, 0, 0)
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(self.layout)

  def _onGetProjectDoc(self, doc: dict) -> None:
    """
    Callback function to set the window Title
    Args:
      doc: Document of the current project (contains name)
    """
    if doc["id"] == self.comm.projectID:
      self.setWindowTitle("Workplan Creator - Current Project: " + doc["name"])
