from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, \
  QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label


class CenterMainWidget(QWidget):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.activeProcedure = None

    # GUI Elements init; setup in changeActiveProcedure()
    self.headerLabel = Label("", "h1")
    self.tagLayout = QHBoxLayout()
    self.shortDesc = QLabel("", wordWrap=True)
    self.description = QTextEdit(markdown="", readOnly=True)
    self.parameterForm = QFormLayout()

    #Signal
    self.comm.activeProcedureChanged.connect(self.changeActiveProcedure)

    # layout
    self.layout = QGridLayout()
    self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    self.layout.addWidget(Label('Choose a Procedure on the left side to begin.', 'h1', style="color: grey;"),0 , 0)
    self.setLayout(self.layout)


  def changeActiveProcedure(self, toProcedure: str, sample: str = None, parameters: dict[str, str] = None):
    """

    """
    # Create empty Layout if layout is not created yet
    if not self.activeProcedure:
      self.layout.takeAt(0).widget().deleteLater()
      # Procedure Name
      self.layout.addWidget(self.headerLabel, 0, 0, 1, -1)
      # Tags
      self.layout.addLayout(self.tagLayout, 1, 0, 1, -1)
      # Long Seperator
      self.layout.addWidget(HSeperator(), 2, 0, 1, -1)
      # Short Description
      self.layout.addWidget(self.shortDesc, 3, 0)
      # Short Seperator (Between short and long description)
      self.layout.addWidget(HSeperator(), 4, 0)
      # Long Description
      self.layout.addWidget(self.description, 5, 0)
      self.description.setStyleSheet(self.comm.palette.get('secondaryDark', 'background-color') +
                                     self.comm.palette.get('primaryText', 'color') +"""
                                     border: none;
                                     padding: 0px;
                                     """)
      self.description.document().setDocumentMargin(0)
      # choose Sample and Parameter field
      self.parameterForm.addRow("Test:", QLineEdit()) # TODO Remove
      self.layout.addLayout(self.parameterForm, 3, 1, -1, 1)
      # Add Button
      # TODO clicked.connect
      self.layout.addWidget(QPushButton("Add to Workplan"), 6, 1)

    # Fill Layout with active Procedure
    self.activeProcedure = toProcedure
    # Procedure Name
    self.headerLabel.setText(toProcedure)
    # Tags
    tags = ["Not yet implemented"]
      # remove old tags
    while self.tagLayout.count():
      item = self.tagLayout.takeAt(0)
      w = item.widget()
      if w:
        w.setParent(None)
      # add new tags
    for tag in tags:
      self.tagLayout.addWidget(QPushButton(tag))
    self.tagLayout.addStretch(1)
    # Short Description
    self.shortDesc.setText("getShortDescription from DB")
    # Long Description
    self.description.setMarkdown("getLongDescription from DB")
    # choose Sample and Parameter field
    # TODO.....self.parameterForm
