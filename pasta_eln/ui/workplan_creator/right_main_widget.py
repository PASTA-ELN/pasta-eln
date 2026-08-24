"""Widget on the right of the WorkplanCreator-Dialog. Contains a list of workplanListItems that represents the Workplan"""
import qtawesome
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QInputDialog, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Label
from pasta_eln.ui.workplan_creator.workplan_functions import (Storage, Workplan, WorkplanProcedure,
                                                              generateAndSaveWorkplan)
from pasta_eln.ui.workplan_creator.workplan_list_item import WorkplanListItem


class RightMainWidget(QWidget):
  """
  Widget on the right of the WorkplanCreator-Dialog. Contains a list of workplanListItems that represents the Workplan
  """

  def __init__(self, comm: Communicate, displayWorkplan: Workplan | None = None) -> None:
    """Initialize the workplan preview pane.

    Args:
      comm (Communicate): Shared communication object.
      displayWorkplan (Workplan | None): Workplan currently selected for display, if any.
    """
    super().__init__()
    self.comm = comm
    if self.comm.storage is None:
      raise RuntimeError('Workplan storage must be initialized before the right widget')
    self.storage: Storage = self.comm.storage
    self.headerLabel = Label('Current Workplan', 'h1')
    self.workplanWidget = QWidget()
    self.workplanLayout = QVBoxLayout()
    self.saveButton = QPushButton('Finish and Save Workplan')

    self.comm.addProcedure.connect(self.addProcedure)
    self.setAcceptDrops(True)

    # scrollarea for list
    scrollarea = QScrollArea(widgetResizable=True)
    # scrollarea.setContentsMargins(0, 0, 0, 0)
    scrollarea.setStyleSheet('QScrollArea {border: none;}')
    scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scrollarea.setWidget(self.workplanWidget)

    # Workplanlayout
    self.workplanLayout.setSpacing(0)
    self.workplanLayout.setContentsMargins(0, 0, 0, 0)
    self.workplanLayout.addStretch(1)
    # Workplanwidget
    self.workplanWidget.setLayout(self.workplanLayout)

    # SaveButton
    self.saveButton.setIcon(qtawesome.icon('mdi.content-save-move'))
    self.saveButton.setAutoDefault(True)
    self.saveButton.clicked.connect(self.saveWorkplan)

    # Style
    self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    # layout
    self.mainLayout = QVBoxLayout()
    # self.mainLayout.setContentsMargins(0,0,0,0)
    self.mainLayout.addWidget(self.headerLabel)
    # self.mainLayout.addWidget(HSeperator())
    self.mainLayout.addWidget(scrollarea)
    self.mainLayout.addWidget(self.saveButton)
    self.setLayout(self.mainLayout)
    if displayWorkplan:
      self.displayWorkplan(displayWorkplan)


  def addProcedure(self, procedureID: str, sample: str, parameters: dict[str, str], at: int | None = None) -> None:
    """
    Add a new workPlanListItem to the list
    Args:
      procedureID: ID of the procedure that is represented by this item
      sample: the user-chosen sample for this particular Item
      parameters: the filled-out parameters for this item
      at: Optional. Position where to insert the Item into the list. Default: at the end.
    """
    listItem = WorkplanListItem(
      self.comm,
      procedureID,
      sample,
      parameters,
      self)
    insertAt = at if at is not None else self.workplanLayout.count() - 1
    self.workplanLayout.insertWidget(insertAt, listItem)
    listItem.clicked.connect(lambda: self.highlightActiveItem(listItem))
    self.highlightActiveItem(listItem)
    self.saveButton.setFocus()

  def saveWorkplan(self) -> None:
    """
    Extracts info from the workplanItems and creates the json for saving it
    """
    dialog = QInputDialog()
    filename, ok = dialog.getText(self, 'Choose Workplan Name',
                                  'Choose a Name for your Workplan File:',
                                  text='unnamed_workplan')
    if not ok:
      return
    elif not filename:
      filename = 'unnamed_workplan'
    workplan: Workplan = {'name': filename, 'procedures': []}
    for i in range(self.workplanLayout.count()):
      layoutItem = self.workplanLayout.itemAt(i)
      item = layoutItem.widget() if layoutItem is not None else None
      if isinstance(item, WorkplanListItem):
        procedureID = item.procedureID
        sample = item.sample
        filledParameters = item.parameters
        defaultParameters = self.storage.getProcedureDefaultParameters(procedureID)
        for param in defaultParameters:
          if param in filledParameters:
            defaultParameters[param] = filledParameters[param]
        workplanProcedure: WorkplanProcedure = {'procedure': procedureID, 'sample': sample, 'parameters': defaultParameters}
        workplan['procedures'].append(workplanProcedure)
    generateAndSaveWorkplan(self.comm, workplan, filename)


  def highlightActiveItem(self, listItem: WorkplanListItem) -> None:
    """
    Highlights the WorkplanListItem in the argument and lowlights every other one
    Args:
      listItem: The WorkplanListItem to highlight
    """
    for i in range(self.workplanLayout.count()):
      layoutItem = self.workplanLayout.itemAt(i)
      item = layoutItem.widget() if layoutItem is not None else None
      if isinstance(item, WorkplanListItem):
        item.lowlight()
    if listItem:
      listItem.highlight()


  def displayWorkplan(self, workplan: Workplan) -> None:
    """
    Adds all the procedures from a given workplan-dict to the Workplan in the Creator.
    What happens when the procedure, sample or parameters are not in Pasta? -Currently not handled
    Args:
      workplan: Currently a json-like dict containing the serialized Workplan
    """
    for procedure in workplan['procedures']:
      procedureID: str = procedure['procedure']
      sample: str = procedure['sample']
      parameters = procedure['parameters']
      self.addProcedure(procedureID, sample, parameters)
