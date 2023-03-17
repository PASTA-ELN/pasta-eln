""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import platform
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget,  QTextEdit  # pylint: disable=no-name-in-module

from .fixedStrings import configurationOverview
from .dialogConfigGUI import ConfigurationGUI
if platform.system()=='Windows':
  from .dialogConfigSetupWindows import ConfigurationSetup
else:
  from .dialogConfigSetupLinux import ConfigurationSetup

class Configuration(QDialog):
  """ Main class of entire config dialog """
  def __init__(self, backend, startTap=''):
    """
    Initialization

    Args:
      backend (Pasta): backend, not communication
      startTap (str): tab to show initially
    """
    super().__init__()
    self.backend = backend
    self.setWindowTitle('PASTA-ELN configuration')

    # GUI elements
    mainL = QVBoxLayout(self)
    tabW = QTabWidget(self)
    mainL.addWidget(tabW)

    # Overview
    # --------
    tabOverview = QTextEdit()
    tabOverview.setMarkdown(configurationOverview)
    tabW.addTab(tabOverview, 'Overview')

    # Setup / Troubeshoot Pasta: main widget
    tabSetup = ConfigurationSetup(backend, self.finished)
    tabW.addTab(tabSetup, 'Setup')

    # Misc configuration: e.g. theming...
    tabGUI = ConfigurationGUI(backend, self.finished)
    tabW.addTab(tabGUI, 'Appearance')

    if startTap=='setup':
      tabW.setCurrentWidget(tabSetup)
      tabW.setTabEnabled(0, False)
      tabW.setTabEnabled(2, False)


  def finished(self):
    """
    callback function to close widget
    """
    self.close()
    self.backend.initialize()  #restart backend
    return
