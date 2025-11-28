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
      # Long Seperator
      self.layout.addWidget(HSeperator(), 2, 0, 1, -1)
      # Short Description
      self.shortDesc.setWordWrap(True)
      self.layout.addWidget(self.shortDesc, 3, 0)
      # Short Seperator (Between short and long description)
      self.layout.addWidget(HSeperator(), 4, 0)
      # Long Description
      self.layout.addWidget(self.description, 5, 0)
      self.description.setStyleSheet(self.comm.palette.get('secondaryDark', 'background-color') +
                                     self.comm.palette.get('primaryText', 'color') + """
                                     border: none;
                                     padding: 0px;
                                     """)
      self.description.document().setDocumentMargin(0)
      # Sample and Parameter field
      self.comm.backendThread.worker.beSendTable.connect(
        lambda table, docType, samplebox=self.sampleBox: samplebox.addItems(
          table['name'] if docType == 'sample' else None))  # TODO:C++ Runtime Error when reopening workplanCreator
      self.comm.uiRequestTable.emit('sample', self.comm.projectID, False)
      formFrame = QFrame()
      formFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
      formFrame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
      formFrame.setStyleSheet(self.comm.palette.get('secondary', 'background-color'))  # +
      # self.comm.palette.get('secondaryLight', 'border-color'))
      formFrame.setLayout(self.parameterForm)
      self.parameterForm.addRow(Label("Choose Sample:", "h2"))
      self.parameterForm.addRow(self.sampleBox)
      self.parameterForm.addRow(Label("Choose Parameters:", "h2"))
      self.layout.addWidget(formFrame, 3, 1, 3, 1)
      # Add-Button
      self.addToWorkplanButton.setIcon(qta.icon("ei.plus", scale_factor=1))
      self.layout.addWidget(self.addToWorkplanButton, 6, 1)
      self.addToWorkplanButton.clicked.connect(lambda: self.comm.addProcedure.emit(
        self.activeProcedureID, self.sampleBox.currentText(), self.getFilledParameters()))
    # END OF FIRST SETUP

    # Fill Layout with active Procedure
    self.activeProcedureID = toProcedure
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
    # Long Description, content gets cut-off --> need to wait for Thread and reading of file
    def onProcedureTextUpdated(docID):
      if docID == self.activeProcedureID:
        self.description.setMarkdown(self.storage.getProcedureText(self.activeProcedureID))
      # Sample and Parameter Form
      for _ in range(self.parameterForm.rowCount() - 3):
        self.parameterForm.removeRow(3)  # Lösche Parameter, ab Zeile 3 sind alle Zeilen Parameter
      if sample:
        self.sampleBox.setCurrentText(sample)

      defaultParameters = self.storage.getProcedureDefaultParameters(self.activeProcedureID)
      if not defaultParameters:
        self.parameterForm.addWidget(Label("This Procedure has no Parameters", "h3"))
      for parameter in defaultParameters:
        lineEdit = QLineEdit(placeholderText=defaultParameters[parameter])
        self.parameterForm.addRow(Label(parameter, "h3"), lineEdit)
        if parameter in parameters:
          lineEdit.setText(parameters[parameter])
    self.comm.storageUpdated.connect(onProcedureTextUpdated)
    self.storage.requestProcedureText(self.activeProcedureID)

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
