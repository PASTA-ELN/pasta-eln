""" Graphical user interface includes all widgets """
import os, logging
from pathlib import Path
from PySide6.QtCore import Qt, Slot      # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication    # pylint: disable=no-name-in-module
from PySide6.QtGui import QIcon    # pylint: disable=no-name-in-module
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from .backend import Pasta
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
    self.backend = Pasta()
    self.comm = Communicate(self.backend)
    self.comm.formDoc.connect(self.formDoc)

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


##############
## Main function
def main():
  """ Main method and entry point for commands """
  logPath = Path.home()/'pastaELN.log'
  #old versions of basicConfig do not know "encoding='utf-8'"
  logging.basicConfig(filename=logPath, level=logging.INFO, format='%(asctime)s|%(levelname)s:%(message)s',
                      datefmt='%m-%d %H:%M:%S')   #TODO_P1 this loggingWarning goes into configuration
  for package in ['urllib3', 'requests', 'asyncio', 'datalad', 'PIL', 'matplotlib.font_manager']:
    logging.getLogger(package).setLevel(logging.WARNING)
  logging.info('Start PASTA GUI')
  app = QApplication()
  window = MainWindow()
  if 'GUI' in window.backend.configuration and 'theme' in window.backend.configuration['GUI']:  #GUI2 vs GUI prepare for both
    theme = window.backend.configuration['GUI']['theme']
    apply_stylesheet(app, theme=theme+'.xml')
  window.show()
  app.exec()
  logging.info('End PASTA GUI')
  return

# called by python3 -m pasta_eln.gui
if __name__ == '__main__':
  main()
