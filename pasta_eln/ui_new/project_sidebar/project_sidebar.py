"""The Toplevel Sidebar on the left that displays the projects to choose."""
import pandas as pd
import qtawesome
from PySide6.QtCore import Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, \
  QWidget

from pasta_eln.misc_tools import clearLayout
from pasta_eln.ui.config.main import Configuration
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import HSeparator, Label
from pasta_eln.ui_new.project_sidebar.project_card import ProjectCard


class ProjectSidebar(QWidget):
  """
  The Toplevel Sidebar on the left that displays the projects to choose.
  """

  def __init__(self, comm: Communicate, parent: QWidget | None = None) -> None:
    super().__init__(parent)
    self.comm = comm
    self.projects = pd.DataFrame()
    self.sideBarWidth = self.comm.configuration['GUI']['sidebarWidth']

    # Header-label
    self.headerLabel = Label("Projects", "h1")

    # newProject-Button
    self.newProjectButton = QPushButton("")
    self.newProjectButton.setStyleSheet("border: none;")
    self.newProjectButton.setToolTip("Create new Project")
    self.newProjectButton.setFixedSize(40, 40)
    iconColor = self.comm.palette.getThemeColor("foreground", "base")
    self.newProjectButton.setIcon(qtawesome.icon("ri.add-circle-line", color=iconColor))
    self.newProjectButton.setIconSize(self.newProjectButton.size())
    self.newProjectButton.clicked.connect(self.createNewProject)

    # Header
    self.header = QWidget()
    self.headerLayout = QHBoxLayout()
    self.headerLayout.addWidget(self.headerLabel, stretch=1)
    self.headerLayout.addWidget(self.newProjectButton)
    self.headerLayout.setContentsMargins(0, 0, 0, 0)
    self.header.setLayout(self.headerLayout)

    # Searchbar
    self.searchbar = QLineEdit(clearButtonEnabled=True)
    self.searchbar.setPlaceholderText("Search Project or #tag")
    self.searchbar.textEdited.connect(self.filterItems)

    # Projectlist
    self.projectList = QWidget()
    self.projectListLayout = QVBoxLayout()
    self.projectListLayout.setContentsMargins(3, 0, 3, 0)
    self.projectListLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.projectList.setLayout(self.projectListLayout)

    # Scrollarea for Projectlist
    self.scrollarea = QScrollArea(widgetResizable=True)
    self.scrollarea.setStyleSheet("QScrollArea {border: none;}")
    self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.scrollarea.setContentsMargins(0, 0, 0, 0)
    self.scrollarea.setWidget(self.projectList)

    # Settings-Button
    self.settingsButton = QPushButton("")
    self.settingsButton.setStyleSheet("border: none;")
    self.settingsButton.setToolTip("Open Configuration/Settings")
    self.settingsButton.setFixedSize(40, 40)
    self.settingsButton.setIcon(qtawesome.icon("ri.settings-2-line", color=iconColor))
    self.settingsButton.setIconSize(self.newProjectButton.size())
    self.settingsButton.clicked.connect(lambda: Configuration(self.comm).exec())

    # Manage-Projects-Button
    self.manageProjectsButton = QPushButton("Manage Projects")
    self.manageProjectsButton.clicked.connect(lambda: self.comm.changeTable.emit('x0', ''))
    self.manageProjectsButton.setFixedHeight(40)

    # Footer
    self.footerLayout = QHBoxLayout()
    self.footerLayout.addWidget(self.settingsButton)
    self.footerLayout.addWidget(self.manageProjectsButton)
    self.footerLayout.setContentsMargins(0, 0, 0, 0)
    self.footer = QWidget()
    self.footer.setLayout(self.footerLayout)

    # Style
    # self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    # self.setMinimumWidth(200)

    # Layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.addWidget(self.header)
    self.mainLayout.addWidget(self.searchbar)
    self.mainLayout.addWidget(HSeparator())
    self.mainLayout.addWidget(self.scrollarea, stretch=1)
    self.mainLayout.addWidget(self.footer)
    self.mainLayout.setSpacing(10)
    self.setLayout(self.mainLayout)

    # Signals
    self.comm.changeSidebar.connect(self.paint)
    self.comm.changeProject.connect(self.highlightActiveProject)
    self.comm.backendThread.worker.beSendTable.connect(self.onGetData)
    self.comm.themeUpdated.connect(self.reloadStyle)

    # CODE
    self.comm.uiRequestTable.emit('x0', '', self.comm.configuration['GUI']['showHidden'] == 'Yes')

  @Slot(str)
  def paint(self, projectChoice: str = '') -> None:
    """
    Redraw sidebar: e.g. after change of project visibility in table

    Args:
      projectChoice (str): projectID on which to focus: '' string=draw default=none; 'redraw' implies redraw; id implies id
    """
    # 1. Empty/Clear the Layout
    clearLayout(self.projectListLayout)

    # 2. Update Project in comm if necessary
    if projectChoice != 'redraw':
      self.comm.projectID = projectChoice

    # 3. Fill projectList with Items = ProjectCards
    if self.projects.empty:
      emptyWarning = Label('Create a Project by clicking on the "+"-button above.', "h1",
                           style=f"color: {self.comm.palette.getThemeColor("foreground", "disabled")};")
      emptyWarning.setWordWrap(True)
      self.projectListLayout.addWidget(emptyWarning)
    self.projects = self.projects.sort_values('name', axis=0).reset_index(drop=True)
    for i in range(self.projects.shape[0]):
      self.projectListLayout.addWidget(ProjectCard(self.comm, self.projects.iloc[i, :]))

  @Slot(pd.DataFrame, str)
  def onGetData(self, projects: pd.DataFrame, docType: str) -> None:
    """
    Callback function to handle the received projects data

    Args:
      projects (pd.DataFrame): DataFrame containing project information
      docType (str): document type (should be 'x0' for projects for the sidebar)
    """
    if docType == 'x0':
      self.projects = projects
      self.paint('redraw')

  @Slot()
  def createNewProject(self) -> None:
    """ Opens the form to create a new Project and redraws sidebar"""
    self.comm.formDoc.emit({'type': ["x0"], '_projectID': self.comm.projectID})
    self.comm.changeTable.emit("x0", self.comm.projectID)
    self.comm.changeSidebar.emit('redraw')

  @Slot(str, str)
  def highlightActiveProject(self, projectID: str, docID: str) -> None:
    """
    Slot for changeProject-Signal
    Highlights the currently active project-card in the sidebar and lowlights every other
    Args:
      projectID (str): project ID of Project to highlight
      docID (str): document ID in Signal that is not used here
    """
    for i in range(self.projectListLayout.count()):
      layoutItem = self.projectListLayout.itemAt(i)
      item = layoutItem.widget() if layoutItem is not None else None
      if isinstance(item, ProjectCard):
        item.lowlight()
        if item.project["id"] == projectID:
          item.highlight()

  @Slot()
  def filterItems(self, filterText: str) -> None:
    """
    hides/shows the procedures that match the phrase in the searchbar
    Args:
      filterText: text that is used to filter the procedures in the list (e.g. Content of the Searchbar)
    """
    filterWords = [word.strip() for word in filterText.lower().split(",")]
    for i in range(self.projectListLayout.count()):
      layoutItem = self.projectListLayout.itemAt(i)
      item = layoutItem.widget() if layoutItem is not None else None
      if not isinstance(item, ProjectCard):
        continue
      name = item.project["name"].lower()
      tags = item.project["tags"].lower().split(",")
      tags = [tag.lower().strip() for tag in tags]
      item.show()
      for word in filterWords:
        if word.startswith("#"):
          word = word[1:]
          item.hide()
          for tag in tags:
            if word in tag:
              item.show()
              break
        elif word in name or filterWords == [""]:
          continue
        else:
          item.hide()
          break

  @Slot()
  def reloadStyle(self) -> None:
    """
    Update the color of buttons after the theme is changed, because they don't change automatically.
    """
    iconColor = self.comm.palette.getThemeColor("foreground", "base")
    self.newProjectButton.setIcon(qtawesome.icon("ri.add-circle-line", color=iconColor))
    self.settingsButton.setIcon(qtawesome.icon("ri.settings-2-line", color=iconColor))
