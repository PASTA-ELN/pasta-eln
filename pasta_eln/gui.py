""" Graphical user interface includes all widgets """
import json
import logging
import os
import sys
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any, Union

from PySide6.QtCore import Qt, Slot, QCoreApplication  # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox  # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  # of https://github.com/UN-GCPDS/qt-material

from pasta_eln import __version__
from pasta_eln.GUI.dataverse.config_dialog import ConfigDialog
from pasta_eln.GUI.dataverse.main_dialog import MainDialog
from .GUI.body import Body
from .GUI.config import Configuration
from .GUI.form import Form
from .GUI.projectGroup import ProjectGroup
from .GUI.sidebar import Sidebar
from .backend import Backend
from .fixedStringsJson import shortcuts
from .guiCommunicate import Communicate
from .guiStyle import Action, showMessage, widgetAndLayout, ScrollMessageBox
from .inputOutput import exportELN, importELN
from .GUI.data_hierarchy.data_hierarchy_editor_dialog import DataHierarchyEditorDialog
from .miscTools import updateExtractorList, restart

os.environ['QT_API'] = 'pyside6'


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """

  def __init__(self) -> None:
    # global setting
    super().__init__()
    venv = ' without venv' if sys.prefix == sys.base_prefix and 'CONDA_PREFIX' not in os.environ else ' in venv'
    self.setWindowTitle(f"PASTA-ELN {__version__}{venv}")
    self.setWindowState(Qt.WindowMaximized)  # type: ignore
    resourcesDir = Path(__file__).parent / 'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir / 'Icons' / 'favicon64.png')))
    self.backend = Backend()
    self.comm = Communicate(self.backend)
    self.comm.formDoc.connect(self.formDoc)
    self.dataverseMainDialog: MainDialog | None = None
    self.dataverseConfig: ConfigDialog | None = None

    # Menubar
    menu = self.menuBar()
    projectMenu = menu.addMenu("&Project")
    Action('&Export project to .eln',        self, [Command.EXPORT],         projectMenu)
    Action('&Import .eln',                   self, [Command.IMPORT],         projectMenu, shortcut='Ctrl+A')
    projectMenu.addSeparator()
    Action('&Export all projects to .eln',   self, [Command.EXPORT_ALL],     projectMenu)
    Action('&Exit',                          self, [Command.EXIT],           projectMenu)

    viewMenu = menu.addMenu("&Lists")
    if hasattr(self.backend, 'db'):
      for docType, docLabel in self.comm.backend.db.dataLabels.items():
        if docType[0] == 'x' and docType[1] != '0':
          continue
        shortcut = self.comm.backend.db.dataHierarchy[docType].get('shortcut','')
        shortcut = None if shortcut=='' else f"Ctrl+{shortcut}"
        Action(docLabel,                     self, [Command.VIEW, docType],  viewMenu, shortcut=shortcut)
        if docType == 'x0':
          viewMenu.addSeparator()
      viewMenu.addSeparator()
      Action('&Tags',                        self, [Command.VIEW, '_tags_'], viewMenu, shortcut='Ctrl+T')
      Action('&Unidentified',                self, [Command.VIEW, '-'],      viewMenu, shortcut='Ctrl+U')

    systemMenu = menu.addMenu("&System")
    Action('&Project groups',                self, [Command.PROJECT_GROUP],   systemMenu)
    changeProjectGroups = systemMenu.addMenu("&Change project group")
    if hasattr(self.backend, 'configuration'):                            # not case in fresh install
      for name in self.backend.configuration['projectGroups'].keys():
        Action(name,                         self, [Command.CHANGE_PG, name], changeProjectGroups)
    Action('&Synchronize',                   self, [Command.SYNC],            systemMenu, shortcut='F5')
    Action('&Data hierarchy editor',         self, [Command.DATAHIERARCHY],        systemMenu, shortcut='F8')
    Action('&Dataverse Configuration',         self, [Command.DATAVERSE_CONFIG],        systemMenu, shortcut='F10')
    Action('&Upload to Dataverse',         self, [Command.DATAVERSE_MAIN],        systemMenu, shortcut='F11')
    systemMenu.addSeparator()
    Action('&Test extraction from a file',   self, [Command.TEST1],           systemMenu)
    Action('Test &selected item extraction', self, [Command.TEST2],           systemMenu, shortcut='F2')
    Action('Update &Extractor list',         self, [Command.UPDATE],          systemMenu)
    systemMenu.addSeparator()
    Action('&Configuration',                 self, [Command.CONFIG],          systemMenu, shortcut='Ctrl+0')

    helpMenu = menu.addMenu("&Help")
    Action('&Website',                       self, [Command.WEBSITE],         helpMenu)
    Action('&Verify database',               self, [Command.VERIFY_DB],       helpMenu, shortcut='Ctrl+?')
    Action('Shortcuts',                      self, [Command.SHORTCUTS],       helpMenu)
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


  @Slot(str)
  def formDoc(self, doc: dict[str, Any]) -> None:
    """
    What happens when new/edit dialog is shown

    Args:
      doc (dict): document
    """
    if '_id' in doc:
      logging.debug('gui:formdoc ' + str(doc['_id']))
    elif '_ids' in doc:
      logging.debug('gui:formdoc ' + str(doc['_ids']))
    else:
      logging.debug('gui:formdoc of type ' + str(doc['-type']))
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
      if fileName != '':
        status = exportELN(self.comm.backend, [self.comm.projectID], fileName)
        showMessage(self, 'Finished', status, 'Information')
    elif command[0] is Command.EXPORT_ALL:
      fileName = QFileDialog.getSaveFileName(self, 'Save everything to .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '':
        allProjects = [i['id'] for i in self.comm.backend.db.getView('viewDocType/x0')]
        print(allProjects)
        status = exportELN(self.comm.backend, allProjects, fileName)
        showMessage(self, 'Finished', status, 'Information')
    elif command[0] is Command.IMPORT:
      fileName = QFileDialog.getOpenFileName(self, 'Load data from .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '':
        status = importELN(self.comm.backend, fileName)
        showMessage(self, 'Finished', status, 'Information')
        self.comm.changeSidebar.emit('redraw')
        self.comm.changeTable.emit('x0', '')
    elif command[0] is Command.EXIT:
      self.close()
    # view menu
    elif command[0] is Command.VIEW:
      self.comm.changeTable.emit(command[1], '')
    # system menu
    elif command[0] is Command.PROJECT_GROUP:
      dialog = ProjectGroup(self.comm)
      dialog.exec()
    elif command[0] is Command.CHANGE_PG:
      self.backend.configuration['defaultProjectGroup'] = command[1]
      with open(Path.home() / '.pastaELN.json', 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.backend.configuration, indent=2))
      restart()
    elif command[0] is Command.SYNC:
      report = self.comm.backend.replicateDB(progressBar=self.sidebar.progress)
      showMessage(self, 'Report of syncronization', report, style='QLabel {min-width: 450px}')
    elif command[0] is Command.DATAHIERARCHY:
      dataHierarchyForm = DataHierarchyEditorDialog(self.comm.backend.db)
      dataHierarchyForm.instance.exec()
      restart()
    elif command[0] is Command.DATAVERSE_CONFIG:
      self.dataverseConfig = ConfigDialog()
      self.dataverseConfig.show()
    elif command[0] is Command.DATAVERSE_MAIN:
      self.dataverseMainDialog = MainDialog(self.comm.backend)
      self.dataverseMainDialog.show()
    elif command[0] is Command.TEST1:
      fileName = QFileDialog.getOpenFileName(self, 'Open file for extractor test', str(Path.home()), '*.*')[0]
      report = self.comm.backend.testExtractor(fileName, outputStyle='html')
      showMessage(self, 'Report of extractor test', report)
    elif command[0] is Command.TEST2:
      self.comm.testExtractor.emit()
    elif command[0] is Command.UPDATE:
      reportDict = updateExtractorList(self.backend.extractorPath)
      messageWindow = ScrollMessageBox('Extractor list updated', reportDict,
                                       style='QScrollArea{min-width:600 px; min-height:400px}')
      messageWindow.exec()
      restart()
    elif command[0] is Command.CONFIG:
      dialog = Configuration(self.comm)
      dialog.exec()
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
      print("**ERROR gui menu unknown:", command)
    return


def mainGUI() -> tuple[Union[QCoreApplication, None], MainWindow]:
  """
    Main method and entry point for commands

  Returns:
    MainWindow: main window
  """
  # logging has to be started first
  log_path = Path.home() / 'pastaELN.log'
  #  old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA GUI')
  # remainder
  if not QApplication.instance():
    application = QApplication().instance()
  else:
    application = QApplication.instance()
  main_window = MainWindow()
  logging.getLogger().setLevel(getattr(logging, main_window.backend.configuration['GUI']['loggingLevel']))
  theme = main_window.backend.configuration['GUI']['theme']
  if theme != 'none':
    apply_stylesheet(application, theme=f'{theme}.xml')
  # qtawesome and matplot cannot coexist
  import qtawesome as qta
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
  PROJECT_GROUP = 5
  CHANGE_PG = 6
  SYNC      = 7
  DATAHIERARCHY = 8
  TEST1     = 9
  TEST2     = 10
  UPDATE    = 11
  CONFIG    = 12
  WEBSITE   = 13
  VERIFY_DB = 14
  SHORTCUTS = 15
  RESTART   = 16
  EXPORT_ALL= 17
  DATAVERSE_CONFIG = 18
  DATAVERSE_MAIN = 19


def startMain() -> None:
  """
  Main function to start GUI. Extra function is required to allow starting in module fashion
  """
  app, window = mainGUI()
  window.show()
  if app:
    app.exec()


# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  startMain()
