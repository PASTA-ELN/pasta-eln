from PySide6.QtCore import Qt # pylint: disable=no-name-in-module
from pasta_eln.gui import MainWindow

def test_simple(qtbot):
  window = MainWindow()
  window.setMinimumSize(1024,800)
  window.show()
  qtbot.addWidget(window)

  # click in the Greet button and make sure it updates the appropriate label
  qtbot.mouseClick(window.sidebar, Qt.LeftButton)
  #
  path = qtbot.screenshot(window) # saved in /tmp/pytest-of-steffen/pytest-0/test_simple0/
  print(path)
  # lximage-qt /tmp/pytest-of-steffen/pytest-1/test_simple0/screenshot_MainWindow.png

  # assert widget.greet_label.text() == "Hello!"
