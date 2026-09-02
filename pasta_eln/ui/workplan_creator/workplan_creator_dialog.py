"""
The Top level Widget of the Workplan Creator Dialog. Containing the 3 Main Widgets:
  - LeftMainWidget: Displays list and search for choosing procedures
  - CenterMainWidget: Displays information and fill in Sample+Parameters for chosen procedure
  - RightMainWidget: Displays Workplan and export-button
"""
from typing import Any
from PySide6.QtWidgets import QApplication, QDialog, QSplitter, QVBoxLayout
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import SPACE
from pasta_eln.ui.workplan_creator.center_main_widget import CenterMainWidget
from pasta_eln.ui.workplan_creator.left_main_widget import LeftMainWidget
from pasta_eln.ui.workplan_creator.right_main_widget import RightMainWidget
from pasta_eln.ui.workplan_creator.workplan_functions import Workplan


class WorkplanCreatorDialog(QDialog):
  """
  The Top level Widget of the Workplan Creator Dialog. Containing the 3 Main Widgets:
  - LeftMainWidget: Displays list and search for choosing procedures
  - CenterMainWidget: Displays information and fill in Sample+Parameters for chosen procedure
  - RightMainWidget: Displays Workplan and export-button
  """

  def __init__(self, comm: Communicate, displayWorkplan: Workplan | None = None):
    """Initialize the dialog used to create or edit a workplan.

    Args:
      comm (Communicate): Shared communication object.
      displayWorkplan (Workplan | None): Existing workplan to edit, or ``None`` for a new one.
    """
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
    self.splitter = QSplitter(handleWidth=SPACE.M)
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
      self.setWindowTitle('Create workplan')
    screen = QApplication.primaryScreen().availableGeometry()
    self.resize(int(screen.width() * 0.75), int(screen.height() * 0.75))

    # layout
    self.mainLayout = QVBoxLayout(self)
    self.mainLayout.setContentsMargins(SPACE.M, SPACE.M, SPACE.M, SPACE.M)
    self.mainLayout.setSpacing(0)
    self.mainLayout.addWidget(self.splitter)

  def _onGetProjectDoc(self, doc: dict[str, Any]) -> None:
    """
    Callback function to set the window Title
    Args:
      doc: Document of the current project (contains name)
    """
    if doc['id'] == self.comm.projectID:
      self.setWindowTitle('Create workplan — Current project: ' + doc['name'])
