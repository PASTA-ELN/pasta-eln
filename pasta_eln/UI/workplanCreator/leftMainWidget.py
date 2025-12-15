"""Widget on the left side of the WorkplanCreator-Dialog. Contains a Searchbar and a list of Procedures to choose from"""
from PySide6.QtWidgets import QLineEdit, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label
from pasta_eln.UI.workplanCreator.procedureListItem import ProcedureListItem
from pasta_eln.UI.workplanCreator.workplanFunctions import Storage


class LeftMainWidget(QWidget):
  """
  Widget on the left side of the WorkplanCreator-Dialog. Contains a Searchbar and a list of Procedures to choose from
  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.storage = None
    self.currentProjectID = self.comm.projectID
    self.procedures = []

    # headerLabel
    self.headerLabel = Label("Choose Procedures", "h1")

    # searchbar
    self.searchbar = QLineEdit(clearButtonEnabled=True)
    self.searchbar.setPlaceholderText("Search Procedure or #tag")
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
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.headerLabel)
    self.layout.addWidget(self.searchbar)
    self.layout.addWidget(scrollarea)
    self.setLayout(self.layout)

    # misc
    self.comm.storageUpdated.connect(self.updateProcedures)
    self.comm.storage = Storage(self.comm, self.currentProjectID)
    self.storage = self.comm.storage

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
      widget = item.widget()
      if widget:
        widget.deleteLater()
    firstSeperator = HSeperator()
    self.procedureListLayout.addWidget(firstSeperator)
    for procedureID in self.procedures:
      listItem = ProcedureListItem(
        self.comm,
        procedureID)
      self.procedureListLayout.addWidget(listItem)
      self.procedureListLayout.addWidget(HSeperator())
    if not self.procedures:
      firstSeperator.hide()
      self.procedureListLayout.addWidget(Label("No Procedure found in\ncurrent Project.", "h1", style="color: grey;"))
    self.procedureListLayout.addStretch(1)

  def filterItems(self, filterText: str):
    """
    hides/shows the procedures that match the phrase in the searchbar
    Args:
      filterText: text that is used to filter the procedures in the list (e.g. Content of the Searchbar)
    """
    filterText = filterText.lower().split(",")
    filterText = [word.strip() for word in filterText]
    for i in range(1, self.procedureListLayout.count() - 1, 2):
      widget = self.procedureListLayout.itemAt(i).widget()
      seperator = self.procedureListLayout.itemAt(i + 1).widget()
      widget.show()
      seperator.show()
      if not isinstance(widget, ProcedureListItem):
        continue
      procedureID = widget.procedureID
      procedureName = self.storage.getProcedureTitle(procedureID).lower()
      for word in filterText:
        if word.startswith("#"):
          tags = self.storage.getProcedureTags(procedureID)
          widget.hide()
          seperator.hide()
          for tag in tags:
            if word.lower() in tag.lower():
              widget.show()
              seperator.show()
              break
        elif word in procedureName or filterText == [""]:
          continue
        else:
          widget.hide()
          seperator.hide()
          break
