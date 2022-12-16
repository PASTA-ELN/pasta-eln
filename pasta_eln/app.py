from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from qt_material import apply_stylesheet  #of https://github.com/UN-GCPDS/qt-material

from backend import Pasta
from widgetHead import Head
from widgetBody import Body

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
  def __init__(self):
    #global setting
    super().__init__()
    self.setWindowTitle("PASTA-ELN")
    self.setWindowState(Qt.WindowMaximized)
    self.backend = Pasta()

    #WIDGETS
    widget = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(0)
    widget.setLayout(layout)
    self.setCentralWidget(widget)      # Set the central widget of the Window
    head = Head(layout, self.backend) #head with buttons
    body = Body(layout)
    self.show()

## Main function
if __name__ == '__main__':
  app = QApplication()
  apply_stylesheet(app, theme='dark_blue.xml')
  window = MainWindow()
  app.exec()
