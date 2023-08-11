""" Graphical user interface includes all widgets """
import os, logging, webbrowser, json, sys
from typing import Any, Optional, Tuple
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
    Action('&Export .eln',          self.executeAction, projectMenu, self, name='export')
    Action('&Import .eln',          self.executeAction, projectMenu, self, name='import')
    projectMenu.addSeparator()
    Action('&Exit',                 self.executeAction, projectMenu, self, name='exit')

    viewMenu = menu.addMenu("&Lists")
    if hasattr(self.backend, 'db'):
      for docType, docLabel in self.comm.backend.db.dataLabels.items():
        if docType[0]=='x' and docType[1]!='0':
          continue
        Action(
            docLabel,
            self.viewMenu,
            viewMenu,
            self,
            f"Ctrl+{shortCuts[docType]}" if docType in shortCuts else None,
            docType,
        )
        if docType=='x0':
          viewMenu.addSeparator()
      viewMenu.addSeparator()
      Action('&Tags',         self.viewMenu, viewMenu, self, 'Ctrl+T', '_tags_')
      Action('&Unidentified', self.viewMenu, viewMenu, self, 'Ctrl+U', name='-')
        #TODO_P5 create list of unaccessible files: linked with accessible files

    systemMenu = menu.addMenu("&System")
    Action('&Project groups',        self.executeAction, systemMenu, self, name='projectGroups')
    changeProjectGroups = systemMenu.addMenu("&Change project group")
    if hasattr(self.backend, 'configuration'):                       #not case in fresh install
      for name in self.backend.configuration['projectGroups'].keys():
        Action(name, self.changeProjectGroup, changeProjectGroups, self, name=name)
    Action('&Syncronize',            self.executeAction, systemMenu, self, name='sync', shortcut='F5')
    Action('&Questionaires',         self.executeAction, systemMenu, self, name='ontology')
    systemMenu.addSeparator()
    Action('&Test extraction from a file',   self.executeAction, systemMenu, self, name='extractorTest')
    Action('Test &selected item extraction', self.executeAction, systemMenu, self, name='extractorTest2',
           shortcut='F2')
    Action('Update &Extractor list',         self.executeAction, systemMenu, self, name='updateExtractors')
    systemMenu.addSeparator()
    Action('&Configuration',         self.executeAction, systemMenu, self, name='configuration', shortcut='Ctrl+0')

    helpMenu = menu.addMenu("&Help")
    Action('&Website',               self.executeAction, helpMenu, self, name='website')
    Action('&Verify database',       self.executeAction, helpMenu, self, name='verifyDB', shortcut='Ctrl+?')
    Action('Shortcuts',              self.executeAction, helpMenu, self, name='shortcuts')
    Action('Todo list',              self.executeAction, helpMenu, self, name='todo')
    helpMenu.addSeparator()
    #shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda : self.executeAction('restart'))
    #TODO_P3 -> lambda and change buttons/actions: cleaner code
    #  Action    ('Todo list',  self,  'todo',     helpMenu, 'Ctrl+H')
    #  Action    ('&Tags',      self,  '_tags_', viewMenu, 'Ctrl+T', call=self.viewMenu)
    #  TextButton('Add Filter', self,  'addFilter', headerL)

    #TODO_P3 export to dataverse
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


  def viewMenu(self) -> None:
    """
    act on user pressing an item in view
    """
    docType = self.sender().data()
    self.comm.changeTable.emit(docType, '')
    return


  def executeAction(self, menuName:Optional[str]=None) -> None:
    """
    action after clicking menu item
    """
    if menuName is None or not menuName :
      menuName = self.sender().data()
    if menuName=='configuration':
      dialog = Configuration(self.comm.backend)
      dialog.exec()
    elif menuName=='projectGroups':
      dialog = ProjectGroup(self.comm.backend)
      dialog.exec()
    elif menuName=='ontology':
      showMessage(self, 'To be implemented','A possibility to change the questionaires / change the ontology is missing.')
      # dialog = Ontology(self.comm.backend)
      # dialog.exec()
    elif menuName=='updateExtractors':
      report = updateExtractorList(self.backend.extractorPath)
      showMessage(self, 'Extractor list updated', report)
      restart()
    elif menuName=='verifyDB':
      report = self.comm.backend.checkDB(outputStyle='html', minimal=True)
      showMessage(self, 'Report of database verification', report, style='QLabel {min-width: 800px}')
    elif menuName=='sync':
      report = self.comm.backend.replicateDB(progressBar=self.sidebar.progress)
      showMessage(self, 'Report of syncronization', report, style='QLabel {min-width: 450px}')
    elif menuName=='exit':
      self.close()
    elif menuName=='website':
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/')
    elif menuName=='extractorTest':
      fileName = QFileDialog.getOpenFileName(self,'Open file for extractor test',str(Path.home()),'*.*')[0]
      report = self.comm.backend.testExtractor(fileName, outputStyle='html')
      showMessage(self, 'Report of extractor test', report)
    elif menuName=='extractorTest2':
      self.comm.testExtractor.emit()
    elif menuName=='shortcuts':
      showMessage(self, 'Keyboard shortcuts', shortcuts)
    elif menuName=='restart':
      restart()
    elif menuName=='todo':
      try:
        from .tempStrings import todoString
        showMessage(self, 'List of items on todo list',todoString)
      except Exception:
        pass
    elif menuName=='export':
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to export', 'Warning')
        return
      fileName = QFileDialog.getSaveFileName(self,'Save data into .eln file',str(Path.home()),'*.eln')[0]
      status = exportELN(self.comm.backend, self.comm.projectID, fileName)
      showMessage(self, 'Finished', status, 'Information')
    elif menuName=='import':
      fileName = QFileDialog.getOpenFileName(self,'Load data from .eln file',str(Path.home()),'*.eln')[0]
      status = importELN(self.comm.backend, fileName)
      showMessage(self, 'Finished', status, 'Information')
      self.comm.changeSidebar.emit('redraw')
      self.comm.changeTable.emit('x0','')
    else:
      showMessage(self,
                  'ERROR',
                  f'menu not implemented yet: {menuName}',
                  icon='Warning')
    return


  def changeProjectGroup(self) -> None:
    """
    change default project group in configuration file and restart
    """
    self.backend.configuration['defaultProjectGroup'] = self.sender().data()
    with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.backend.configuration,indent=2))
    restart()
    return

# TODO_P5 copy of file: should it the be the same in database or should it be two separate entities??
#         - what happens if you want to change metadata of one but don't want to change the other?
#           - copy of raw data into one that will changed, to clean

##############
## Main function
def main_gui() -> tuple[QApplication | QApplication, MainWindow]:
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
  if not QApplication.instance():
    app = QApplication()
  else:
    app = QApplication.instance()
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
  logging.info('End PASTA GUI')
  return app, window

# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  app, window = main_gui()
  window.show()
  app.exec()
