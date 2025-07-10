from pasta_eln.gui import MainWindow


def test_simple(qtbot):
  window = MainWindow('research')
  window.setMinimumSize(1024,800)
  window.show()
  qtbot.addWidget(window)

  # projID1 = window.comm.backend.output('x0').split('|')[-1].strip()
  # print(projID1)
  # window.comm.changeProject.emit(projID1, '')
  # click in the Greet button and make sure it updates the appropriate label
  # projectBtn = window.sidebar.projectsListL.itemAt(0).widget().layout().itemAt(0).widget()
  # qtbot.mouseClick(projectBtn, Qt.LeftButton)
  #
  path = qtbot.screenshot(window)
  print(path)
  # saved in
  #   /tmp/pytest-of-steffen/pytest-0/test_simple0/
  #   /tmp/pytest-of-runner/pytest-0/test_simple0/screenshot_MainWindow.png
