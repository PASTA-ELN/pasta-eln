""" Graphical user interface includes all widgets """
import os, logging, webbrowser
from pathlib import Path
from PySide6.QtCore import Qt, Slot      # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QFileDialog # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QAction    # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from .backend import Backend
from .communicate import Communicate
from .widgetSidebar import Sidebar
from .widgetBody import Body
from .dialogForm import Form
from .dialogConfig import Configuration
from .dialogProjectGroup import ProjectGroup
from .dialogOntology import Ontology
from .miscTools import updateExtractorList
from .mixin_cli import text2html
from .style import Action, showMessage
from .fixedStrings import shortcuts
os.environ['QT_API'] = 'pyside6'

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """
  def __init__(self):
    #global setting
    super().__init__()
    self.setWindowTitle("PASTA-ELN")
    self.setWindowState(Qt.WindowMaximized)
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
    systemMenu = menu.addMenu("&System")
    Action('&Ontology',              self.executeAction, systemMenu, self, name='ontology')
    Action('&Project groups',        self.executeAction, systemMenu, self, name='projectGroups')
    #TODO_P3 convenience: change project group via menus
    systemMenu.addSeparator()
    Action('Update &Extractor list', self.executeAction, systemMenu, self, name='updateExtractors')
    Action('&Verify database',       self.executeAction, systemMenu, self, name='verifyDB', shortcut='Ctrl+?')
    systemMenu.addSeparator()
    Action('&Configuration',         self.executeAction, systemMenu, self, name='configuration')
    helpMenu = menu.addMenu("&Help")
    Action('&Website',               self.executeAction, helpMenu, self, name='website')
    Action('&Test file extraction',  self.executeAction, helpMenu, self, name='extractorTest')
    Action('&Test selected item extraction', self.executeAction, helpMenu, self, name='extractorTest2', shortcut='F2')
    Action('&Shortcuts',             self.executeAction, helpMenu, self, name='shortcuts')
    Action('&Todo list',             self.executeAction, helpMenu, self, name='todo')

    shortCuts = {'measurement':'m', 'sample':'s', 'x0':'p'} #TODO_P5 addToConfig
    for docType, docLabel in self.comm.backend.db.dataLabels.items():
      if docType[0]=='x' and docType[1]!='0':
        continue
      Action(docLabel, self.viewMenu, viewMenu, self, \
        "Ctrl+"+shortCuts[docType] if docType in shortCuts else None, docType)
      if docType=='x0':
        viewMenu.addSeparator()
    viewMenu.addSeparator()
    Action('&Tags',         self.viewMenu, viewMenu, self, 'Ctrl+T', '_tags_')
    Action('&Unidentified', self.viewMenu, viewMenu, self, name='-')

    #GUI elements
    mainWidget = QWidget()
    mainLayout = QHBoxLayout()
    mainLayout.setContentsMargins(0,0,0,0)
    mainLayout.setSpacing(0)
    mainWidget.setLayout(mainLayout)
    self.setCentralWidget(mainWidget)      # Set the central widget of the Window
    body = Body(self.comm)        #body with information
    sidebar = Sidebar(self.comm)  #sidebar with buttons
    mainLayout.addWidget(sidebar)
    mainLayout.addWidget(body)
    self.comm.changeTable.emit('x0','')


  @Slot(str)
  def formDoc(self, doc):
    """
    What happens when new/edit dialog is shown

    Args:
      doc (dict): document
    """
    formWindow = Form(self.comm, doc)
    formWindow.exec()
    return


  def viewMenu(self):
    """
    act on user pressing an item in view
    """
    docType = self.sender().data()
    self.comm.changeTable.emit(docType, '')
    return


  def executeAction(self):
    """
    action after clicking menu item
    """
    menuName = self.sender().data()
    if menuName=='configuration':
      dialog = Configuration(self.comm.backend)
      dialog.exec()
    elif menuName=='projectGroups':
      dialog = ProjectGroup(self.comm.backend)
      dialog.exec()
    elif menuName=='ontology':
      dialog = Ontology(self.comm.backend)
      dialog.exec()
    elif menuName=='updateExtractors':
      updateExtractorList(self.backend.extractorPath)
    elif menuName=='verifyDB':
      report = self.comm.backend.checkDB(True)
      showMessage(self, 'Report of database verification', text2html(report), style='QLabel {min-width: 800px}')
    elif menuName=='exit':
      self.close()
    elif menuName=='website':
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/')
    elif menuName=='extractorTest':
      fileName = QFileDialog.getOpenFileName(self,'Open file for extractor test',str(Path.home()),'*.*')[0]
      report = self.comm.backend.testExtractor(fileName, reportHTML=True)
      showMessage(self, 'Report of extractor test', report)
    elif menuName=='extractorTest2':
      self.comm.testExtractor.emit()
    elif menuName=='shortcuts':
      showMessage(self, 'Keyboard shortcuts', shortcuts)
    elif menuName=='todo':
      try:
        from .tempStrings import todoString
        showMessage(self, 'List of items on todo list',todoString)
      except:
        pass
    else:
      showMessage(self, 'ERROR','menu not implemented yet: '+menuName, icon='Warning')
    return


##############
## Main function
def main():
  """ Main method and entry point for commands """
  app = QApplication()
  window = MainWindow()
  # logging
  logPath = Path.home()/'pastaELN.log'
  #  old versions of basicConfig do not know "encoding='utf-8'"
  logLevel = getattr(logging, window.backend.configuration['GUI']['loggingLevel'])
  logging.basicConfig(filename=logPath, level=logLevel, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')
  for package in ['urllib3', 'requests', 'asyncio', 'PIL', 'matplotlib.font_manager']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA GUI')
  # remainder
  theme = window.backend.configuration['GUI']['theme']
  if theme!='none':
    apply_stylesheet(app, theme=theme+'.xml')
  # test if qtawesome and matplot can coexist
  import qtawesome as qta
  if not isinstance(qta.icon('fa5s.times'), QIcon):
    logging.error('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
    print('qtawesome: could not load. Likely matplotlib is included and can not coexist.')
  # end test coexistance
  window.show()
  app.exec()
  logging.info('End PASTA GUI')
  return

# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  main()
