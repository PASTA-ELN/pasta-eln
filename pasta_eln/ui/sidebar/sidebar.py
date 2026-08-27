"""The Toplevel Sidebar on the left that displays the projects to choose."""
from __future__ import annotations
from enum import Enum
import pandas as pd
import qtawesome as qta
from PySide6.QtCore import Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget
from pasta_eln.misc_tools import clearLayout
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import SPACE, Button, ButtonStyle, HSeparator, Label, Widget
from pasta_eln.ui.sidebar.project_card import ProjectCard


class ProjectSidebar(Widget):
  """
  The Toplevel Sidebar on the left that displays the projects to choose.
  """

  def __init__(self, comm: Communicate, parent: QWidget | None = None) -> None:
    """Initialize the project sidebar and connect it to the GUI state.

    Args:
      comm (Communicate): Shared communication object.
      parent (QWidget | None): Optional Qt parent widget, aka main window
    """
    super().__init__(parent)
    self.comm = comm
    self.projects = pd.DataFrame()
    self._initialProjectSelected = False
    self.showHiddenProjects = self.comm.configuration['GUI']['showHidden'] == 'Yes'

    # Header: project label and button
    self.headerLabel = Label('Projects', 'h2')
    self.newProjectBtn = Button('', self, Command.CREATE_PROJECT, icon='ri.add-circle-line',
                                tooltip='Create new project', iconSize='l', flat=True)
    self.headerW = QWidget()
    self.headerL = QHBoxLayout(self.headerW)
    self.headerL.addWidget(self.headerLabel, stretch=1)
    self.showHiddenBtn = Button('', self, Command.TOGGLE_HIDDEN_PROJECTS, self.headerL,
                                icon='fa5s.eye-slash', style=ButtonStyle.PRIMARY,
                                tooltip='Show hidden projects', checkable=True)
    self.showHiddenBtn.setChecked(self.showHiddenProjects)
    self.paintHiddenProjectButton()
    self.headerL.addWidget(self.newProjectBtn)
    self.headerL.setContentsMargins(0, 0, 0, 0)

    # Projectlist
    self.projectListW = QWidget()
    self.projectListL = QVBoxLayout(self.projectListW)
    self.projectListL.setContentsMargins(SPACE.S, 0, SPACE.S, 0)
    self.projectListL.setAlignment(Qt.AlignmentFlag.AlignTop)

    # Scrollarea for Projectlist
    self.scrollarea = QScrollArea(widgetResizable=True)
    self.scrollarea.setStyleSheet('QScrollArea {border: none;}')
    self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.scrollarea.setContentsMargins(0, 0, 0, 0)
    self.scrollarea.setWidget(self.projectListW)

    # Layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.addWidget(self.headerW)
    self.mainLayout.addWidget(HSeparator())
    self.mainLayout.addWidget(self.scrollarea, stretch=1)
    self.mainLayout.setSpacing(10)
    self.setLayout(self.mainLayout)

    # Signals
    self.comm.changeSidebar.connect(self.onSidebarChange)
    self.comm.changeProject.connect(self.highlightActiveProject)
    self.comm.backendThread.worker.beSendTable.connect(self.onGetData)

    # CODE
    self.comm.uiRequestTable.emit('x0', '', True)


  @Slot(str)
  def onSidebarChange(self, projectChoice: str) -> None:
    """Refresh projects after a visibility or project-selection change."""
    if projectChoice not in ('', 'redraw'):
      self.comm.projectID = projectChoice
    self.paint()
    self.comm.uiRequestTable.emit('x0', '', True)


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
      visibleProjects = self.visibleProjects()
      if not self._initialProjectSelected and not visibleProjects.empty:
        self._initialProjectSelected = True
        projectId = visibleProjects.iloc[0]['id']
        self.comm.projectID = projectId
        self.comm.changeProject.emit(projectId, '')


  @Slot(str)
  def paint(self, projectChoice: str = '') -> None:
    """
    Redraw sidebar: e.g. after change of project visibility in table

    Args:
      projectChoice (str): projectID on which to focus: '' string=draw default=none; 'redraw' implies redraw; id implies id
    """
    # 1. Empty/Clear the Layout
    clearLayout(self.projectListL)

    # 2. Update Project in comm if necessary
    if projectChoice not in ('', 'redraw'):
      self.comm.projectID = projectChoice

    # 3. Fill projectList with Items = ProjectCards
    projects = self.visibleProjects()
    if projects.empty:
      emptyWarning = Label('Create a Project by clicking on the "+"-button above.', 'h1',
                           style=f"color: {self.comm.palette.getThemeColor('foreground', 'disabled')};")
      emptyWarning.setWordWrap(True)
      self.projectListL.addWidget(emptyWarning)
    projects = projects.sort_values('name', axis=0).reset_index(drop=True)
    for i in range(projects.shape[0]):
      projectCard = ProjectCard(self.comm, projects.iloc[i, :])
      if projectCard.project['id'] == self.comm.projectID:
        projectCard.highlight()
      self.projectListL.addWidget(projectCard)


  def paintHiddenProjectButton(self) -> None:
    """Update the visibility toggle's icon and tooltip."""
    iconName = 'fa5s.eye' if self.showHiddenProjects else 'fa5s.eye-slash'
    tooltip = 'Hide hidden projects' if self.showHiddenProjects else 'Show hidden projects'
    color = self.comm.palette.getThemeColor('primary', 'base')
    self.showHiddenBtn.setIcon(qta.icon(iconName, color=color))
    self.showHiddenBtn.setToolTip(tooltip)


  def execute(self, command: Command) -> None:
    """Handle commands emitted by the sidebar controls."""
    if command is Command.TOGGLE_HIDDEN_PROJECTS:
      self.showHiddenProjects = not self.showHiddenProjects
      self.showHiddenBtn.setChecked(self.showHiddenProjects)
      self.paintHiddenProjectButton()
      self.paint()
    elif command is Command.CREATE_PROJECT:
      self.comm.formDoc.emit({'type': ['x0'], '_projectID': self.comm.projectID})
      self.comm.changeTable.emit('x0', self.comm.projectID, '')
      self.comm.changeSidebar.emit('redraw')


  def visibleProjects(self) -> pd.DataFrame:
    """Return projects allowed by the current sidebar visibility policy."""
    if self.showHiddenProjects or self.projects.empty:
      return self.projects
    isActive = self.projects['id'] == self.comm.projectID
    isHidden = self.projects['show'].str.contains('F')
    return self.projects[~isHidden | isActive]



  @Slot(str, str)
  def highlightActiveProject(self, projectID: str, docID: str) -> None:
    """
    Slot for changeProject-Signal
    Highlights the currently active project-card in the sidebar and lowlights every other
    Args:
      projectID (str): project ID of Project to highlight
      docID (str): document ID in Signal that is not used here
    """
    for i in range(self.projectListL.count()):
      layoutItem = self.projectListL.itemAt(i)
      item = layoutItem.widget() if layoutItem is not None else None
      if isinstance(item, ProjectCard):
        item.lowlight()
        if item.project['id'] == projectID:
          item.highlight()


class Command(Enum):
  """Commands handled by :class:`ProjectSidebar`."""
  TOGGLE_HIDDEN_PROJECTS = 1
  CREATE_PROJECT = 2
