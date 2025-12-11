import copy

import qtawesome
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QInputDialog, QLabel, QPushButton, QScrollArea, QSizePolicy, \
  QVBoxLayout, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label
from pasta_eln.UI.workplanCreator.workplanFunctions import generateAndSaveWorkplan
from pasta_eln.UI.workplanCreator.workplanListItem import WorkplanListItem


class RightMainWidget(QWidget):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.storage = self.comm.storage
    self.headerLabel = Label("Current Workplan", 'h1')
    self.workplanWidget = QWidget()
    self.workplanLayout = QVBoxLayout()
    self.saveButton = QPushButton("Finish and Save Workplan")

    self.comm.addProcedure.connect(self.addProcedure)
    self.setAcceptDrops(True)

    # scrollarea for list
    scrollarea = QScrollArea(widgetResizable=True)
    # scrollarea.setContentsMargins(0, 0, 0, 0)
    scrollarea.setStyleSheet("QScrollArea {border: none;}")
    scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scrollarea.setWidget(self.workplanWidget)

    # Workplanlayout
    self.workplanLayout.setSpacing(0)
    self.workplanLayout.setContentsMargins(0, 0, 0, 0)
    self.workplanLayout.addStretch(1)
    # Workplanwidget
    self.workplanWidget.setLayout(self.workplanLayout)

    # SaveButton
    self.saveButton.setIcon(qtawesome.icon("mdi.content-save-move"))
    self.saveButton.setAutoDefault(True)
    self.saveButton.clicked.connect(self.saveWorkplan)

    # Style
    self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    # layout
    self.layout = QVBoxLayout()
    #self.layout.setContentsMargins(0,0,0,0)
    self.layout.addWidget(self.headerLabel)
    #self.layout.addWidget(HSeperator())
    self.layout.addWidget(scrollarea)
    self.layout.addWidget(self.saveButton)
    self.setLayout(self.layout)

  def addProcedure(self, procedureID: str, sample: str, parameters: dict[str, str], at: int = None):
    listItem = WorkplanListItem(
      self.comm,
      procedureID,
      sample,
      parameters,
      self)
    icon = qtawesome.icon("ph.arrow-down").pixmap(30, 30)
    label = QLabel(pixmap=icon)
    if at is not None:
      insertAt = at
    else:
      insertAt = self.workplanLayout.count() - 1
    self.workplanLayout.insertWidget(insertAt, label, alignment=Qt.AlignmentFlag.AlignHCenter)
    self.workplanLayout.insertWidget(insertAt, listItem)
    listItem.clicked.connect(lambda: self.highlightActiveItem(listItem))
    self.highlightActiveItem(listItem)
    self.saveButton.setFocus()

  def saveWorkplan(self):
    filename, ok = QInputDialog.getText(self, "Choose Workplan Name",
                                        "Choose a Name for your Workplan File:",
                                        text="unnamed_workplan")
    if not ok:
      return
    elif not filename:
      filename = "unnamed_workplan"
    workplan = {
      "name": filename,
      "procedures": []
    }
    for i in range(self.workplanLayout.count()):
      item = self.workplanLayout.itemAt(i).widget()
      if isinstance(item, WorkplanListItem):
        procedureID = item.procedureID
        sample = item.sample
        filledParameters = item.parameters
        defaultParameters = self.storage.getProcedureDefaultParameters(procedureID)
        for param in defaultParameters:
          if param in filledParameters:
            defaultParameters[param] = filledParameters[param]
        workplan["procedures"].append({
          "procedure": procedureID,
          "sample": sample,
          "parameters": defaultParameters
        })
    generateAndSaveWorkplan(self.comm, workplan, filename)

  def highlightActiveItem(self, listItem: WorkplanListItem):
    for i in range(self.workplanLayout.count()):
      item = self.workplanLayout.itemAt(i).widget()
      if isinstance(item, WorkplanListItem):
        item.lowlight()
    listItem.highlight()
