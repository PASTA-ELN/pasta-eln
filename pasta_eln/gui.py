""" Graphical user interface includes all widgets """
import json
import logging
import os
import sys
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any, Union
from PySide6.QtCore import QCoreApplication, Slot  # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow  # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  # of https://github.com/UN-GCPDS/qt-material
from pasta_eln import __version__
from pasta_eln.GUI.dataverse.config_dialog import ConfigDialog
from pasta_eln.GUI.dataverse.main_dialog import MainDialog
from .backend import Backend
from .elabFTWsync import Pasta2Elab
from .fixedStringsJson import CONF_FILE_NAME, shortcuts
# from pasta_eln.GUI.dataverse.config_dialog import ConfigDialog
# from pasta_eln.GUI.dataverse.main_dialog import MainDialog
from .GUI.body import Body
from .GUI.config import Configuration
from .GUI.form import Form
from .GUI.palette import Palette
from .GUI.sidebar import Sidebar
from .guiCommunicate import Communicate
from .guiStyle import Action, ScrollMessageBox, showMessage, widgetAndLayout
from .inputOutput import exportELN, importELN
from .miscTools import restart, updateAddOnList

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
    venv = ' without venv' if sys.prefix == sys.base_prefix and 'CONDA_PREFIX' not in os.environ else ' in venv'
    self.setWindowTitle(f"PASTA-ELN {__version__}{venv}")
    self.resize(self.screen().size()) #self.setWindowState(Qt.WindowMaximized) #TODO https://bugreports.qt.io/browse/PYSIDE-2706 https://bugreports.qt.io/browse/QTBUG-124892
    resourcesDir = Path(__file__).parent / 'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir / 'Icons' / 'favicon64.png')))
    self.backend = Backend(defaultProjectGroup=projectGroup)
    theme = self.backend.configuration['GUI']['theme']
    palette      = Palette(self, theme)
    self.comm = Communicate(self.backend, palette)
    self.comm.formDoc.connect(self.formDoc)
    self.dataverseMainDialog: MainDialog | None = None
    self.dataverseConfig: ConfigDialog | None = None

    # Menubar
    menu = self.menuBar()
    projectMenu = menu.addMenu('&Project')
    Action('&Export project to .eln',        self, [Command.EXPORT],         projectMenu)
    if 'develop' in self.comm.backend.configuration:
      Action('&Import .eln into project',      self, [Command.IMPORT],         projectMenu)
    # Action('&Upload to Dataverse',           self, [Command.DATAVERSE_MAIN], projectMenu)
    Action('&Exit',                          self, [Command.EXIT],           projectMenu)

    viewMenu = menu.addMenu('&Lists')
    if hasattr(self.backend, 'db'):
      for docType, docLabel in self.comm.backend.db.dataHierarchy('', 'title'):
        if docType[0] == 'x' and docType[1] != '0':
          continue
        shortcut = self.comm.backend.db.dataHierarchy(docType,'shortcut')[0]
        shortcut = None if shortcut=='' else f"Ctrl+{shortcut}"
        Action(docLabel,                     self, [Command.VIEW, docType],  viewMenu, shortcut=shortcut)
        if docType == 'x0':
          viewMenu.addSeparator()
      viewMenu.addSeparator()
      Action('&Tags',                        self, [Command.VIEW, '_tags_'], viewMenu, shortcut='Ctrl+T')
      Action('&Unidentified',                self, [Command.VIEW, '-'],      viewMenu, shortcut='Ctrl+U')

    systemMenu = menu.addMenu('Project &group')
    changeProjectGroups = systemMenu.addMenu('&Change project group')
    if hasattr(self.backend, 'configuration'):                            # not case in fresh install
      for name in self.backend.configuration['projectGroups'].keys():
        Action(name,                         self, [Command.CHANGE_PG, name], changeProjectGroups)
    if 'develop' in self.comm.backend.configuration:
      syncMenu = systemMenu.addMenu('&Synchronize')
      Action('Send',                         self, [Command.SYNC_SEND],       syncMenu, shortcut='F5')
      # Action('Get',                          self, [Command.SYNC_GET],       syncMenu)
      # Action('Smart synce',                  self, [Command.SYNC_SMART],       syncMenu)
      Action('&Editor to change data type schema', self, [Command.SCHEMA],   systemMenu, shortcut='F8')
    systemMenu.addSeparator()
    Action('&Test extraction from a file',   self, [Command.TEST1],           systemMenu)
    Action('Test &selected item extraction', self, [Command.TEST2],           systemMenu, shortcut='F2')
    Action('Update &Add-on list',            self, [Command.UPDATE],          systemMenu)
    systemMenu.addSeparator()
    Action('&Verify database',               self, [Command.VERIFY_DB],       systemMenu, shortcut='Ctrl+?')

    helpMenu = menu.addMenu('&Help')
    Action('&Website',                       self, [Command.WEBSITE],         helpMenu)
    Action('Shortcuts',                      self, [Command.SHORTCUTS],       helpMenu)
    systemMenu.addSeparator()
    Action('&Configuration',                 self, [Command.CONFIG],          helpMenu, shortcut='Ctrl+0')
    # Action('&Dataverse Configuration',       self, [Command.DATAVERSE_CONFIG],helpMenu, shortcut='F10')

    # shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda: self.execute([Command.RESTART]))

    # GUI elements
    mainWidget, mainLayout = widgetAndLayout('H')
    self.setCentralWidget(mainWidget)  # Set the central widget of the Window
    body = Body(self.comm)  # body with information
    self.sidebar = Sidebar(self.comm)  # sidebar with buttons
    # sidebarScroll = QScrollArea()
    # sidebarScroll.setWidget(self.sidebar)
    # if hasattr(self.comm.backend, 'configuration'):
    #   sidebarScroll.setFixedWidth(self.comm.backend.configuration['GUI']['sidebarWidth']+10)
    # mainLayout.addWidget(sidebarScroll)
    mainLayout.addWidget(self.sidebar)
    mainLayout.addWidget(body)
    self.comm.changeTable.emit('x0', '')


  @Slot(dict)                                         # type: ignore[arg-type]
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
      sync = Pasta2Elab(self.backend, self.backend.configurationProjectGroup)
      if hasattr(sync, 'api'):  #if hostname and api-key given
        sync.sync('sA')
      else:                     #if not given
        showMessage(self, 'ERROR', 'Please give server address and API-key in Configuration')
        dialogC = Configuration(self.comm)
        dialogC.exec()
    elif command[0] is Command.SYNC_GET:
      sync = Pasta2Elab(self.backend)
      sync.sync('gA')
    elif command[0] is Command.SYNC_SMART:
      sync = Pasta2Elab(self.backend)
      sync.sync('')
    elif command[0] is Command.SCHEMA:
      pass
      # dataHierarchyForm = DataHierarchyEditorDialog()
      # dataHierarchyForm.instance.exec()
    # elif command[0] is Command.DATAVERSE_CONFIG:
    #   self.dataverseConfig = ConfigDialog()
    #   self.dataverseConfig.show()
    # elif command[0] is Command.DATAVERSE_MAIN:
    #   self.dataverseMainDialog = MainDialog(self.comm.backend)
    #   self.dataverseMainDialog.show()
    elif command[0] is Command.TEST1:
      fileName = QFileDialog.getOpenFileName(self, 'Open file for extractor test', str(Path.home()), '*.*')[0]
      report = self.comm.backend.testExtractor(fileName, outputStyle='html')
      showMessage(self, 'Report of extractor test', report)
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
      report = self.comm.backend.checkDB(outputStyle='html', minimal=True)
      showMessage(self, 'Report of database verification', report, style='QLabel {min-width: 800px}')
    elif command[0] is Command.SHORTCUTS:
      showMessage(self, 'Keyboard shortcuts', shortcuts)
    elif command[0] is Command.RESTART:
      restart()
    else:
      print('**ERROR gui menu unknown:', command)
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
  theme = main_window.backend.configuration['GUI']['theme']
  if theme != 'none':
    apply_stylesheet(application, theme=f'{theme}.xml')
  import qtawesome as qta  # qtawesome and matplot cannot coexist
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
