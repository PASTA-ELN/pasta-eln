""" Graphical user interface includes all widgets """
import json
import logging
import os
import sys
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any, Union
from PySide6.QtCore import QCoreApplication, Slot                          # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut                        # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox# pylint: disable=no-name-in-module
from pasta_eln import __version__
from .backend import Backend
from .elabFTWsync import Pasta2Elab
from .fixedStringsJson import CONF_FILE_NAME, AboutMessage, shortcuts
from .GUI.body import Body
from .GUI.config import Configuration
from .GUI.data_hierarchy.editor import SchemeEditor
from .GUI.definitions.editor import Editor as DefinitionsEditor
from .GUI.form import Form
from .GUI.palette import Palette
from .GUI.repositories.uploadGUI import UploadGUI
from .GUI.sidebar import Sidebar
from .guiCommunicate import Communicate
from .guiStyle import Action, ScrollMessageBox, showMessage, widgetAndLayout
from .inputOutput import exportELN, importELN
from .miscTools import restart, testNewPastaVersion, updateAddOnList

os.environ['QT_API'] = 'pyside6'


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """


  def __init__(self, projectGroup:str='') -> None:
    """ Init main window

    Args:
      projectGroup (str): project group to load
    """
    # global setting
    super().__init__()
    self.setWindowTitle(f"PASTA-ELN {__version__}")
    self.resize(self.screen().size())                                 #self.setWindowState(Qt.WindowMaximized)
    #TODO https://bugreports.qt.io/browse/PYSIDE-2706 https://bugreports.qt.io/browse/QTBUG-124892
    resourcesDir = Path(__file__).parent / 'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir / 'Icons' / 'favicon64.png')))
    self.backend = Backend(defaultProjectGroup=projectGroup)
    theme = self.backend.configuration['GUI']['theme']
    palette      = Palette(self, theme)
    self.comm = Communicate(self.backend, palette)
    self.comm.formDoc.connect(self.formDoc)
    self.comm.restart.connect(self.initialize)

    # Menubar
    menu = self.menuBar()
    projectMenu = menu.addMenu('&Project')
    Action('&Export project to .eln',        self, [Command.EXPORT],         projectMenu)
    if 'develop' in self.comm.backend.configuration:
      Action('&Import .eln into project',    self, [Command.IMPORT],         projectMenu)
      Action('&Upload to repository',        self, [Command.REPOSITORY], projectMenu)
    Action('&Exit',                          self, [Command.EXIT],           projectMenu)

    self.viewMenu = menu.addMenu('&Lists')

    systemMenu = menu.addMenu('Project &group')
    self.changeProjectGroups = systemMenu.addMenu('&Change project group')
    syncMenu = systemMenu.addMenu('&Synchronize')
    Action('Send',                         self, [Command.SYNC_SEND],       syncMenu, shortcut='F5')
    if 'develop' in self.comm.backend.configuration:
      Action('Get',                          self, [Command.SYNC_GET],        syncMenu, shortcut='F4')
      # Action('Smart synce',                  self, [Command.SYNC_SMART],       syncMenu)
    Action('&Editor to change data type schema', self, [Command.SCHEMA],      systemMenu, shortcut='F8')
    Action('&Definitions editor',          self, [Command.DEFINITIONS],     systemMenu)
    systemMenu.addSeparator()
    Action('&Test extraction from a file',   self, [Command.TEST1],           systemMenu)
    Action('Test &selected item extraction', self, [Command.TEST2],           systemMenu, shortcut='F2')
    Action('Update &Add-on list',            self, [Command.UPDATE],          systemMenu)
    if 'develop' in self.comm.backend.configuration:
      systemMenu.addSeparator()
      Action('&Verify database',             self, [Command.VERIFY_DB],       systemMenu, shortcut='Ctrl+?')

    helpMenu = menu.addMenu('&Help')
    Action('&Website',                       self, [Command.WEBSITE],         helpMenu)
    Action('Shortcuts',                      self, [Command.SHORTCUTS],       helpMenu)
    Action('About',                          self, [Command.ABOUT],           helpMenu)
    systemMenu.addSeparator()
    Action('&Configuration',                 self, [Command.CONFIG],          helpMenu, shortcut='Ctrl+0')

    # shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda: self.execute([Command.RESTART]))
    if 'develop' not in self.comm.backend.configuration:
      QShortcut('Ctrl+?', self, lambda: self.execute([Command.VERIFY_DB]))

    # GUI elements
    mainWidget, mainLayout = widgetAndLayout('H')
    self.setCentralWidget(mainWidget)                                   # Set the central widget of the Window
    try:
      body = Body(self.comm)                                                           # body with information
      self.sidebar = Sidebar(self.comm)                                                 # sidebar with buttons
      mainLayout.addWidget(self.sidebar)
      mainLayout.addWidget(body)
      # tests that run at start-up
      if self.backend.configuration['GUI']['checkForUpdates']=='Yes' and not testNewPastaVersion(False):
        button = QMessageBox.question(self, 'Update?', 'There is a new version of PASTA-ELN available. Do you want to update?',
                                      QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if button == QMessageBox.StandardButton.Yes:
          testNewPastaVersion(update=True)
      # initialize things that might change
      self.initialize()
    except Exception as e:
      logging.error('Error in GUI initialization %s', e)


  @Slot()
  def initialize(self) -> None:
    """ Initialize: things that might change """
    self.comm.backend.initialize(self.backend.configurationProjectGroup)                      #restart backend
    # Things that are inside the List menu
    self.viewMenu.clear()
    if hasattr(self.backend, 'db'):
      for docType, docLabel in self.comm.backend.db.dataHierarchy('', 'title'):
        shortcut = self.comm.backend.db.dataHierarchy(docType,'shortcut')[0]
        shortcut = None if shortcut=='' else f"Ctrl+{shortcut}"
        Action(docLabel,            self, [Command.VIEW, docType],  self.viewMenu, shortcut=shortcut)
      self.viewMenu.addSeparator()
      Action('&Tags',               self, [Command.VIEW, '_tags_'], self.viewMenu, shortcut='Ctrl+T')
      Action('&Unidentified',       self, [Command.VIEW, '-'],      self.viewMenu, shortcut='Ctrl+U')
    # Things that are related to project group
    self.changeProjectGroups.clear()
    if hasattr(self.backend, 'configuration'):                                     # not case in fresh install
      for name in self.backend.configuration['projectGroups'].keys():
        Action(name,                         self, [Command.CHANGE_PG, name], self.changeProjectGroups)
    self.comm.changeTable.emit('x0', '')
    return


  @Slot(dict)                                                                         # type: ignore[arg-type]
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


  def execute(self, command: list[Any]) -> None:
    """
    action after clicking menu item
    """
    # file menu
    if command[0] is Command.EXPORT:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to export', 'Warning')
        return
      fileName = QFileDialog.getSaveFileName(self, 'Save project into .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '' and hasattr(self.backend, 'db'):
        docTypes = [i for i in self.comm.backend.db.dataHierarchy('','') if i[0]!='x']
        status = exportELN(self.comm.backend, [self.comm.projectID], fileName, docTypes)
        showMessage(self, 'Finished', status, 'Information')
    elif command[0] is Command.IMPORT:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to import', 'Warning')
        return
      fileName = QFileDialog.getOpenFileName(self, 'Load data from .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '':
        status, statistics  = importELN(self.comm.backend, fileName, self.comm.projectID)
        showMessage(self, 'Finished', f'{status}\n{statistics}', 'Information')
        self.comm.changeSidebar.emit('redraw')
        self.comm.changeTable.emit('x0', '')
    elif command[0] is Command.REPOSITORY:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to upload', 'Warning')
        return
      dialogR = UploadGUI(self.comm)
      dialogR.exec()
    elif command[0] is Command.EXIT:
      self.close()
    # view menu
    elif command[0] is Command.VIEW:
      self.comm.changeTable.emit(command[1], '')
    # system menu
    elif command[0] is Command.CHANGE_PG:
      self.backend.configuration['defaultProjectGroup'] = command[1]
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.backend.configuration, indent=2))
      restart()
    elif command[0] is Command.SYNC_SEND:
      if 'ERROR' in self.backend.checkDB(minimal=True):
        showMessage(self, 'ERROR', 'There are errors in your database: fix before upload')
        return
      sync = Pasta2Elab(self.backend, self.backend.configurationProjectGroup)
      if hasattr(sync, 'api') and sync.api.url:                                 #if hostname and api-key given
        self.comm.progressWindow(lambda func1: sync.sync('sA', progressCallback=func1))
      else:                                                                                      #if not given
        showMessage(self, 'ERROR', 'Please give server address and API-key in Configuration')
        dialogC = Configuration(self.comm)
        dialogC.exec()
    elif command[0] is Command.SYNC_GET:
      sync = Pasta2Elab(self.backend, self.backend.configurationProjectGroup)
      self.comm.progressWindow(lambda func1: sync.sync('gA', progressCallback=func1))
      self.comm.changeSidebar.emit('redraw')
      self.comm.changeTable.emit('x0', '')
    elif command[0] is Command.SYNC_SMART:
      sync = Pasta2Elab(self.backend)
      sync.sync('')
    elif command[0] is Command.SCHEMA:
      dialogS = SchemeEditor(self.comm)
      dialogS.exec()
    elif command[0] is Command.DEFINITIONS:
      dialogD = DefinitionsEditor(self.comm)
      dialogD.show()
    # elif command[0] is Command.DATAVERSE_CONFIG:
    #   self.dataverseConfig = ConfigDialog()
    #   self.dataverseConfig.show()
    # elif command[0] is Command.DATAVERSE_MAIN:
    #   self.dataverseMainDialog = MainDialog(self.comm.backend)
    #   self.dataverseMainDialog.show()
    elif command[0] is Command.TEST1:
      fileName = QFileDialog.getOpenFileName(self, 'Open file for extractor test', str(Path.home()), '*.*')[0]
      reportText = self.comm.backend.testExtractor(fileName, outputStyle='html')
      showMessage(self, 'Report of extractor test', reportText)
    elif command[0] is Command.TEST2:
      self.comm.testExtractor.emit()
    elif command[0] is Command.UPDATE:
      reportDict = updateAddOnList(self.backend.configurationProjectGroup)
      messageWindow = ScrollMessageBox('Extractor list updated', reportDict,
                                       style='QScrollArea{min-width:600 px; min-height:400px}')
      messageWindow.exec()
      restart()
    elif command[0] is Command.CONFIG:
      dialogC = Configuration(self.comm)
      dialogC.exec()
    # remainder
    elif command[0] is Command.WEBSITE:
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/')
    elif command[0] is Command.VERIFY_DB:
      reportText = self.comm.backend.checkDB(outputStyle='html', minimal=True)
      showMessage(self, 'Report of database verification', reportText, style='QLabel {min-width: 800px}')
    elif command[0] is Command.SHORTCUTS:
      showMessage(self, 'Keyboard shortcuts', shortcuts)
    elif command[0] is Command.ABOUT:
      showMessage(self, 'About', f'{AboutMessage}Environment: {sys.prefix}\n', '')
    elif command[0] is Command.RESTART:
      restart()
    else:
      logging.error('Gui menu unknown: %s', command)
    return


def mainGUI(projectGroup:str='') -> tuple[Union[QCoreApplication, None], MainWindow]:
  """  Main method and entry point for commands

  Args:
      projectGroup (str): project group to load

  Returns:
    MainWindow: main window
  """
  # logging has to be started first
  log_path = Path.home() / 'pastaELN.log'
  #  old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib','pudb']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA GUI')
  # remainder
  if not QApplication.instance():
    application = QApplication().instance()
  else:
    application = QApplication.instance()
  main_window = MainWindow(projectGroup=projectGroup)
  logging.getLogger().setLevel(getattr(logging, main_window.backend.configuration['GUI']['loggingLevel']))
  main_window.comm.palette.setTheme(application)
  import qtawesome as qta                                               # qtawesome and matplot cannot coexist
  if not isinstance(qta.icon('fa5s.times'), QIcon):
    logging.error('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
    print('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
  # end test coexistence
  logging.info('End PASTA GUI')
  return application, main_window


class Command(Enum):
  """ Commands used in this file """
  EXPORT    = 1
  IMPORT    = 2
  EXIT      = 3
  VIEW      = 4
  CHANGE_PG = 6
  SYNC_SEND = 7
  SYNC_GET  = 8
  SYNC_SMART= 9
  SCHEMA    = 10
  TEST1     = 11
  TEST2     = 12
  UPDATE    = 13
  CONFIG    = 14
  WEBSITE   = 15
  VERIFY_DB = 16
  SHORTCUTS = 17
  RESTART   = 18
  ABOUT     = 19
  DEFINITIONS= 20
  REPOSITORY = 21


def startMain(projectGroup:str='') -> None:
  """
  Main function to start GUI. Extra function is required to allow starting in module fashion

  Args:
    projectGroup (str): project group to load
  """
  app, window = mainGUI(projectGroup=projectGroup)
  window.show()
  if app:
    app.exec()


# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  startMain()
