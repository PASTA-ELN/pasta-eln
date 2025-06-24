""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import logging
from PySide6.QtWidgets import QDialog, QTabWidget, QVBoxLayout             # pylint: disable=no-name-in-module
from ..guiCommunicate import Communicate
from .configAddOnParameter import ConfigurationAddOnParameter
from .configAuthors import ConfigurationAuthors
from .configGUI import ConfigurationGUI
from .configProjectGroup import ProjectGroup
from .configSetup import ConfigurationSetup
from .repositories.configGUI import ConfigurationRepositories


class Configuration(QDialog):
  """ Main class of entire config dialog """
  def __init__(self, comm:Communicate, startTab:str=''):
    """
    Initialization
    - if sidebar.py notices no database, it will call this dialog with 'setup' as only tab

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

    # tab has to always exist
    tabSetup = ConfigurationSetup(self.comm, self.closeWidget)                    # Setup / Troubleshoot Pasta

    # optional tabs
    try:
      tabProjectGroup = ProjectGroup(self.comm, self.closeWidget)                 # Project group. Restart app
      tabW.addTab(tabProjectGroup, 'Project group')

      tabGUI = ConfigurationGUI(self.comm, self.closeWidget)   # Misc configuration: e.g. theming. Restart app
      tabW.addTab(tabGUI, 'Appearance')

      tabAuthors = ConfigurationAuthors(self.comm, self.closeWidget)                               # Author(s)
      tabW.addTab(tabAuthors, 'Author')

      tabRepository = ConfigurationRepositories(self.comm, self.closeWidget)                    # Repositories
      tabW.addTab(tabRepository, 'Repository')

      tabAddOnParameter = ConfigurationAddOnParameter(self.comm, self.closeWidget)         # Add-on parameters
      tabW.addTab(tabAddOnParameter, 'Add-on parameters')

      # initialize when setup is called
      if startTab=='setup':
        tabW.setCurrentWidget(tabSetup)
        tabW.setTabEnabled(0, False)
        tabW.setTabEnabled(1, False)
        tabW.setTabEnabled(2, False)
        tabW.setTabEnabled(3, False)
        tabW.setTabEnabled(4, False)
    except Exception as e:
      logging.error('Could not create configuration dialog: %s', e)

    # always add setup tab
    tabW.addTab(tabSetup, 'Setup')


  def closeWidget(self, restart:bool=True) -> None:
    """
    callback function to close widget, without restarting the entire app

    Args:
      restart (bool): if true, initialize
    """
    self.close()
    if restart:
      self.comm.restart.emit()                                                                    #send signal
    return
