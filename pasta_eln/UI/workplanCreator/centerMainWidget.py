import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLineEdit, QPushButton, \
  QSizePolicy, QTextEdit, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label


class CenterMainWidget(QWidget):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.activeProcedureID = None

    # GUI Elements init; setup in changeActiveProcedure()
    self.headerLabel = Label("", "h1")
    self.tagLayout = QHBoxLayout()
    self.shortDesc = Label("", "h2")
    self.description = QTextEdit(markdown="", readOnly=True)
    self.formFrame = QFrame()
    self.parameterForm = QFormLayout()
    self.addToWorkplanButton = QPushButton("Add to Workplan")
    self.sampleBox = QComboBox()

    # Signal
    self.comm.activeProcedureChanged.connect(self.changeActiveProcedure)

    # Style
    self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)  # Causes whole Widget to be fully
    # squishable

    # layout
    self.layout = QGridLayout()
    self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    self.layout.addWidget(Label('Choose a Procedure on the left side to begin.', 'h1', style="color: grey;"), 0, 0)
    self.setLayout(self.layout)

  def changeActiveProcedure(self, toProcedure: str, sample: str = None, parameters: dict[str, str] = None):
    """

    """
    # Create empty Layout if layout is not created yet (FIRST SETUP)
    if not self.activeProcedureID:
      self.layout.takeAt(0).widget().deleteLater()
      # Procedure Name / Header Label
      self.layout.addWidget(self.headerLabel, 0, 0, 1, -1)
      # Tags
      self.layout.addLayout(self.tagLayout, 1, 0, 1, -1)
      # Short Description
      self.shortDesc.setWordWrap(True)
      self.layout.addWidget(self.shortDesc, 2, 0)
      # Short Seperator (Between short and long description)
      self.layout.addWidget(HSeperator(), 3, 0)
      # Long Description
      self.layout.addWidget(self.description, 4, 0)
      # self.description.setStyleSheet(self.comm.palette.get('secondaryDark', 'background-color') +
      #                                self.comm.palette.get('primaryText', 'color') + """
      #                                border: none;
      #                                padding: 0px;
      #                                """)
      self.description.document().setDocumentMargin(0)
      # Sample and Parameter field
      self.comm.backendThread.worker.beSendTable.connect(self._addSampleBoxItems)
      self.comm.uiRequestTable.emit('sample', self.comm.projectID, False)
      self.formFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
      self.formFrame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
      # formFrame.setStyleSheet(self.comm.palette.get('secondary', 'background-color'))  # +
      # self.comm.palette.get('secondaryLight', 'border-color'))
      self.formFrame.setLayout(self.parameterForm)
      self.parameterForm.addRow(Label("Choose Sample:", "h2"))
      self.parameterForm.addRow(self.sampleBox)
      self.parameterForm.addRow(Label("Choose Parameters:", "h2"))
      self.layout.addWidget(self.formFrame, 2, 1, 3, 1)
      self.comm.storageUpdated.connect(self._onProcedureTextUpdated)
      # Add-Button
      self.addToWorkplanButton.setIcon(qta.icon("ei.plus", scale_factor=1))
      self.layout.addWidget(self.addToWorkplanButton, 6, 1)
      self.addToWorkplanButton.clicked.connect(lambda: self.comm.addProcedure.emit(
        self.activeProcedureID, self.sampleBox.currentText(), self.getFilledParameters()))
      # END OF FIRST SETUP

    # Fill Layout with active Procedure
    self.activeProcedureID = toProcedure
    self.sample = sample
    self.parameters = parameters
    # Long Description, content gets cut-off --> need to wait for Thread and reading of file
    self.storage.requestProcedureText(self.activeProcedureID)
    # Procedure Name
    self.headerLabel.setText(self.storage.getProcedureTitle(self.activeProcedureID))
    # self.headerLabel.setWordWrap(True)
    # Tags
    # remove old tags
    while self.tagLayout.count():
      item = self.tagLayout.takeAt(0)
      w = item.widget()
      if w:
        w.setParent(None)
      # add new tags
    for tag in self.storage.getProcedureTags(self.activeProcedureID):
      self.tagLayout.addWidget(QPushButton(tag))
    self.tagLayout.addStretch(1)
    # Short Description
    self.shortDesc.setText(self.storage.getProcedureShortDescription(self.activeProcedureID))

  def getFilledParameters(self):
    filledParameters = {}
    for i in range(3, self.parameterForm.rowCount()):
      labelItem = self.parameterForm.itemAt(i, QFormLayout.ItemRole.LabelRole)
      fieldItem = self.parameterForm.itemAt(i, QFormLayout.ItemRole.FieldRole)
      if labelItem and fieldItem:
        labelItemText = labelItem.widget().text()
        fieldItemText = fieldItem.widget().text()
        filledParameters[labelItemText] = fieldItemText
    return filledParameters

  def _onProcedureTextUpdated(self, docID):
    if docID == self.activeProcedureID:
      self.description.setMarkdown(self.storage.getProcedureText(self.activeProcedureID))
    # Sample and Parameter Form
    for _ in range(self.parameterForm.rowCount() - 3):
      self.parameterForm.removeRow(3)  # Lösche Parameter, ab Zeile 3 sind alle Zeilen Parameter
    if self.sample:
      self.sampleBox.setCurrentText(self.sample)
    defaultParameters = self.storage.getProcedureDefaultParameters(self.activeProcedureID)
    if not defaultParameters:
      self.parameterForm.addWidget(Label("This Procedure has no Parameters", "h3"))
    for parameter in defaultParameters:
      lineEdit = QLineEdit(placeholderText=defaultParameters[parameter])
      self.parameterForm.addRow(Label(parameter, "h3"), lineEdit)
      if parameter in self.parameters:
        lineEdit.setText(self.parameters[parameter])

  def _addSampleBoxItems(self, table: dict, docType: str):
    if docType == "sample":
      self.sampleBox.addItems(table["name"])
