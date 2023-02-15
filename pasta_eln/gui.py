""" Graphical user interface includes all widgets """
import os, logging
from pathlib import Path
from PySide6.QtCore import Qt, Slot      # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication    # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon, QAction, QKeySequence    # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from .backend import Backend
from .communicate import Communicate
from .widgetSidebar import Sidebar
from .widgetBody import Body
from .dialogForm import Form
os.environ['QT_API'] = 'pyside6'

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  """ Graphical user interface includes all widgets """
  def __init__(self):
    #global setting
    super().__init__()
    self.setWindowTitle("PASTA-ELN")
    self.setWindowState(Qt.WindowMaximized)
    self.setWindowIcon(QIcon('./Resources/Icons/favicon64.png'))
    self.backend = Backend()
    self.comm = Communicate(self.backend)
    self.comm.formDoc.connect(self.formDoc)

    #Menubar
    menu = self.menuBar()
    _ = menu.addMenu("&File")
    viewMenu = menu.addMenu("&View list")
    _ = menu.addMenu("&System")
    _ = menu.addMenu("&Help")

    shortCuts = {'measurement':'m', 'sample':'s'}
    for docType, docLabel in self.comm.backend.db.dataLabels.items():
      if docType[0]=='x' and docType[1]!='0':
        continue
      action = QAction(docLabel, self)
      if docType in shortCuts:
        action.setShortcut(QKeySequence("Ctrl+"+shortCuts[docType]))
      action.setData(docType)
      action.triggered.connect(self.viewMenu)
      viewMenu.addAction(action)

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


  @Slot(str)
  def formDoc(self, doc):
    """
    What happens when new/edit dialog is shown

    Args:
      doc (dict): document
    """
    formWindow = Form(self.comm.backend, doc)
    formWindow.exec()
    return


  def viewMenu(self):
    """
    act on user pressing an item in view
    """
    docType = self.sender().data()
    self.comm.changeTable.emit(docType, '')
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
  window.show()
  app.exec()
  logging.info('End PASTA GUI')
  return

# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  main()
