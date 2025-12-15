"""Widget in the middle of the WorkplanCreator-Dialog. Displays selected procedure and choices for Sample/Procedure"""
import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
  QScrollArea, QSizePolicy, QTextEdit, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label
from pasta_eln.UI.workplanCreator.workplanListItem import WorkplanListItem


class CenterMainWidget(QWidget):
  """
  Widget in the middle of the WorkplanCreator-Dialog. Displays selected procedure and choices for Sample/Procedure
  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.activeProcedureID = None
    self.activeListItem = None
    self.sample = None
    self.parameters = None

    # GUI Elements init; setup in changeActiveProcedure()
    self.headerLabel = Label("", "h1")
    self.tagLayout = QHBoxLayout()
    self.shortDesc = QLabel("")
    self.description = QTextEdit(markdown="", readOnly=True)
    self.formScrollArea = QScrollArea()
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

  def changeActiveProcedure(self, toProcedure: str, sample: str = None, parameters: dict[str, str] = None,
                            # pylint: disable=missing-param-doc
                            workplanListItem: WorkplanListItem = None):
    """
    Change the current displayed Procedure of the Widget

    Args:
      toProcedure (str): docID of the procedure the Widget should display now
      sample (str): Optional. Name of the sample that is currently selected
      parameters (dict[str, str): Optional. Dict of parameter-value pairs, that are already filled out
      workplanListItem (WorkplanListItem): Optional. Item of the list (RightMainWidget) that the changes are
      connected to
    """
    # Create empty Layout if layout is not created yet (FIRST SETUP)
    if not self.activeProcedureID:
      self.layout.takeAt(0).widget().deleteLater()
      self.layout.setColumnStretch(0, 1)
      self.layout.setColumnStretch(1, 1)
      # Procedure Name / Header Label
      self.layout.addWidget(self.headerLabel, 0, 0, 1, -1)
      # Tags
      self.layout.addLayout(self.tagLayout, 1, 0, 1, -1)
      # Short Description
      self.shortDesc.setWordWrap(True)
      self.shortDesc.setMaximumHeight(100)
      self.shortDesc.setProperty("inactive", True)
      self.layout.addWidget(self.shortDesc, 2, 0)
      # Short Seperator (Between short and long description)
      self.layout.addWidget(HSeperator(), 3, 0)
      # Long Description
      self.description.setStyleSheet(f"""
      background-color: {self.palette().window().color().name()};
      border: none;
      padding: 0px;
      """)
      self.description.setFocusPolicy(Qt.FocusPolicy.NoFocus)
      self.description.document().setDocumentMargin(0)
      self.layout.addWidget(self.description, 4, 0)
      # Sample and Parameter field
      self.comm.backendThread.worker.beSendTable.connect(self._addSampleBoxItems)
      self.comm.uiRequestTable.emit('sample', self.comm.projectID, False)
      self.formScrollArea.setWidgetResizable(True)
      self.formScrollArea.setContentsMargins(0, 0, 0, 0)
      self.formScrollArea.setStyleSheet("QScrollArea{border: none;}")
      self.formScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
      self.formFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
      self.formFrame.setFrameShape(QFrame.Shape.Panel)
      self.formFrame.setLayout(self.parameterForm)
      self.formScrollArea.setWidget(self.formFrame)
      self.parameterForm.addRow(Label("Choose Sample:", "h2"))
      self.parameterForm.addRow(self.sampleBox)
      self.parameterForm.addRow(Label("Choose Parameters:", "h2"))
      self.layout.addWidget(self.formScrollArea, 2, 1, 3, 1)
      self.comm.storageUpdated.connect(self._onProcedureTextUpdated)
      # Add-Button
      self.addToWorkplanButton.setIcon(qta.icon("ei.plus", scale_factor=1))
      self.addToWorkplanButton.setDefault(True)
      self.layout.addWidget(self.addToWorkplanButton, 6, 1)
      self.addToWorkplanButton.clicked.connect(lambda: self.comm.addProcedure.emit(
        self.activeProcedureID, self.sampleBox.currentText(), self.getFilledParameters()))
    # END OF FIRST SETUP

    if self.activeListItem:
      # Disconnect Sample Changes from previous WorkplanItem
      try:
        self.sampleBox.currentTextChanged.disconnect(self.activeListItem.updateSample)
      except RuntimeError:  # self.activeListItem could already be deleted by the user
        pass
      if not workplanListItem:
        # If the new active Procedure is not a Procedure from the Workplan on the right
        try:
          self.activeListItem.lowlight()
        except RuntimeError:  # self.activeListItem could already be deleted by the user
          pass

    # Fill Layout with active Procedure
    self.activeProcedureID = toProcedure
    self.activeListItem = workplanListItem
    self.sample = sample
    self.parameters = parameters
    # Long Description, content gets cut-off --> need to wait for Thread and reading of file
    self.storage.requestProcedureText(self.activeProcedureID)
    # Procedure Name
    self.headerLabel.setText(self.storage.getProcedureTitle(self.activeProcedureID))
    # Tags
    # remove old tags
    while self.tagLayout.count():
      item = self.tagLayout.takeAt(0)
      w = item.widget()
      if w:
        w.setParent(None)
      # add new tags
    for tag in self.storage.getProcedureTags(self.activeProcedureID):
      if len(tag) > 20:
        tag = tag[:20] + "..."
      tagButton = QPushButton(tag)  # pylint: disable=qt-local-widget
      tagButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
      self.tagLayout.addWidget(tagButton)
    self.tagLayout.addStretch(1)
    # Short Description
    self.shortDesc.setText(self.storage.getProcedureShortDescription(self.activeProcedureID))

  def getFilledParameters(self) -> dict[str, str]:
    """
    Iterates through all Rows of the QFormLayout and extracts the parameter-value pairs of filled-in QLineEdits.

    Returns: dictionary of only the filled-in parameter-value pairs from the QFormLayout
    """
    filledParameters = {}
    for i in range(3, self.parameterForm.rowCount()):  # 3 because the sample part is skipped
      labelItem = self.parameterForm.itemAt(i, QFormLayout.ItemRole.LabelRole)
      fieldItem = self.parameterForm.itemAt(i, QFormLayout.ItemRole.FieldRole)
      if labelItem and fieldItem:
        labelItemText = labelItem.widget().text()
        fieldItemText = fieldItem.widget().text()
        filledParameters[labelItemText] = fieldItemText
    return filledParameters

  def _onProcedureTextUpdated(self, docID: str) -> None:
    """
    Callback for when the Storage-Object has read the files for the content; This function works as an extension to
    changeActiveProcedure() and contains the changes to description and parameters.
    Both the description and the parameters are dependend on this Storage update caused by storage.requestProcedureText.
    Args:
      docID: identifier, if the signal is meant for this function. Has to match self.currentActiveProcedureID
    """
    if docID != self.activeProcedureID:
      return
    self.description.setMarkdown(self.storage.getProcedureText(self.activeProcedureID))
    # Sample and Parameter Form
    for _ in range(self.parameterForm.rowCount() - 3):
      self.parameterForm.removeRow(3)  # Remove the old parameters from the layout (everything after row 3 of the Form)
    if self.activeListItem:
      # Connect Sample Changes to WorkplanItem (For Saving edits on selected Procedure in Workplan)
      self.sampleBox.currentTextChanged.connect(self.activeListItem.updateSample)
    if self.sample:
      self.sampleBox.setCurrentText(self.sample)
    defaultParameters = self.storage.getProcedureDefaultParameters(self.activeProcedureID)
    if not defaultParameters:
      self.parameterForm.addWidget(Label("This Procedure has no Parameters", "h3"))
    for parameter in defaultParameters:
      lineEdit = QLineEdit(placeholderText=defaultParameters[parameter])  # pylint: disable=qt-local-widget
      lineEdit.setToolTip("Default: " + defaultParameters[parameter])
      if self.activeListItem:
        # Connect Parameter Changes to WorkplanItem (For Saving edits on selected Procedure in Workplan)
        lineEdit.textChanged.connect(lambda text, param=parameter: self.activeListItem.updateParameter(text, param))
      label = Label(parameter, "h3", style="margin-left: 1em;", tooltip=parameter)
      label.setMaximumWidth(200)
      self.parameterForm.addRow(label, lineEdit)
      if parameter in self.parameters:
        lineEdit.setText(self.parameters[parameter])

  def _addSampleBoxItems(self, table: dict, docType: str) -> None:
    """
    Callback after request for the sample table, to fill the ComboBox with Samples from the Storage.
    This Function as a lambda causes weird C++ Storage access problems.
    Args:
      table: The sample table from the backend
      docType: identifier, to check if the signal is meant for this function.
    """
    if docType == "sample":
      self.sampleBox.addItems(table["name"])
