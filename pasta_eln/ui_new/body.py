"""
Central widget: The big toplevel Widget on the righthand side of the sidebar:
Manages the TabBar to switch between Project-Tree-View and DocType-Tables
"""
import qtawesome
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QPushButton, QSizePolicy, QSplitter, QStackedWidget, QTabWidget

from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Label
from pasta_eln.ui.project import Project
from pasta_eln.ui_new.details.details import Details
from pasta_eln.ui_new.table_view.table_view import TableView


class Body(QStackedWidget):
  """
  Central widget: The big toplevel Widget on the righthand side of the sidebar:
  Manages the TabBar to switch between Project-Tree-View and DocType-Tables
  """

  def __init__(self, comm: Communicate):
    super().__init__()
    self.comm = comm

    self.comm.docTypesChanged.connect(self.paint)
    self.comm.changeProject.connect(self.onChangeProject)

    ### STACK #0
    # Start Page (Before a project is chosen)
    color = self.comm.palette.getThemeColor("foreground", "disabled")
    self.startPage = Label("Please Select a Project on the left.", 'h1', style=f"color: {color};")
    self.startPage.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.startPage.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.addWidget(self.startPage)

    ### STACK #1
    # Tabwidget (Contains Project- and Table-views)
    self.tabWidget = QTabWidget()
    self.tabWidget.setContentsMargins(0, 0, 0, 0)
    self.tabWidget.setMovable(True)
    borderColor = self.comm.palette.getThemeColor("border", "base")
    self.tabWidget.setStyleSheet(f"""
    QTabWidget::pane {{
      border: none;
      border-top: 1px solid {borderColor};
      margin: 0px;
    }}
    """)
    # tabMenuButton for actions like add new tab
    self.tabMenuButton = QPushButton()
    self.tabMenuButton.setIcon(qtawesome.icon("ri.menu-fill"))
    self.tabWidget.setCornerWidget(self.tabMenuButton)

    # Details-Widget (right sidebar, displaying the details of a single entry)
    self.detailsWidget = Details(self.comm)

    # Splitter (for Tabwidget and Details)
    self.splitter = QSplitter(handleWidth=3)
    self.splitter.addWidget(self.tabWidget)
    self.splitter.setStretchFactor(0, 3)
    self.splitter.addWidget(self.detailsWidget)
    self.splitter.setStretchFactor(1, 1)
    self.addWidget(self.splitter)
    ###

    # Style

    # Signals
    self.tabWidget.currentChanged.connect(self.onTabChanged)

    # CODE
    self.setCurrentIndex(0)

  @Slot()
  def paint(self) -> None:
    """
    Create the changable things in the Widget.
    """
    # Add Project View - Tab
    projectView = Project(self.comm)
    self.tabWidget.addTab(projectView, qtawesome.icon("ri.home-2-line"), "Home")
    # Add Table Views - Tabs
    for doctype, docTypeDetails in self.comm.docTypesTitles.items():
      if doctype[0] == 'x' or '/' in doctype:
        continue
      tableView = TableView(self.comm, doctype)
      icon = 'ri.asterisk' if docTypeDetails['icon'] == '' else docTypeDetails["icon"]
      icon = qtawesome.icon(icon)
      label = docTypeDetails["title"]
      self.tabWidget.addTab(tableView, icon, label)

  @Slot(str, str)
  def onChangeProject(self, docID: str, projectID: str) -> None:
    """
    What happens when the currently chosen project is changed.
    Args:
      docID: from Signal: Which doc should be shown.
      projectID: from Signal: Which Project it was changed to.
    """
    # Show the TabWidget, instead of startPage
    self.setCurrentIndex(1)
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
