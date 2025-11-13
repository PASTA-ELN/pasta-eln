from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget

from pasta_eln.UI.guiCommunicate import Communicate


class RightMainWidget(QWidget):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm

    self.nameEdit = QLineEdit(placeholderText="Enter name of Workplan", clearButtonEnabled=True, frame=False)


    # layout
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.nameEdit)
    self.setLayout(self.layout)
