""" Graphical user interface houses all widgets """
import json
import logging
import sys
import tempfile
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtCore import QEvent, QObject, Qt, QTimer, QUrl, Slot
from PySide6.QtGui import QDesktopServices, QIcon, QKeyEvent, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QLabel, QMainWindow, QMessageBox, QSplitter
from pasta_eln import __version__
from pasta_eln.backend_worker.worker import Task
from pasta_eln.configuration_file import saveConfiguration
from pasta_eln.fixed_strings_json import aboutMessage, shortcuts
from pasta_eln.misc_tools import hardRestart, installPythonPackages, updateAddOnList
from pasta_eln.ui.body.body import Body
from pasta_eln.ui.config.main import Configuration
from pasta_eln.ui.data_hierarchy.editor import SchemeEditor
from pasta_eln.ui.definitions.editor import Editor as DefinitionsEditor
from pasta_eln.ui.details.details import Command as DetailsCommand
from pasta_eln.ui.form.form import Form
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import action
from pasta_eln.ui.message_dialog import MessageDialog, showMessage
from pasta_eln.ui.palette import Palette
from pasta_eln.ui.repositories.upload_gui import UploadGUI
from pasta_eln.ui.sidebar.sidebar import ProjectSidebar


class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """

  def __init__(self, comm: Communicate) -> None:
    """ Init main window
    Args:
      comm (Communicate): communicate object to transfer information
    """
    # global setting
    super().__init__()
    self.comm = comm
    self.application = QApplication.instance()
    if self.comm.configuration:
      self.comm.palette = Palette(comm, self.comm.configuration['GUI']['theme'])
      self.comm.docTypesChanged.connect(self.paint)
    else:
      configWindow = Configuration(self.comm, 'setup')
      configWindow.exec()
      self.setCentralWidget(QLabel('ERROR: No configuration present!'))
      return
    self.comm.formDoc.connect(self.formDoc)
    self.comm.changeSidebar.connect(self.paint)
    self.comm.backendThread.worker.beSendTaskReport.connect(self.showReport)

    # GUI
    self.setWindowTitle(f"PASTA-ELN {__version__}")
    self.resize(self.screen().size())                                # self.setWindowState(Qt.WindowMaximized)
    # TODO https://bugreports.qt.io/browse/PYSIDE-2706 https://bugreports.qt.io/browse/QTBUG-124892
    resourcesDir = Path(__file__).parent / 'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir / 'Icons' / 'favicon64.png')))
    menu = self.menuBar()
    projectMenu = menu.addMenu('&Project')
    self.projectActions = [
        action('&Export project to .eln',   self, Command.EXPORT, projectMenu),
        action('&Import .eln into project', self, Command.IMPORT, projectMenu),
        action('&Upload to repository',     self, Command.REPOSITORY, projectMenu),
    ]
    projectMenu.addSeparator()
    self.projectActions.append(action('&Delete current project...', self, Command.DELETE_PROJECT, projectMenu))
    projectMenu.aboutToShow.connect(self.paintProjectActions)
    projectMenu.addSeparator()
    action('&Exit',                     self, Command.EXIT, projectMenu)

    self.viewMenu = menu.addMenu('Common &Lists')

    systemMenu = menu.addMenu('Project &group')
    self.changeProjectGroups = systemMenu.addMenu('&Change project group')
    syncMenu = systemMenu.addMenu('&Synchronize')
    action('Send all',                  self, Command.SYNC_SEND_ALL, syncMenu)
    action('Send',                      self, Command.SYNC_SEND, syncMenu, keySequence='F5')
    if 'develop' in self.comm.configuration:
      action('Get all',                 self, Command.SYNC_GET_ALL, syncMenu)
      action('Get',                     self, Command.SYNC_GET, syncMenu, keySequence='F4')
      action('Smart sync',              self, Command.SYNC_SMART, syncMenu)
    configureMenu = systemMenu.addMenu('&Configure')
    action('&Item type editor',         self, Command.SCHEMA, configureMenu, keySequence='F8')
    action('&Definitions editor',       self, Command.DEFINITIONS, configureMenu)
    addOnsMenu = systemMenu.addMenu('&Add-ons')
    action('Update add-on list',            self, Command.UPDATE, addOnsMenu)
    action('Test extraction from a file',   self, Command.TEST1, addOnsMenu)
    action('Test selected item extraction', self, Command.TEST_SELECTED, addOnsMenu, keySequence='F2')

    helpMenu = menu.addMenu('&Other')
    action('&Website',                  self, Command.WEBSITE, helpMenu)
    action('Shortcuts',                 self, Command.SHORTCUTS, helpMenu)
    action('About',                     self, Command.ABOUT, helpMenu)
    helpMenu.addSeparator()
    action('&Configuration',            self, Command.CONFIG, helpMenu, keySequence='Ctrl+0')
    developerMenu = helpMenu.addMenu('&Developer tools')
    action('Verify database',           self, Command.CHECK_DB, developerMenu, keySequence='Ctrl+?')
    action('Restart application',       self, Command.RESTART, developerMenu, keySequence='F9')
    action('Capture window screenshot', self, Command.SCREENSHOT, developerMenu, keySequence='F12')
    # F12 must remain available while a modal dialog (for example Form) is open.
    if self.application is not None:
      self.application.installEventFilter(self)

    # GUI elements
    self.splitter = QSplitter(handleWidth=3)
    self.setCentralWidget(self.splitter)                                # Set the central widget of the Window
    self.body = Body(self.comm)                                                        # body with information
    self.sidebar = ProjectSidebar(self.comm)                                            # sidebar with buttons
    self.splitter.addWidget(self.sidebar)
    self.splitter.addWidget(self.body)

    self.paint()
    def _resizeSplitter() -> None:
      """Restore the sidebar width from the GUI configuration."""
      sidebarWidth = self.comm.configuration['GUI']['sidebarWidth']
      self.splitter.setSizes([sidebarWidth, self.splitter.width() - sidebarWidth])
    QTimer.singleShot(0, _resizeSplitter)


  @Slot(str)
  def paint(self, _: str = '') -> None:
    """ Process things that might change """
    # Things that are inside the List menu
    self.viewMenu.clear()
    for key, value in self.comm.docTypesTitles.items():
      shortcutValue = value['shortcut'].strip()
      shortcut = None if shortcutValue == '' else f'Ctrl+{shortcutValue.upper()}'
      action(value['title'], self, [Command.VIEW, key], self.viewMenu, keySequence=shortcut)
    self.viewMenu.addSeparator()
    action('&Tags', self, [Command.VIEW, '_tags_'], self.viewMenu, keySequence='Ctrl+T')
    action('&Unidentified', self, [Command.VIEW, '-'], self.viewMenu, keySequence='Ctrl+U')
    # Things that are related to project group
    self.changeProjectGroups.clear()
    for name in self.comm.configuration['projectGroups'].keys():
      action(name, self, [Command.CHANGE_PG, name], self.changeProjectGroups)
    return


  def paintProjectActions(self) -> None:
    """Enable project-scoped menu actions only when a project is open."""
    for projectAction in self.projectActions:
      projectAction.setEnabled(bool(self.comm.projectID))


  def closeEvent(self, event: QEvent) -> None:
    """
    Handle window close event - cleanup of backend thread

    Args:
      event: close event
    """
    if self.application is not None:
      self.application.removeEventFilter(self)
    if self.comm and hasattr(self.comm, 'backendThread') and self.comm.backendThread:
      self.comm.shutdownBackendThread()
    event.accept()


  def eventFilter(self, watched: QObject, event: QEvent) -> bool:
    """Handle F12 even when a modal dialog owns the keyboard focus.
    Args:
      watched: object that was watched
      event: event
    Returns:
      bool: True if the event was handled, False otherwise
    """
    if (isinstance(event, QKeyEvent) and event.type() == QEvent.Type.KeyPress
        and event.key() == Qt.Key.Key_F12 and not event.isAutoRepeat()):
      self.execute(Command.SCREENSHOT)
      return True
    return super().eventFilter(watched, event)


  @Slot(dict)
  def formDoc(self, doc: dict[str, Any]) -> None:
    """
    What happens when new/edit dialog is shown

    Args:
      doc (dict): document
    """
    formWindow = Form(self.comm, doc)
    ret = formWindow.exec()
    if ret == 0:
      self.comm.stopSequentialEdit.emit()
    return


  def execute(self, command: Command | list[Any]) -> None:
    """Action after clicking menu item
    Args:
      command (Command | list[Any]): command to execute
    """
    # file menu
    commandType = command if isinstance(command, Command) else command[0]
    payload = [] if isinstance(command, Command) else command[1:]
    projectCommands = (Command.EXPORT, Command.IMPORT, Command.REPOSITORY, Command.DELETE_PROJECT)
    if commandType in projectCommands and not self.comm.projectID:
      logging.critical('Open a project before using this action.')
      return
    if commandType is Command.EXPORT:
      fileName = QFileDialog.getSaveFileName(self, 'Save project into .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '':
        docTypes = [i for i in self.comm.docTypesTitles if i[0] != 'x']
        self.comm.uiRequestTask.emit(Task.EXPORT_ELN,
                                     {'fileName': fileName, 'projID': self.comm.projectID, 'docTypes': docTypes})
    elif commandType is Command.IMPORT:
      fileName = QFileDialog.getOpenFileName(self, 'Load data from .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '':
        self.comm.uiRequestTask.emit(Task.IMPORT_ELN, {'fileName': fileName, 'projID': self.comm.projectID})
        self.comm.changeProject.emit(self.comm.projectID, '')
    elif commandType is Command.REPOSITORY:
      dialogR = UploadGUI(self.comm)
      dialogR.exec()
    elif commandType is Command.DELETE_PROJECT:
      confirmation = QMessageBox.critical(self, 'Critical', 'Do you want to delete the current project?',
          QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,  QMessageBox.StandardButton.No)
      if confirmation == QMessageBox.StandardButton.Yes:
        self.comm.uiRequestTask.emit(Task.DELETE_DOC, {'docID': self.comm.projectID, 'stack': self.comm.projectID})
        self.comm.changeTable.emit('x0', '')
        self.comm.changeSidebar.emit('redraw')
        self.comm.changeDetails.emit('')
    elif commandType is Command.EXIT:
      self.close()
    # view menu
    elif commandType is Command.VIEW:
      self.comm.projectID = ''
      self.comm.changeTable.emit(payload[0], '')
      self.comm.changeSidebar.emit('')
    # system menu
    elif commandType is Command.CHANGE_PG:
      self.comm.configuration['defaultProjectGroup'] = payload[0]
      saveConfiguration(self.comm.configuration)
      self.comm.projectGroup = payload[0]
      self.comm.start(payload[0])
    elif commandType is Command.SYNC_SEND_ALL:
      self.comm.uiRequestTask.emit(Task.SYNC_ELAB, {'projGroup': self.comm.projectGroup, 'subtask': 'sA'})
    elif commandType is Command.SYNC_SEND:
      self.comm.uiRequestTask.emit(Task.SYNC_ELAB, {'projGroup': self.comm.projectGroup, 'subtask': 's'})
    elif commandType is Command.SYNC_GET_ALL:
      self.comm.uiRequestTask.emit(Task.SYNC_ELAB, {'projGroup': self.comm.projectGroup, 'subtask': 'gA'})
    elif commandType is Command.SYNC_GET:
      self.comm.uiRequestTask.emit(Task.SYNC_ELAB, {'projGroup': self.comm.projectGroup, 'subtask': 'g'})
    elif commandType is Command.SYNC_SMART:
      self.comm.uiRequestTask.emit(Task.SYNC_ELAB, {'projGroup': self.comm.projectGroup, 'subtask': ''})
    elif commandType is Command.SCHEMA:
      dialogS = SchemeEditor(self.comm)
      dialogS.exec()
    elif commandType is Command.DEFINITIONS:
      DefinitionsEditor(self.comm).exec()
    elif commandType is Command.TEST1:
      fileName = QFileDialog.getOpenFileName(self, 'Open file for extractor test', str(Path.home()), '*.*')[0]
      if fileName is not None:
        self.comm.uiRequestTask.emit(Task.EXTRACTOR_TEST,
                                     {'fileName': fileName, 'style': 'html', 'recipe': '', 'saveFig': ''})
    elif commandType is Command.TEST_SELECTED:
      self.body.detailsW.execute(DetailsCommand.TEST_EXTRACTION)
    elif commandType is Command.UPDATE:
      configProjecGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
      installPythonPackages(configProjecGroup['addOnDir'])
      reportDict = updateAddOnList(self.comm.projectGroup)
      MessageDialog(self, 'Add-on list updated', {'main': reportDict}, minWidth=600,
                    style='QScrollArea{min-height:400px}').exec()
      hardRestart()
    elif commandType is Command.CONFIG:
      dialogC = Configuration(self.comm)
      dialogC.exec()
    # remainder
    elif commandType is Command.WEBSITE:
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/')
    elif commandType is Command.CHECK_DB:
      self.comm.uiRequestTask.emit(Task.CHECK_DB, {'style': 'json'})
    elif commandType is Command.SHORTCUTS:
      showMessage(self, 'Keyboard shortcuts', shortcuts, 'Information')
    elif commandType is Command.ABOUT:
      showMessage(self, 'About', f'{aboutMessage}Environment: {sys.prefix}\n', 'Information')
    elif commandType is Command.RESTART:
      hardRestart()
    elif commandType is Command.SCREENSHOT:
      screenshotPath = Path(tempfile.gettempdir()) / 'pasta-eln-current-window.png'
      if self.grab().save(str(screenshotPath), 'PNG'):
        showMessage(self, 'Screenshot saved', f'Window screenshot saved to:\n{screenshotPath}', 'Information')
      else:
        logging.error('Could not save UI screenshot to %s', screenshotPath)
    else:
      logging.error('Gui menu unknown: %s', command, exc_info=True)
    return


  @Slot(Task, str, str, str)
  def showReport(self, task: Task, reportText: str, image: str, path: str) -> None:
    """ Show a report from backend worker
    Args:
      task (Task): task name
      reportText (str): text of the report
      image (str): base64 encoded image, svg image
      path (str): path to the file/folder that should be opened
    """
    if task is Task.OPEN_EXTERNAL and path:
      QDesktopServices.openUrl(QUrl.fromLocalFile(path))
      return
    if task in (Task.SCAN, Task.DROP_EXTERNAL):
      self.comm.changeProject.emit(self.comm.projectID, '')
    elif task is Task.CHECK_DB:
      MessageDialog(self, 'Database verification', json.loads(reportText),
                    style='QScrollArea { min-height: 400px; }').exec()
      return
    elif task not in (Task.EXTRACTOR_TEST, Task.EXTRACTOR_RERUN, Task.DELETE_DOC, Task.EXPORT_ELN, Task.IMPORT_ELN,
                      Task.SYNC_ELAB):                              # e.g. extractor tests work out of the box
      logging.error('Unknown task in showReport: %s', task, exc_info=True)
    showMessage(self, 'Report', reportText, image=image)


class Command(Enum):
  """ Commands used in this file """
  EXPORT = 1
  IMPORT = 2
  EXIT = 3
  VIEW = 4
  CHANGE_PG = 6
  SYNC_SEND = 7
  SYNC_GET = 8
  SYNC_SMART = 9
  SCHEMA = 10
  TEST1 = 11
  TEST_SELECTED = 23
  UPDATE = 13
  CONFIG = 14
  WEBSITE = 15
  CHECK_DB = 16
  SHORTCUTS = 17
  RESTART = 18
  SCREENSHOT = 19
  ABOUT = 20
  DEFINITIONS = 21
  REPOSITORY = 22
  SYNC_SEND_ALL = 24
  SYNC_GET_ALL = 25
  DELETE_PROJECT = 26
