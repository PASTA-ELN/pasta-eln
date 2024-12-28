""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget  # pylint: disable=no-name-in-module
from ..guiCommunicate import Communicate
from .configProjectGroup import ProjectGroup
from .configGUI import ConfigurationGUI
from .configAuthors import ConfigurationAuthors
from .configSetup import ConfigurationSetup

class Configuration(QDialog):
  """ Main class of entire config dialog """
  def __init__(self, comm:Communicate, startTab:str=''):
    """
    Initialization

    Args:
      backend (Pasta): backend, not communication
      startTab (str): tab to show initially
    """
    super().__init__()
    self.comm = comm
    self.setWindowTitle('PASTA-ELN configuration')
    self.setMinimumWidth(1200)

    # GUI elements
    mainL = QVBoxLayout(self)
    tabW = QTabWidget(self)
    mainL.addWidget(tabW)

    tabProjectGroup = ProjectGroup(self.comm, self.closeWidget)     # Project group. Restart app
    tabW.addTab(tabProjectGroup, 'Project group')

    tabGUI = ConfigurationGUI(self.comm, self.closeWidget)          # Misc configuration: e.g. theming. Restart app
    tabW.addTab(tabGUI, 'Appearance')

    tabAuthors = ConfigurationAuthors(self.comm, self.closeWidget)  # Author(s)
    tabW.addTab(tabAuthors, 'Author')

    tabSetup = ConfigurationSetup(self.comm, self.closeWidget)      # Setup / Troubleshoot Pasta
    tabW.addTab(tabSetup, 'Setup')

    # initialize when setup is called
    if startTab=='setup':
      tabW.setCurrentWidget(tabSetup)
      tabW.setTabEnabled(0, False)
      tabW.setTabEnabled(1, False)
      tabW.setTabEnabled(2, False)


  def closeWidget(self, restart:bool=True) -> None:
    """
    callback function to close widget, without restarting the entire app

    Args:
      restart (bool): if true, initialize
    """
    self.close()
    if restart:
      self.comm.backend.initialize()  #restart backend
    return
