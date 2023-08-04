""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import platform
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget,  QTextEdit  # pylint: disable=no-name-in-module
from ..backend import Backend
from .configGUI import ConfigurationGUI
from .configAuthors import ConfigurationAuthors
if platform.system()=='Windows':
  from .configSetupWindows import ConfigurationSetup
else:
  from .configSetupLinux import ConfigurationSetup

class Configuration(QDialog):
  """ Main class of entire config dialog """
  def __init__(self, backend:Backend, startTab:str=''):
    """
    Initialization

    Args:
      backend (Pasta): backend, not communication
      startTab (str): tab to show initially
    """
    super().__init__()
    self.backend = backend
    self.setWindowTitle('PASTA-ELN configuration')

    # GUI elements
    mainL = QVBoxLayout(self)
    tabW = QTabWidget(self)
    mainL.addWidget(tabW)

    # Misc configuration: e.g. theming...
    tabGUI = ConfigurationGUI(backend, self.finished)
    tabW.addTab(tabGUI, 'Appearance')
    tabGUI = ConfigurationAuthors(backend, self.finished)
    tabW.addTab(tabGUI, 'Authors')

    # Setup / Troubeshoot Pasta: main widget
    tabSetup = ConfigurationSetup(backend, self.finished)
    tabW.addTab(tabSetup, 'Setup')

    if startTab=='setup':
      tabW.setCurrentWidget(tabSetup)
      tabW.setTabEnabled(0, False)
      tabW.setTabEnabled(1, False)


  def finished(self) -> None:
    """
    callback function to close widget
    """
    self.close()
    self.backend.initialize()  #restart backend
    return