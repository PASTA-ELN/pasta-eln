""" Graphical user interface houses all widgets """
import json
import logging
import re
import sys
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtCore import Slot                                            # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut                        # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox        # pylint: disable=no-name-in-module
from pasta_eln import __version__
# from ..elabFTWsync import Pasta2Elab
from ..fixedStringsJson import CONF_FILE_NAME, AboutMessage, shortcuts
# from .body import Body
# from .config import Configuration
# from .data_hierarchy.editor import SchemeEditor
# from .definitions.editor import Editor as DefinitionsEditor
# from .form import Form
from .palette import Palette
# from .repositories.uploadGUI import UploadGUI
from .sidebar import Sidebar
from .guiStyle import Action, ScrollMessageBox, widgetAndLayout
from .messageDialog import showMessage
# from ..inputOutput import exportELN, importELN
from ..miscTools import hardRestart, testNewPastaVersion, updateAddOnList, installPythonPackages
from ..guiCommunicate import Communicate
from .config import Configuration

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """


  def __init__(self, comm:Communicate) -> None:
    """ Init main window

    Args:
      projectGroup (str): project group to load
    """
    # global setting
    super().__init__()
    self.docTypesTitlesIcons:dict[str,dict[str,str]] = {}  # docType: {'title': title, 'icon': icon, 'shortcut': shortcut}
    self.comm = comm
    if self.comm.configuration:
      self.comm.palette = Palette(self, self.comm.configuration['GUI']['theme'])
      self.comm.backendThread.worker.beSendDocTypes.connect(self.onGetDocTypes)
    else:
      configWindow = Configuration(self, 'setup')
      configWindow.exec()
      return


    self.comm.formDoc.connect(self.formDoc)
    self.comm.softRestart.connect(self.paint)

    # GUI
    self.setWindowTitle(f"PASTA-ELN {__version__}")
    self.resize(self.screen().size())                                 #self.setWindowState(Qt.WindowMaximized)
    #TODO https://bugreports.qt.io/browse/PYSIDE-2706 https://bugreports.qt.io/browse/QTBUG-124892
    resourcesDir = Path(__file__).parent / 'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir / 'Icons' / 'favicon64.png')))

    # Menubar
    menu = self.menuBar()
    projectMenu = menu.addMenu('&Project')
    Action('&Export project to .eln',        self, [Command.EXPORT],         projectMenu)
    if 'develop' in self.comm.configuration:
      Action('&Import .eln into project',    self, [Command.IMPORT],         projectMenu)
      Action('&Upload to repository',        self, [Command.REPOSITORY], projectMenu)
    Action('&Exit',                          self, [Command.EXIT],           projectMenu)

    self.viewMenu = menu.addMenu('&Lists')

    systemMenu = menu.addMenu('Project &group')
    self.changeProjectGroups = systemMenu.addMenu('&Change project group')
    syncMenu = systemMenu.addMenu('&Synchronize')
    Action('Send',                         self, [Command.SYNC_SEND],       syncMenu, shortcut='F5')
    if 'develop' in self.comm.configuration:
      Action('Get',                          self, [Command.SYNC_GET],        syncMenu, shortcut='F4')
      # Action('Smart synce',                  self, [Command.SYNC_SMART],       syncMenu)
    Action('&Editor to change data type schema', self, [Command.SCHEMA],      systemMenu, shortcut='F8')
    Action('&Definitions editor',          self, [Command.DEFINITIONS],     systemMenu)
    systemMenu.addSeparator()
    Action('&Test extraction from a file',   self, [Command.TEST1],           systemMenu)
    Action('Test &selected item extraction', self, [Command.TEST2],           systemMenu, shortcut='F2')
    Action('Update &Add-on list',            self, [Command.UPDATE],          systemMenu)
    if 'develop' in self.comm.configuration:
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
    if 'develop' not in self.comm.configuration:
      QShortcut('Ctrl+?', self, lambda: self.execute([Command.VERIFY_DB]))

    # GUI elements
    mainWidget, mainLayout = widgetAndLayout('H')
    self.setCentralWidget(mainWidget)                                   # Set the central widget of the Window
    try:
      #TODO body = Body(self.comm)                                                           # body with information
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


  @Slot(dict)
  def onGetDocTypes(self, data: dict[str, dict[str, str]]) -> None:
    """Handle data received from backend worker"""
    print(data)
    self.docTypesTitlesIcons = data
    self.paint()  # reinitialize to update menu items


  @Slot()
  def paint(self) -> None:
    """ Process things that might change """
    # Things that are inside the List menu
    self.viewMenu.clear()
    for key, value in self.docTypesTitlesIcons.items():
      shortcut = None if value['shortcut']=='' else f"Ctrl+{value['shortcut']}"
      Action(value['title'],            self, [Command.VIEW, key],  self.viewMenu, shortcut=shortcut)
    self.viewMenu.addSeparator()
    Action('&Tags',               self, [Command.VIEW, '_tags_'], self.viewMenu, shortcut='Ctrl+T')
    Action('&Unidentified',       self, [Command.VIEW, '-'],      self.viewMenu, shortcut='Ctrl+U')
    # Things that are related to project group
    self.changeProjectGroups.clear()
    for name in self.comm.configuration['projectGroups'].keys():
      Action(name,                         self, [Command.CHANGE_PG, name], self.changeProjectGroups)
    self.comm.changeTable.emit('x0', '')
    return


  def closeEvent(self, event) -> None:
    """
    Handle window close event - cleanup of backend thread

    Args:
      event: close event
    """
    if self.comm and self.comm.backendThread:
      self.comm.shutdownBackendThread()
    event.accept()


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


  def execute(self, command: list[Any]) -> None:
    """
    action after clicking menu item
    """
    # file menu
    if command[0] is Command.EXPORT:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to export', 'Critical')
        return
      fileName = QFileDialog.getSaveFileName(self, 'Save project into .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '' and hasattr(self.backend, 'db'):
        docTypes = [i for i in self.comm.backend.db.dataHierarchy('','') if i[0]!='x']
        status = exportELN(self.comm.backend, [self.comm.projectID], fileName, docTypes)
        showMessage(self, 'Finished', status, 'Information')
    elif command[0] is Command.IMPORT:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to import', 'Critical')
        return
      fileName = QFileDialog.getOpenFileName(self, 'Load data from .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '':
        status, statistics  = importELN(self.comm.backend, fileName, self.comm.projectID)
        showMessage(self, 'Finished', f'{status}\n{statistics}', 'Information')
        self.comm.changeSidebar.emit('redraw')
        self.comm.changeTable.emit('x0', '')
    elif command[0] is Command.REPOSITORY:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to upload', 'Critical')
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
      hardRestart()
    elif command[0] is Command.SYNC_SEND:
      if 'ERROR' in self.backend.checkDB(minimal=True):
        showMessage(self, 'Error', 'There are errors in your database: fix before upload', 'Critical')
        return
      sync = Pasta2Elab(self.backend, self.backend.configurationProjectGroup)
      if hasattr(sync, 'api') and sync.api.url:                                 #if hostname and api-key given
        self.comm.progressWindow(lambda func1: sync.sync('sA', progressCallback=func1))
      else:                                                                                      #if not given
        showMessage(self, 'Error', 'Please give server address and API-key in Configuration', 'Critical')
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
    elif command[0] is Command.TEST1:
      fileName = QFileDialog.getOpenFileName(self, 'Open file for extractor test', str(Path.home()), '*.*')[0]
      reportText, image = self.comm.backend.testExtractor(fileName, outputStyle='html')
      showMessage(self, 'Report of extractor test', reportText, image=image)
    elif command[0] is Command.TEST2:
      self.comm.testExtractor.emit()
    elif command[0] is Command.UPDATE:
      configProjecGroup = self.backend.configuration['projectGroups'][self.backend.configurationProjectGroup]
      installPythonPackages(configProjecGroup['addOnDir'])
      reportDict = updateAddOnList(self.backend.configurationProjectGroup)
      messageWindow = ScrollMessageBox('Extractor list updated', reportDict,
                                       style='QScrollArea{min-width:600 px; min-height:400px}')
      messageWindow.exec()
      hardRestart()
    elif command[0] is Command.CONFIG:
      dialogC = Configuration(self.comm)
      dialogC.exec()
    # remainder
    elif command[0] is Command.WEBSITE:
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/')
    elif command[0] is Command.VERIFY_DB:
      reportText = self.comm.backend.checkDB(outputStyle='html', minimal=True)
      regexStr = r'<font color="magenta">image does not exist m-[0-9a-f]+ image: comment:<\/font><br>'
      myCount = len(re.findall(regexStr, reportText))
      if myCount>5:
        reportText = re.sub(regexStr, '', reportText, count=myCount-5)
        reportText += '<font color="magenta">image does not exist ...:<\/font><br>'
      showMessage(self, 'Report of database verification', reportText, minWidth=800)
    elif command[0] is Command.SHORTCUTS:
      showMessage(self, 'Keyboard shortcuts', shortcuts, 'Information')
    elif command[0] is Command.ABOUT:
      showMessage(self, 'About', f'{AboutMessage}Environment: {sys.prefix}\n','Information')
    elif command[0] is Command.RESTART:
      hardRestart()
    else:
      logging.error('Gui menu unknown: %s', command)
    return


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
