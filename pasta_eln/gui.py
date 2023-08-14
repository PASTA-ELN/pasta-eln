""" Graphical user interface includes all widgets """
import json
import logging
import os
import sys
import webbrowser
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import Qt, Slot, QCoreApplication  # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QPixmap, QShortcut  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog  # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  # of https://github.com/UN-GCPDS/qt-material

from pasta_eln import __version__
from .GUI.body import Body
from .GUI.config import Configuration
from .GUI.form import Form
from .GUI.projectGroup import ProjectGroup
from .GUI.sidebar import Sidebar
from .backend import Backend
from .fixedStringsJson import shortcuts
from .guiCommunicate import Communicate
from .guiStyle import Action, showMessage, widgetAndLayout, shortCuts
from .inputOutput import exportELN, importELN
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
    resources_dir = Path(__file__).parent / 'Resources'
    self.setWindowIcon(QIcon(QPixmap(resources_dir / 'Icons' / 'favicon64.png')))
    self.backend = Backend()
    self.comm = Communicate(self.backend)
    self.comm.formDoc.connect(self.form_doc)

    # Menubar
    menu = self.menuBar()
    project_menu = menu.addMenu("&Project")
    Action('&Export .eln', self.execute_action, project_menu, self, name='export')
    Action('&Import .eln', self.execute_action, project_menu, self, name='import')
    project_menu.addSeparator()
    Action('&Exit', self.execute_action, project_menu, self, name='exit')

    view_menu = menu.addMenu("&Lists")
    if hasattr(self.backend, 'db'):
      for docType, docLabel in self.comm.backend.db.dataLabels.items():
        if docType[0] == 'x' and docType[1] != '0':
          continue
        Action(
          docLabel,
          self.view_menu,
          view_menu,
          self,
          f"Ctrl+{shortCuts[docType]}" if docType in shortCuts else None,
          docType,
        )
        if docType == 'x0':
          view_menu.addSeparator()
      view_menu.addSeparator()
      Action('&Tags', self.view_menu, view_menu, self, 'Ctrl+T', '_tags_')
      Action('&Unidentified', self.view_menu, view_menu, self, 'Ctrl+U', name='-')
      # TODO_P5 create list of unaccessible files: linked with accessible files

    system_menu = menu.addMenu("&System")
    Action('&Project groups', self.execute_action, system_menu, self, name='projectGroups')
    change_project_groups = system_menu.addMenu("&Change project group")
    if hasattr(self.backend, 'configuration'):  # not case in fresh install
      for name in self.backend.configuration['projectGroups'].keys():
        Action(name, self.change_project_group, change_project_groups, self, name=name)
    Action('&Syncronize', self.execute_action, system_menu, self, name='sync', shortcut='F5')
    Action('&Questionaires', self.execute_action, system_menu, self, name='ontology')
    system_menu.addSeparator()
    Action('&Test extraction from a file', self.execute_action, system_menu, self, name='extractorTest')
    Action('Test &selected item extraction', self.execute_action, system_menu, self, name='extractorTest2',
           shortcut='F2')
    Action('Update &Extractor list', self.execute_action, system_menu, self, name='updateExtractors')
    system_menu.addSeparator()
    Action('&Configuration', self.execute_action, system_menu, self, name='configuration', shortcut='Ctrl+0')

    help_menu = menu.addMenu("&Help")
    Action('&Website', self.execute_action, help_menu, self, name='website')
    Action('&Verify database', self.execute_action, help_menu, self, name='verifyDB', shortcut='Ctrl+?')
    Action('Shortcuts', self.execute_action, help_menu, self, name='shortcuts')
    Action('Todo list', self.execute_action, help_menu, self, name='todo')
    help_menu.addSeparator()
    # shortcuts for advanced usage (user should not need)
    QShortcut('F9', self, lambda: self.execute_action('restart'))
    # TODO_P3 -> lambda and change buttons/actions: cleaner code
    #  Action    ('Todo list',  self,  'todo',     help_menu, 'Ctrl+H')
    #  Action    ('&Tags',      self,  '_tags_', view_menu, 'Ctrl+T', call=self.view_menu)
    #  TextButton('Add Filter', self,  'addFilter', headerL)

    # TODO_P3 export to dataverse
    # GUI elements
    main_widget, main_layout = widgetAndLayout('H')
    self.setCentralWidget(main_widget)  # Set the central widget of the Window
    body = Body(self.comm)  # body with information
    self.sidebar = Sidebar(self.comm)  # sidebar with buttons
    # sidebarScroll = QScrollArea()
    # sidebarScroll.setWidget(self.sidebar)
    # if hasattr(self.comm.backend, 'configuration'):
    #   sidebarScroll.setFixedWidth(self.comm.backend.configuration['GUI']['sidebarWidth']+10)
    # main_layout.addWidget(sidebarScroll)
    main_layout.addWidget(self.sidebar)
    main_layout.addWidget(body)
    self.comm.changeTable.emit('x0', '')

  @Slot(str)
  def form_doc(self, doc: dict[str, Any]) -> None:
    """
    What happens when new/edit dialog is shown

    Args:
      doc: document

    Returns:
    """
    if '_id' in doc:
      logging.debug('gui:formdoc ' + str(doc['_id']))
    elif '_ids' in doc:
      logging.debug('gui:formdoc ' + str(doc['_ids']))
    else:
      logging.debug('gui:formdoc of type ' + str(doc['-type']))
    form_window = Form(self.comm, doc)
    ret = form_window.exec()
    if ret == 0:
      self.comm.stopSequentialEdit.emit()
    return

  def view_menu(self) -> None:
    """
      Act on user pressing an item in view
    Returns:

    """
    doc_type = self.sender().data()
    self.comm.changeTable.emit(doc_type, '')
    return

  def execute_action(self, menu_name: Optional[str] = None) -> None:
    """
    Action after clicking menu item
    Args:
      menu_name:

    Returns:

    """
    if menu_name is None or not menu_name:
      menu_name = self.sender().data()
    if menu_name == 'configuration':
      dialog = Configuration(self.comm.backend)
      dialog.exec()
    elif menu_name == 'projectGroups':
      dialog = ProjectGroup(self.comm.backend)
      dialog.exec()
    elif menu_name == 'ontology':
      showMessage(self, 'To be implemented',
                  'A possibility to change the questionaires / change the ontology is missing.')
      # dialog = Ontology(self.comm.backend)
      # dialog.exec()
    elif menu_name == 'updateExtractors':
      report = updateExtractorList(self.backend.extractorPath)
      showMessage(self, 'Extractor list updated', report)
      restart()
    elif menu_name == 'verifyDB':
      report = self.comm.backend.checkDB(outputStyle='html', minimal=True)
      showMessage(self, 'Report of database verification', report, style='QLabel {min-width: 800px}')
    elif menu_name == 'sync':
      report = self.comm.backend.replicateDB(progressBar=self.sidebar.progress)
      showMessage(self, 'Report of syncronization', report, style='QLabel {min-width: 450px}')
    elif menu_name == 'exit':
      self.close()
    elif menu_name == 'website':
      webbrowser.open('https://pasta-eln.github.io/pasta-eln/')
    elif menu_name == 'extractorTest':
      file_name = QFileDialog.getOpenFileName(self, 'Open file for extractor test', str(Path.home()), '*.*')[0]
      report = self.comm.backend.testExtractor(file_name, outputStyle='html')
      showMessage(self, 'Report of extractor test', report)
    elif menu_name == 'extractorTest2':
      self.comm.testExtractor.emit()
    elif menu_name == 'shortcuts':
      showMessage(self, 'Keyboard shortcuts', shortcuts)
    elif menu_name == 'restart':
      restart()
    elif menu_name == 'todo':
      try:
        from .tempStrings import todoString
        showMessage(self, 'List of items on todo list', todoString)
      except Exception:
        pass
    elif menu_name == 'export':
      if self.comm.projectID == '':
        showMessage(self, 'Error', 'You have to open a project to export', 'Warning')
        return
      file_name = QFileDialog.getSaveFileName(self, 'Save data into .eln file', str(Path.home()), '*.eln')[0]
      status = exportELN(self.comm.backend, self.comm.projectID, file_name)
      showMessage(self, 'Finished', status, 'Information')
    elif menu_name == 'import':
      file_name = QFileDialog.getOpenFileName(self, 'Load data from .eln file', str(Path.home()), '*.eln')[0]
      status = importELN(self.comm.backend, file_name)
      showMessage(self, 'Finished', status, 'Information')
      self.comm.changeSidebar.emit('redraw')
      self.comm.changeTable.emit('x0', '')
    else:
      showMessage(self,
                  'ERROR',
                  f'menu not implemented yet: {menu_name}',
                  icon='Warning')
    return

  def change_project_group(self) -> None:
    """
      Change default project group in configuration file and restart

    Returns:

    """
    self.backend.configuration['defaultProjectGroup'] = self.sender().data()
    with open(Path.home() / '.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.backend.configuration, indent=2))
    restart()
    return


# TODO_P5 copy of file: should it the be the same in database or should it be two separate entities??
#         - what happens if you want to change metadata of one but don't want to change the other?
#           - copy of raw data into one that will changed, to clean


def main_gui() -> tuple[QApplication | QCoreApplication | None, MainWindow]:
  """
    Main method and entry point for commands
  Returns:

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
    application = QApplication()
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
  # end test coexistance
  logging.info('End PASTA GUI')
  return application, main_window


# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  app, window = main_gui()
  window.show()
  app.exec()
