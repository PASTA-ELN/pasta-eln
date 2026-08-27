"""Widget on the left side of the WorkplanCreator-Dialog. Contains a Searchbar and a list of Procedures to choose from"""
from PySide6.QtWidgets import QLineEdit, QScrollArea, QSizePolicy, QVBoxLayout, QWidget
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import HSeparator, Label
from pasta_eln.ui.workplan_creator.procedure_list_item import ProcedureListItem
from pasta_eln.ui.workplan_creator.workplan_functions import Storage


class LeftMainWidget(QWidget):
  """
  Widget on the left side of the WorkplanCreator-Dialog. Contains a Searchbar and a list of Procedures to choose from
  """

  def __init__(self, comm: Communicate) -> None:
    """Initialize the procedure-list pane with shared communication state.

    Args:
      comm (Communicate): Shared communication object.
    """
    super().__init__()
    self.comm = comm
    self.storage: Storage = Storage(self.comm, self.comm.projectID)
    self.comm.storage = self.storage
    self.currentProjectID = self.comm.projectID
    self.procedures: list[str] = []

    # headerLabel
    self.headerLabel = Label('Choose Procedures', 'h1')

    # searchbar
    self.searchbar = QLineEdit(clearButtonEnabled=True)
    self.searchbar.setPlaceholderText('Search Procedure or #tag')
    self.searchbar.textEdited.connect(self.filterItems)

    # procedureList
    self.procedureList = QWidget()
    self.procedureListLayout = QVBoxLayout()
    self.procedureListLayout.setContentsMargins(0, 0, 0, 0)
    self.procedureListLayout.setSpacing(0)
    self.procedureList.setLayout(self.procedureListLayout)

    # scrollarea
    scrollarea = QScrollArea(widgetResizable=True)
    scrollarea.setContentsMargins(0, 0, 0, 0)
    scrollarea.setWidget(self.procedureList)

    # Style
    self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    # layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.addWidget(self.headerLabel)
    self.mainLayout.addWidget(self.searchbar)
    self.mainLayout.addWidget(scrollarea)
    self.setLayout(self.mainLayout)

    # misc
    self.comm.storageUpdated.connect(self.updateProcedures)

  def updateProcedures(self, projID: str) -> None:
    """
    Add all Procedures from the current project to the list
    Args:
      projID: Identifier, if the Signal is meant for this function
    """
    if projID != self.currentProjectID:
      return
    self.procedures = self.storage.getProcedureIDs()
    # empty Layout
    while self.procedureListLayout.count():
      item = self.procedureListLayout.takeAt(0)
      if item is None:
        continue
      if widget := item.widget():
        widget.deleteLater()
    firstSeparator = HSeparator()
    self.procedureListLayout.addWidget(firstSeparator)
    for procedureID in self.procedures:
      listItem = ProcedureListItem(
        self.comm,
        procedureID)
      self.procedureListLayout.addWidget(listItem)
      self.procedureListLayout.addWidget(HSeparator())
    if not self.procedures:
      firstSeparator.hide()
      self.procedureListLayout.addWidget(
        Label('No Procedure found in\ncurrent Project.', 'h1',
              style=f"color: {self.comm.palette.getThemeColor('foreground', 'disabled')};"))
    self.procedureListLayout.addStretch(1)

  def filterItems(self, filterText: str) -> None:
    """
    hides/shows the procedures that match the phrase in the searchbar
    Args:
      filterText: text that is used to filter the procedures in the list (e.g. Content of the Searchbar)
    """
    filterWords = [word.strip() for word in filterText.lower().split(',')]
    for i in range(1, self.procedureListLayout.count() - 1, 2):
      widgetItem    = self.procedureListLayout.itemAt(i)
      separatorItem = self.procedureListLayout.itemAt(i + 1)
      widget    = widgetItem.widget()    if widgetItem    is not None else None
      separator = separatorItem.widget() if separatorItem is not None else None
      if widget is None or separator is None:
        continue
      widget.show()
      separator.show()
      if not isinstance(widget, ProcedureListItem):
        continue
      procedureID = widget.procedureID
      procedureName = self.storage.getProcedureTitle(procedureID).lower()
      for word in filterWords:
        if word.startswith('#'):
          tags = self.storage.getProcedureTags(procedureID)
          widget.hide()
          separator.hide()
          for tag in tags:
            if word.lower() in tag.lower():
              widget.show()
              separator.show()
              break
        elif word in procedureName or filterWords == ['']:
          continue
        else:
          widget.hide()
          separator.hide()
          break
