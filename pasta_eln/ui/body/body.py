"""
Central widget: The big toplevel Widget on the righthand side of the sidebar:
Manages the TabBar to switch between Project-Tree-View and DocType-Tables
"""
import qtawesome
from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSplitter, QTabWidget, QVBoxLayout, QWidget
from pasta_eln.ui.body.tabBar import ProjectTabBar
from pasta_eln.ui.details.details import Details
from pasta_eln.ui.details.context import DetailContext
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.project.project import Project
from pasta_eln.ui.table.table import TableView


class Body(QWidget):
  """
  Central widget: The big toplevel Widget on the righthand side of the sidebar:
  Manages the TabBar to switch between Project-Tree-View and DocType-Tables
  """

  def __init__(self, comm: Communicate):
    """Initialize the main body widget with its communication object.

    Args:
      comm (Communicate): Shared object used to exchange UI and backend requests.
    """
    super().__init__()
    self.comm = comm
    self._tableChangingInProgress = False

    # Tabwidget (Contains Project- and Table-views)
    self.tabWidget = QTabWidget()
    self.projectTabBar = ProjectTabBar(self.comm.palette.getThemeColor('foreground', 'base'))
    self.tabWidget.setTabBar(self.projectTabBar)
    self.tabWidget.setMovable(True)
    self.tabWidget.setContentsMargins(0, 0, 0, 0)
    self.tabWidget.setStyleSheet(f"""
    QTabWidget::pane {{
      border: none;
      border-top: 1px solid {self.comm.palette.getThemeColor('border', 'base')};
      margin: 0px;
    }}
    """)
    # Splitter (for Tabwidget and Details)
    self.detailsW = Details(self.comm)     # Details (right sidebar, displaying the details of a single entry)
    self.splitter = QSplitter(handleWidth=3)
    self.splitter.addWidget(self.tabWidget)
    self.splitter.setStretchFactor(0, 3)
    self.splitter.addWidget(self.detailsW)
    self.splitter.setStretchFactor(1, 1)

    # Layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.setContentsMargins(0, 0, 0, 0)
    self.mainLayout.addWidget(self.splitter)
    self.setLayout(self.mainLayout)

    # Signals
    self.comm.docTypesChanged.connect(self.paint)
    self.comm.changeProject.connect(self.onChangeProject)
    self.comm.changeTable.connect(self.onChangeTable)
    self.tabWidget.currentChanged.connect(self.onTabChanged)
    self.detailsW.becameVisible.connect(self.resizeDetailsSplitter)


  @Slot()
  def paint(self) -> None:
    """
    Create the changable things in the Widget.
    """
    iconColor         = self.comm.palette.getThemeColor('foreground', 'base')
    selectedIconColor = self.comm.palette.getThemeColor('primary', 'base')
    # Add Project View - Tab
    projectView = Project(self.comm)
    homeIndex = self.tabWidget.addTab(projectView,
                                      self.createIcon('ri.home-2-fill', iconColor, selectedIconColor), 'Home')
    self.projectTabBar.markHomeTab(homeIndex)
    # Add Table Views - Tabs
    for doctype, docTypeDetails in self.comm.docTypesTitles.items():
      if doctype[0] == 'x' or '/' in doctype:
        continue
      tableView = TableView(self.comm, doctype)
      iconName = 'ri.asterisk' if docTypeDetails['icon'] == '' else docTypeDetails['icon']
      icon     = self.createIcon(iconName, iconColor, selectedIconColor)
      label    = docTypeDetails['title']
      self.tabWidget.addTab(tableView, icon, label)
    for docType, iconName, label in (('_tags_', 'ri.price-tag-3-line', 'Tags'),
                                     ('-', 'ri.question-line', 'Unidentified')):
      tableView = TableView(self.comm, docType)
      icon = self.createIcon(iconName, iconColor, selectedIconColor)
      self.tabWidget.addTab(tableView, icon, label)


  def createIcon(self, iconName: str, color: str, selectedColor: str) -> QIcon:
    """Create a tab icon with distinct selected and unselected render states

    Args:
      iconName (str): name of the icon to create
      color (str): color of the icon
      selectedColor (str): color of the icon when selected

    Returns:
      QIcon: the created icon
    """
    tabIcon = QIcon()
    unselectedIcon = qtawesome.icon(iconName, color=color)
    selectedIcon   = qtawesome.icon(iconName, color=selectedColor)
    for mode in (QIcon.Mode.Normal, QIcon.Mode.Active, QIcon.Mode.Selected):
      tabIcon.addPixmap(unselectedIcon.pixmap(QSize(64, 64), mode), mode, QIcon.State.Off)
      tabIcon.addPixmap(selectedIcon.pixmap(QSize(64, 64), mode), mode, QIcon.State.On)
    return tabIcon


  @Slot()
  def resizeDetailsSplitter(self) -> None:
    """Set the details sidebar to the configured width after it becomes visible."""
    detailsWidth = int(self.comm.configuration['GUI']['detailsWidth'])
    self.splitter.setSizes([self.splitter.width() - detailsWidth, detailsWidth])


  @Slot(str, str)
  def onChangeProject(self, docID: str, projectID: str) -> None:
    """What happens when the currently chosen project is changed

    Args:
      docID: from Signal: Which doc should be shown.
      projectID: from Signal: Which Project it was changed to.
    """
    self.comm.changeDetails.emit(DetailContext())                                              # close details
    self.tabWidget.setCurrentIndex(0)


  @Slot(str, str, str)
  def onChangeTable(self, docType: str, _projectID: str, docID: str) -> None:
    """Select the table tab targeted by a table-change request."""
    if docType == 'x0':                         # to return to Home after large changes: e.g. project creation
      self.tabWidget.setCurrentIndex(0)
      return
    for index in range(self.tabWidget.count()):
      widget = self.tabWidget.widget(index)
      if isinstance(widget, TableView) and widget.docType == docType:
        self._tableChangingInProgress = True
        self.tabWidget.setCurrentIndex(index)
        self._tableChangingInProgress = False
        return


  @Slot(int)
  def onTabChanged(self, index: int) -> None:
    """What happens when tab is changed -> new table

    Args:
      index: index of the now active tab after change.
    """
    if self._tableChangingInProgress:
      return
    widget = self.tabWidget.widget(index)
    if isinstance(widget, Project):
      self.comm.changeDetails.emit(DetailContext())                                            # close details
    elif isinstance(widget, TableView):
      docType = widget.docType
      self.comm.changeTable.emit(docType, '', '')
