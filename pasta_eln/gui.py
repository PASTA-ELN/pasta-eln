import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from backend import Pasta
from communicate import Communicate
from widgetSidebar import Sidebar
from widgetBody import Body
os.environ['QT_API'] = 'pyside6'

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  def __init__(self):
    #global setting
    super().__init__()
    self.setWindowTitle("PASTA-ELN")
    self.setWindowState(Qt.WindowMaximized)
    self.backend = Pasta()
    comm = Communicate(self.backend)

    #WIDGETS
    mainWidget = QWidget()
    mainLayout = QHBoxLayout()
    mainLayout.setContentsMargins(0,0,0,0)
    mainLayout.setSpacing(0)
    mainWidget.setLayout(mainLayout)
    self.setCentralWidget(mainWidget)      # Set the central widget of the Window
    body = Body(comm)        #body with information
    sidebar = Sidebar(comm)  #sidebar with buttons
    mainLayout.addWidget(sidebar)
    mainLayout.addWidget(body)
    self.show()

## Main function
if __name__ == '__main__':
  app = QApplication()
  apply_stylesheet(app, theme='dark_blue.xml')
  window = MainWindow()
  app.exec()
