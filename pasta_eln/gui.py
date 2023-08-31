""" Graphical user interface includes all widgets """
import os, logging, webbrowser, json, sys
from enum import Enum
from typing import Any, Optional
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QScrollArea # pylint: disable=no-name-in-module
from PySide6.QtCore import Qt, Slot      # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut  # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from pasta_eln import __version__
from .backend import Backend
from .guiCommunicate import Communicate
from .GUI.sidebar import Sidebar
from .GUI.body import Body
from .GUI.form import Form
from .GUI.config import Configuration
from .GUI.projectGroup import ProjectGroup
from .GUI.ontology import Ontology
from .miscTools import updateExtractorList, restart
from .guiStyle import Action, showMessage, widgetAndLayout, shortCuts
from .fixedStringsJson import shortcuts
from .inputOutput import exportELN, importELN
os.environ['QT_API'] = 'pyside6'

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """
  def __init__(self) -> None:
    #global setting
    super().__init__()
    venv = ' without venv' if sys.prefix == sys.base_prefix and 'CONDA_PREFIX' not in os.environ else ' in venv'
    self.setWindowTitle(f"PASTA-ELN {__version__}{venv}")
    self.setWindowState(Qt.WindowMaximized) # type: ignore
    resourcesDir = Path(__file__).parent/'Resources'
    self.setWindowIcon(QIcon(QPixmap(resourcesDir/'Icons'/'favicon64.png')))
    self.backend = Backend()
    self.comm = Communicate(self.backend)
    self.comm.formDoc.connect(self.formDoc)

    #Menubar
    menu = self.menuBar()
    projectMenu = menu.addMenu("&Project")
    Action('&Export .eln',          self, [Command.EXPORT], projectMenu)
    Action('&Import .eln',          self, [Command.IMPORT], projectMenu)
    projectMenu.addSeparator()
    Action('&Exit',                 self, [Command.EXIT],   projectMenu)

    viewMenu = menu.addMenu("&Lists")
    if hasattr(self.backend, 'db'):
      for docType, docLabel in self.comm.backend.db.dataLabels.items():
        if docType[0]=='x' and docType[1]!='0':
          continue
        shortcut = f"Ctrl+{shortCuts[docType]}" if docType in shortCuts else None
        Action(docLabel,            self, [Command.VIEW, docType], viewMenu, shortcut=shortcut)
        if docType=='x0':
          viewMenu.addSeparator()
      viewMenu.addSeparator()
      Action('&Tags',               self, [Command.VIEW, '_tags_'], viewMenu, shortcut='Ctrl+T')
      Action('&Unidentified',       self, [Command.VIEW, '-'],      viewMenu, shortcut='Ctrl+U')

    systemMenu = menu.addMenu("&System")
    Action('&Project groups',       self, [Command.PROJECT_GROUP],    systemMenu)
    changeProjectGroups = systemMenu.addMenu("&Change project group")
    if hasattr(self.backend, 'configuration'):                       #not case in fresh install
      for name in self.backend.configuration['projectGroups'].keys():
        Action(name,                self, [Command.CHANGE_PG, name], changeProjectGroups)
    Action('&Syncronize',           self, [Command.SYNC],            systemMenu, shortcut='F5')
    Action('&Questionaires',        self, [Command.ONTOLOGY],        systemMenu)
    systemMenu.addSeparator()
    Action('&Test extraction from a file',   self, [Command.TEST1],  systemMenu)
    Action('Test &selected item extraction', self, [Command.TEST2],  systemMenu, shortcut='F2')
    Action('Update &Extractor list',         self, [Command.UPDATE], systemMenu)
    systemMenu.addSeparator()
    Action('&Configuration',         self, [Command.CONFIG],         systemMenu, shortcut='Ctrl+0')

    helpMenu = menu.addMenu("&Help")
    Action('&Website',               self, [Command.WEBSITE],        helpMenu)
    Action('&Verify database',       self, [Command.VERIFY_DB],      helpMenu, shortcut='Ctrl+?')
    Action('Shortcuts',              self, [Command.SHORTCUTS],      helpMenu)
    helpMenu.addSeparator()
    #shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda : self.execute([Command.RESTART]))

    #GUI elements
    mainWidget, mainLayout = widgetAndLayout('H')
    self.setCentralWidget(mainWidget)      # Set the central widget of the Window
    body = Body(self.comm)        #body with information
    self.sidebar = Sidebar(self.comm)  #sidebar with buttons
    # sidebarScroll = QScrollArea()
    # sidebarScroll.setWidget(self.sidebar)
    # if hasattr(self.comm.backend, 'configuration'):
    #   sidebarScroll.setFixedWidth(self.comm.backend.configuration['GUI']['sidebarWidth']+10)
    # mainLayout.addWidget(sidebarScroll)
    mainLayout.addWidget(self.sidebar)
    mainLayout.addWidget(body)
    self.comm.changeTable.emit('x0','')


  @Slot(str)
  def formDoc(self, doc:dict[str,Any]) -> None:
    """
    What happens when new/edit dialog is shown

    Args:
      doc (dict): document
    """
    if '_id' in doc:
      logging.debug('gui:formdoc '+str(doc['_id']))
    elif '_ids' in doc:
      logging.debug('gui:formdoc '+str(doc['_ids']))
    else:
      logging.debug('gui:formdoc of type '+str(doc['-type']))
    formWindow = Form(self.comm, doc)
    ret = formWindow.exec()
    if ret==0:
      self.comm.stopSequentialEdit.emit()
    return


  def execute(self,  command:list[Any]) -> None:
    """
    action after clicking menu item
    """
    # file menu
    if command[0] is Command.EXPORT:
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to export', 'Warning')
        return
      fileName = QFileDialog.getSaveFileName(self,'Save data into .eln file',str(Path.home()),'*.eln')[0]
      status = exportELN(self.comm.backend, self.comm.projectID, fileName)
      showMessage(self, 'Finished', status, 'Information')
    elif command[0] is Command.IMPORT:
      fileName = QFileDialog.getOpenFileName(self,'Load data from .eln file',str(Path.home()),'*.eln')[0]
      status = importELN(self.comm.backend, fileName)
      showMessage(self, 'Finished', status, 'Information')
      self.comm.changeSidebar.emit('redraw')
      self.comm.changeTable.emit('x0','')
    elif command[0] is Command.EXIT:
      self.close()
    #view menu
    elif command[0] is Command.VIEW:
      self.comm.changeTable.emit(command[1], '')
    #system menu
    elif command[0] is Command.PROJECT_GROUP:
      dialog = ProjectGroup(self.comm)
      dialog.exec()
    elif command[0] is Command.CHANGE_PG:
      self.backend.configuration['defaultProjectGroup'] = command[1]
      with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(self.backend.configuration,indent=2))
      restart()
    elif command[0] is Command.SYNC:
      report = self.comm.backend.replicateDB(progressBar=self.sidebar.progress)
      showMessage(self, 'Report of syncronization', report, style='QLabel {min-width: 450px}')
    elif command[0] is Command.ONTOLOGY:
      showMessage(self, 'To be implemented','A possibility to change the questionaires / change the ontology is missing.')
      # dialog = Ontology(self.comm.backend)
      # dialog.exec()
    elif command[0] is Command.TEST1:
      fileName = QFileDialog.getOpenFileName(self,'Open file for extractor test',str(Path.home()),'*.*')[0]
      report = self.comm.backend.testExtractor(fileName, outputStyle='html')
      showMessage(self, 'Report of extractor test', report)
    elif command[0] is Command.TEST2:
      self.comm.testExtractor.emit()
    elif command[0] is Command.UPDATE:
      report = updateExtractorList(self.backend.extractorPath)
      showMessage(self, 'Extractor list updated', report)
      restart()
    elif command[0] is Command.CONFIG:
      dialog = Configuration(self.comm)
      dialog.exec()
    #remainder
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
      print("**ERROR gui menu unknown:",command)
    return


##############
## Main function
def main() -> None:
  """ Main method and entry point for commands """
  # logging has to be started first
  logPath = Path.home()/'pastaELN.log'
  #  old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA GUI')
  # remainder
  app = QApplication()
  window = MainWindow()
  logging.getLogger().setLevel(getattr(logging, window.backend.configuration['GUI']['loggingLevel']))
  theme = window.backend.configuration['GUI']['theme']
  if theme!='none':
    apply_stylesheet(app, theme=f'{theme}.xml')
  # qtawesome and matplot cannot coexist
  import qtawesome as qta
  if not isinstance(qta.icon('fa5s.times'), QIcon):
    logging.error('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
    print('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
  # end test coexistance
  window.show()
  app.exec()
  logging.info('End PASTA GUI')
  return


class Command(Enum):
  """ Commands used in this file """
  EXPORT = 1
  IMPORT = 2
  EXIT   = 3
  VIEW   = 4
  PROJECT_GROUP = 5
  CHANGE_PG     = 6
  SYNC          = 7
  ONTOLOGY      = 8
  TEST1         = 9
  TEST2         = 10
  UPDATE        = 11
  CONFIG        = 12
  WEBSITE       = 13
  VERIFY_DB     = 14
  SHORTCUTS     = 15
  RESTART       = 16


# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  main()
