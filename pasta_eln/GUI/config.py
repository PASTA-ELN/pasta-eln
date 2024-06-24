""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
from typing import Union, Optional
import platform
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget  # pylint: disable=no-name-in-module
from ..guiCommunicate import Communicate
from .configGUI import ConfigurationGUI
from .configAuthors import ConfigurationAuthors
from .configSetupWindows import ConfigurationSetup as ConfigSetupWindows
from .configSetupLinux import ConfigurationSetup as ConfigSetupLinux

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

    # GUI elements
    mainL = QVBoxLayout(self)
    tabW = QTabWidget(self)
    mainL.addWidget(tabW)

    # Misc configuration: e.g. theming...
    tabGUI = ConfigurationGUI(self.comm, self.closeWidget)
    tabW.addTab(tabGUI, 'Appearance')
    tabAuthors = ConfigurationAuthors(self.comm, self.closeWidget)
    tabW.addTab(tabAuthors, 'Author')

    # Setup / Troubleshoot Pasta: main widget
    tabSetup:Optional[Union[ConfigSetupWindows,ConfigSetupLinux]] = None
    if platform.system()=='Windows':
      tabSetup = ConfigSetupWindows(self.comm, self.closeWidget)
    else:
      tabSetup = ConfigSetupLinux(self.comm, self.closeWidget)
    tabW.addTab(tabSetup, 'Setup')

    if startTab=='setup':
      tabW.setCurrentWidget(tabSetup)
      tabW.setTabEnabled(0, False)
      tabW.setTabEnabled(1, False)


  def closeWidget(self, restart:bool=True) -> None:
    """
    callback function to close widget

    Args:
      restart (bool): if true, initialize
    """
    self.close()
    if restart:
      self.comm.backend.initialize()  #restart backend
    return
