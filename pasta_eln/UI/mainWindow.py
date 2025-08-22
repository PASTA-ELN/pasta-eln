""" Graphical user interface houses all widgets """
import json
import logging
import re
import sys
import webbrowser
from enum import Enum
from pathlib import Path
from typing import Any
from PySide6.QtCore import QEvent, QUrl, Slot
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap, QShortcut
from PySide6.QtWidgets import QFileDialog, QLabel, QMainWindow
from pasta_eln import __version__
from ..backendWorker.worker import Task
from ..fixedStringsJson import CONF_FILE_NAME, AboutMessage, shortcuts
from ..miscTools import hardRestart, installPythonPackages, updateAddOnList
from .body import Body
from .config.main import Configuration
from .data_hierarchy.editor import SchemeEditor
from .definitions.editor import Editor as DefinitionsEditor
from .form import Form
from .guiCommunicate import Communicate
from .guiStyle import Action, ScrollMessageBox, widgetAndLayout
from .messageDialog import showMessage
from .palette import Palette
from .repositories.uploadGUI import UploadGUI
from .sidebar import Sidebar


class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """

  def __init__(self, comm:Communicate) -> None:
    """ Init main window
    Args:
      projectGroup (str): project group to load
    """
    # global setting
    super().__init__()
    self.comm = comm
    if self.comm.configuration:
      self.comm.palette = Palette(self, self.comm.configuration['GUI']['theme'])
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
    self.resize(self.screen().size())                                 #self.setWindowState(Qt.WindowMaximized)
    #TODO https://bugreports.qt.io/browse/PYSIDE-2706 https://bugreports.qt.io/browse/QTBUG-124892
    resourcesDir = Path(__file__).parent / 'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir / 'Icons' / 'favicon64.png')))
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
    Action('&Item type editor',              self, [Command.SCHEMA],      systemMenu, shortcut='F8')
    Action('&Definitions editor',            self, [Command.DEFINITIONS],     systemMenu)
    systemMenu.addSeparator()
    Action('&Test extraction from a file',   self, [Command.TEST1],           systemMenu)
    Action('Test &selected item extraction', self, [Command.TEST2],           systemMenu, shortcut='F2')
    Action('Update &Add-on list',            self, [Command.UPDATE],          systemMenu)
    if 'develop' in self.comm.configuration:
      systemMenu.addSeparator()
      Action('&Verify database',             self, [Command.CHECK_DB],       systemMenu, shortcut='Ctrl+?')

    helpMenu = menu.addMenu('&Help')
    Action('&Website',                       self, [Command.WEBSITE],         helpMenu)
    Action('Shortcuts',                      self, [Command.SHORTCUTS],       helpMenu)
    Action('About',                          self, [Command.ABOUT],           helpMenu)
    systemMenu.addSeparator()
    Action('&Configuration',                 self, [Command.CONFIG],          helpMenu, shortcut='Ctrl+0')

    # shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda: self.execute([Command.RESTART]))
    if 'develop' not in self.comm.configuration:
      QShortcut('Ctrl+?', self, lambda: self.execute([Command.CHECK_DB]))

    # GUI elements
    mainWidget, mainLayout = widgetAndLayout('H')
    self.setCentralWidget(mainWidget)                                   # Set the central widget of the Window
    body = Body(self.comm)                                                             # body with information
    self.sidebar = Sidebar(self.comm)                                                   # sidebar with buttons
    mainLayout.addWidget(self.sidebar)
    mainLayout.addWidget(body)
    self.paint()
    self.comm.changeTable.emit('x0', '')                                 # show project table, without details


  @Slot(str)
  def paint(self, _:str='') -> None:
    """ Process things that might change """
    # Things that are inside the List menu
    self.viewMenu.clear()
    for key, value in self.comm.docTypesTitles.items():
      shortcut = None if value['shortcut']=='' else f"Ctrl+{value['shortcut']}"
      Action(value['title'],            self, [Command.VIEW, key],  self.viewMenu, shortcut=shortcut)
    self.viewMenu.addSeparator()
    Action('&Tags',               self, [Command.VIEW, '_tags_'], self.viewMenu, shortcut='Ctrl+T')
    Action('&Unidentified',       self, [Command.VIEW, '-'],      self.viewMenu, shortcut='Ctrl+U')
    # Things that are related to project group
    self.changeProjectGroups.clear()
    for name in self.comm.configuration['projectGroups'].keys():
      Action(name,                         self, [Command.CHANGE_PG, name], self.changeProjectGroups)
    return


  def closeEvent(self, event:QEvent) -> None:
    """
    Handle window close event - cleanup of backend thread

    Args:
      event: close event
    """
    if self.comm and hasattr(self.comm, 'backendThread') and self.comm.backendThread:
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
      if fileName != '':
        docTypes = [i for i in self.comm.docTypesTitles if i[0]!='x']
        self.comm.uiRequestTask.emit(Task.EXPORT_ELN, {'fileName':fileName, 'projID':self.comm.projectID, 'docTypes':docTypes})
    elif command[0] is Command.IMPORT:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to import', 'Critical')
        return
      fileName = QFileDialog.getOpenFileName(self, 'Load data from .eln file', str(Path.home()), '*.eln')[0]
      if fileName != '':
        self.comm.uiRequestTask.emit(Task.IMPORT_ELN, {'fileName':fileName, 'projID':self.comm.projectID})
        self.comm.changeProject.emit(self.comm.projectID, '')
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
      self.comm.configuration['defaultProjectGroup'] = command[1]
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.comm.configuration, indent=2))
      self.comm.commSendConfiguration.emit(self.comm.configuration, command[1])
    elif command[0] is Command.SYNC_SEND:
      self.comm.uiRequestTask.emit(Task.SEND_ELAB,  {'projGroup':self.comm.projectGroup})
    elif command[0] is Command.SYNC_GET:
      self.comm.uiRequestTask.emit(Task.GET_ELAB,   {'projGroup':self.comm.projectGroup})
    elif command[0] is Command.SYNC_SMART:
      self.comm.uiRequestTask.emit(Task.SMART_ELAB, {'projGroup':self.comm.projectGroup})
    elif command[0] is Command.SCHEMA:
      dialogS = SchemeEditor(self.comm)
      dialogS.exec()
    elif command[0] is Command.DEFINITIONS:
      dialogD = DefinitionsEditor(self.comm)
      dialogD.show()
    elif command[0] is Command.TEST1:
      fileName = QFileDialog.getOpenFileName(self, 'Open file for extractor test', str(Path.home()), '*.*')[0]
      if fileName is not None:
        self.comm.uiRequestTask.emit(Task.EXTRACTOR_TEST, {'fileName':fileName, 'style':'html', 'recipe':'', 'saveFig':''})
    elif command[0] is Command.TEST2:
      self.comm.testExtractor.emit()
    elif command[0] is Command.UPDATE:
      configProjecGroup = self.comm.configuration['projectGroups'][self.comm.projectGroup]
      installPythonPackages(configProjecGroup['addOnDir'])
      reportDict = updateAddOnList(self.comm.projectGroup)
      messageWindow = ScrollMessageBox('Add-on list updated', reportDict,
                                       style='QScrollArea{min-width:600 px; min-height:400px}')
      messageWindow.exec()
      hardRestart()
    elif command[0] is Command.CONFIG:
      dialogC = Configuration(self.comm)
      dialogC.exec()
    # remainder
    elif command[0] is Command.WEBSITE:
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/')
    elif command[0] is Command.CHECK_DB:
      self.comm.uiRequestTask.emit(Task.CHECK_DB, {'style':'html'})
    elif command[0] is Command.SHORTCUTS:
      showMessage(self, 'Keyboard shortcuts', shortcuts, 'Information')
    elif command[0] is Command.ABOUT:
      showMessage(self, 'About', f'{AboutMessage}Environment: {sys.prefix}\n','Information')
    elif command[0] is Command.RESTART:
      hardRestart()
    else:
      logging.error('Gui menu unknown: %s', command, exc_info=True)
    return


  @Slot(Task, str, str, str)
  def showReport(self, task:Task, reportText:str, image:str, path:str) -> None:
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
      regexStr = r'<font color="magenta">image does not exist m-[0-9a-f]+ image: comment:<\/font><br>'
      myCount = len(re.findall(regexStr, reportText))
      if myCount>5:
        reportText = re.sub(regexStr, '', reportText, count=myCount-5)
        reportText += r'<font color="magenta">image does not exist ...:<\/font><br>'
    elif task not in (Task.EXTRACTOR_TEST, Task.EXTRACTOR_RERUN, Task.DELETE_DOC, Task.EXPORT_ELN, Task.IMPORT_ELN, Task.SEND_ELAB,
                      Task.GET_ELAB, Task.SMART_ELAB):               #e.g. extractor tests work out of the box
      logging.error('Unknown task in showReport: %s', task, exc_info=True)
    showMessage(self, 'Report', reportText, image=image)


class Command(Enum):
  """ Commands used in this file """
  EXPORT     = 1
  IMPORT     = 2
  EXIT       = 3
  VIEW       = 4
  CHANGE_PG  = 6
  SYNC_SEND  = 7
  SYNC_GET   = 8
  SYNC_SMART = 9
  SCHEMA     = 10
  TEST1      = 11
  TEST2      = 12
  UPDATE     = 13
  CONFIG     = 14
  WEBSITE    = 15
  CHECK_DB   = 16
  SHORTCUTS  = 17
  RESTART    = 18
  ABOUT      = 19
  DEFINITIONS= 20
  REPOSITORY = 21
