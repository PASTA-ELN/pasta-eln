"""
Central widget: The big toplevel Widget on the righthand side of the sidebar:
Manages the TabBar to switch between Project-Tree-View and DocType-Tables
"""
import qtawesome
from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSplitter, QTabWidget, QVBoxLayout, QWidget
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.project.project import Project
from pasta_eln.ui.details.details import Details
from pasta_eln.ui.table.table import TableView
from pasta_eln.ui.body.tabBar import ProjectTabBar


class Body(QWidget):
  """
  Central widget: The big toplevel Widget on the righthand side of the sidebar:
  Manages the TabBar to switch between Project-Tree-View and DocType-Tables
  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm

    # Tabwidget (Contains Project- and Table-views)
    self.tabWidget = QTabWidget()
    self.projectTabBar = ProjectTabBar(self.comm.palette.getThemeColor('foreground', 'base'))
    self.tabWidget.setTabBar(self.projectTabBar)
    self.tabWidget.setContentsMargins(0, 0, 0, 0)
    self.tabWidget.setMovable(True)
    borderColor = self.comm.palette.getThemeColor('border', 'base')
    self.tabWidget.setStyleSheet(f"""
    QTabWidget::pane {{
      border: none;
      border-top: 1px solid {borderColor};
      margin: 0px;
    }}
    """)
    # tabMenuButton for actions like add new tab # Simple-GUI
    # self.tabMenuButton = QPushButton()
    # self.tabMenuButton.setIcon(qtawesome.icon('ri.menu-fill'))
    # self.tabWidget.setCornerWidget(self.tabMenuButton)

    # Details-Widget (right sidebar, displaying the details of a single entry)
    self.detailsWidget = Details(self.comm)

    # Splitter (for Tabwidget and Details)
    self.splitter = QSplitter(handleWidth=3)
    self.splitter.addWidget(self.tabWidget)
    self.splitter.setStretchFactor(0, 3)
    self.splitter.addWidget(self.detailsWidget)
    self.splitter.setStretchFactor(1, 1)

    # Layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.setContentsMargins(0, 0, 0, 0)
    self.mainLayout.addWidget(self.splitter)
    self.setLayout(self.mainLayout)

    # Signals
    self.comm.docTypesChanged.connect(self.paint)
    self.comm.changeProject.connect(self.onChangeProject)
    self.tabWidget.currentChanged.connect(self.onTabChanged)
    self.detailsWidget.becameVisible.connect(self.resizeDetailsSplitter)

  @Slot()
  def resizeDetailsSplitter(self) -> None:
    """Set the details sidebar to the configured width after it becomes visible."""
    detailsWidth = int(self.comm.configuration['GUI']['detailsWidth'])
    self.splitter.setSizes([self.splitter.width() - detailsWidth, detailsWidth])

  def createTabIcon(self, iconName: str, color: str, selectedColor: str) -> QIcon:
    """Create a tab icon with distinct selected and unselected render states."""
    unselectedIcon = qtawesome.icon(iconName, color=color)
    selectedIcon = qtawesome.icon(iconName, color=selectedColor)
    tabIcon = QIcon()
    iconSize = QSize(64, 64)
    for mode in (QIcon.Mode.Normal, QIcon.Mode.Active, QIcon.Mode.Selected):
      tabIcon.addPixmap(unselectedIcon.pixmap(iconSize, mode), mode, QIcon.State.Off)
      tabIcon.addPixmap(selectedIcon.pixmap(iconSize, mode), mode, QIcon.State.On)
    return tabIcon


  @Slot()
  def paint(self) -> None:
    """
    Create the changable things in the Widget.
    """
    iconColor = self.comm.palette.getThemeColor('foreground', 'base')
    selectedIconColor = self.comm.palette.getThemeColor('primary', 'base')
    # Add Project View - Tab
    projectView = Project(self.comm)
    homeIndex = self.tabWidget.addTab(projectView,
                                      self.createTabIcon('ri.home-2-fill', iconColor, selectedIconColor), 'Home')
    self.projectTabBar.markHomeTab(homeIndex)
    # Add Table Views - Tabs
    for doctype, docTypeDetails in self.comm.docTypesTitles.items():
      if doctype[0] == 'x' or '/' in doctype:
        continue
      tableView = TableView(self.comm, doctype)
      icon = 'ri.asterisk' if docTypeDetails['icon'] == '' else docTypeDetails['icon']
      icon = self.createTabIcon(icon, iconColor, selectedIconColor)
      label = docTypeDetails['title']
      self.tabWidget.addTab(tableView, icon, label)


  @Slot(str, str)
  def onChangeProject(self, docID: str, projectID: str) -> None:
    """
    What happens when the currently chosen project is changed.
    Args:
      docID: from Signal: Which doc should be shown.
      projectID: from Signal: Which Project it was changed to.
    """
    # When changing a Project, the Project-View should be shown.
    self.tabWidget.setCurrentIndex(0)


  @Slot(int)
  def onTabChanged(self, index: int) -> None:
    """

    Args:
      index: index of the now active tab after change.
    """
    widget = self.tabWidget.widget(index)
    if isinstance(widget, TableView):
      docType = widget.docType
      self.comm.changeTable.emit(docType, '')
