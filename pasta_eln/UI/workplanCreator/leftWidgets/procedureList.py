from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import Label
from pasta_eln.UI.workplanCreator.workplanFunctions import get_db_procedures


class ProcedureList(QWidget):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.procedures = []

    # Signale
    self.comm.storageUpdated.connect(self.update_procedures)

    # layout
    self.layout = QVBoxLayout()
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.setSpacing(0)
    self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    self.setLayout(self.layout)

  def update_procedures(self):
    """

    """
    self.procedures = get_db_procedures(self.comm)
    # Layout leeren
    while self.layout.count():
      item = self.layout.takeAt(0)
      widget = item.widget()
      if widget:
        widget.deleteLater()

    for procedure in self.procedures:
      listItem = QPushButton(procedure)
      listItem.clicked.connect(lambda _, p = procedure: self.comm.activeProcedureChanged.emit(p))
      self.layout.addWidget(listItem)
    if not self.procedures:
      self.layout.addWidget(Label("No Procedures found.", "h1", style="color: grey;"))
    self.layout.addStretch(1)
