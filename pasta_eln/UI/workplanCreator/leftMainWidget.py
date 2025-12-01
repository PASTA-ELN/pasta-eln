from PySide6.QtWidgets import QLineEdit, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from pasta_eln.UI.guiCommunicate import Communicate
from pasta_eln.UI.guiStyle import HSeperator, Label
from pasta_eln.UI.workplanCreator.procedureListItem import ProcedureListItem
from pasta_eln.UI.workplanCreator.workplanFunctions import Storage


class LeftMainWidget(QWidget):
  """

  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm
    self.storage = None
    self.currentProjectID = self.comm.projectID
    self.procedures = []

    # headerLabel
    self.headerLabel = Label("Choose Procedures", "h1")
    self.headerLabel.setContentsMargins(11, 11, 11, 11)

    # searchbar
    self.searchbar = QLineEdit(clearButtonEnabled=True)
    self.searchbar.setPlaceholderText("Search Procedure or #tag")
    self.searchbar.textEdited.connect(self.filterItems)
    self.searchbar.setContentsMargins(11, 0, 11, 0)

    # seperator
    self.seperator = HSeperator()

    # procedureList
    self.procedureList = QWidget()
    self.procedureListLayout = QVBoxLayout()
    self.procedureListLayout.setContentsMargins(0, 0, 0, 0)
    self.procedureListLayout.setSpacing(0)
    self.procedureList.setLayout(self.procedureListLayout)

    # scrollarea
    scrollarea = QScrollArea(widgetResizable=True)
    scrollarea.setContentsMargins(0, 0, 0, 0)
    # scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scrollarea.setWidget(self.procedureList)

    # Style
    # self.setFrameShape(QFrame.Shape.StyledPanel)
    self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    # self.setFrameShadow(QFrame.Shadow.Raised)

    # layout
    self.layout = QVBoxLayout()
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.layout.addWidget(self.headerLabel)
    self.layout.addWidget(self.searchbar)
    self.layout.addWidget(self.seperator)
    self.layout.addWidget(scrollarea)
    self.setLayout(self.layout)

    # function calls
    self.comm.storageUpdated.connect(self.updateProcedures)
    self.comm.storage = Storage(self.comm, self.currentProjectID)
    self.storage = self.comm.storage

  def updateProcedures(self, projID: str):
    """

    """
    if projID != self.currentProjectID:
      return
    self.procedures = self.storage.getProcedureIDs()
    # Layout leeren
    while self.procedureListLayout.count():
      item = self.procedureListLayout.takeAt(0)
      widget = item.widget()
      if widget:
        widget.deleteLater()

    for procedureID in self.procedures:
      listItem = ProcedureListItem(
        self.comm,
        procedureID)
      self.procedureListLayout.addWidget(listItem)
      self.procedureListLayout.addWidget(HSeperator())
    if not self.procedures:
      self.procedureListLayout.addWidget(Label("No Procedures found.", "h1", style="color: grey;"))
    self.procedureListLayout.addStretch(1)

  def filterItems(self, filterText: str):
    filterText = filterText.lower().split(",")
    filterText = [word.strip() for word in filterText]
    print("1:", filterText)
    for i in range(0, self.procedureListLayout.count() - 1, 2):
      widget = self.procedureListLayout.itemAt(i).widget()
      seperator = self.procedureListLayout.itemAt(i + 1).widget()
      widget.show()
      seperator.show()
      if not isinstance(widget, ProcedureListItem):
        continue
      procedureID = widget.procedureID
      for word in filterText:
        if word.startswith("#"):
          tags = self.storage.getProcedureTags(procedureID)
          print("2:", tags)
          widget.hide()
          seperator.hide()
          for tag in tags:
            if word.lower() in tag.lower():
              print("DEBUG; Wort:", word.lower(), "; TAG:", tag.lower())
              widget.show()
              seperator.show()
              break
        else:
          if word in procedureID or filterText == [""]:
            continue
          else:
            widget.hide()
            seperator.hide()
            break
