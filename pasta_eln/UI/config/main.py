""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import logging
from PySide6.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QWidget
from ..guiCommunicate import Communicate
from ..repositories.config import ConfigurationRepositories
from .addOnParameter import ConfigurationAddOnParameter
from .authors import ConfigurationAuthors
from .gui import ConfigurationGUI
from .projectGroup import ProjectGroup
from .setup import ConfigurationSetup

# Loading times of tabs: min - max of 3 runs
# Tab 'Project group' loaded in 0.022 - 0.023 seconds
# Tab 'Appearance'    loaded in 0.045 - 0.047 seconds
# Tab 'Author'        loaded in 0.014 seconds
# Tab 'Repository'    loaded in 0.013 seconds
# Tab 'Add-on parameters' loaded in 0.672 - 0.672 seconds
# Tab 'Setup'         loaded in 0.002 seconds


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
    self.tabW = QTabWidget(self)
    self.tabW.currentChanged.connect(self.loadTab)
    mainL.addWidget(self.tabW)
    self.tabs = {}                                                          # to hold the actual tab instances
    self.placeholders = {}                                                       # to hold placeholder widgets
    self.tabClasses = {
      'Project group': ProjectGroup,
      'Appearance': ConfigurationGUI,
      'Author': ConfigurationAuthors,
      'Repository': ConfigurationRepositories,
      'Add-on parameters': ConfigurationAddOnParameter,
      'Setup': ConfigurationSetup
    }
    for name in self.tabClasses:
      placeholder = QWidget()     # Only create empty placeholder tabs initially
      self.placeholders[name] = placeholder
      self.tabW.addTab(placeholder, name)

    if startTab=='setup':
      self.tabW.setCurrentIndex(self.tabW.indexOf(self.placeholders['Setup']))
      for tabName in self.tabClasses:
        if tabName != 'Setup':
          self.tabW.setTabEnabled(self.tabW.indexOf(self.placeholders[tabName]), False)
    else:
      self.tabW.setCurrentIndex(0)


  def loadTab(self, index:int) -> None:
    """ Load the tab content when the tab is clicked
    - Replace the placeholder's content (layout and widget inside it)

    Args:
      index (int): index of the tab that was clicked
    """
    tabName = self.tabW.tabText(index)
    if tabName not in self.tabs and tabName in self.tabClasses:
      # Create the actual tab content
      tabClass = self.tabClasses[tabName]
      self.tabs[tabName] = tabClass(self.comm, self.closeWidget)
      placeholder = self.placeholders[tabName]
      if placeholder.layout():
        placeholder.layout().deleteLater()                                    # Clear the placeholder's layout
      layout = QVBoxLayout(placeholder)
      layout.setContentsMargins(0, 0, 0, 0)
      layout.addWidget(self.tabs[tabName])                                 # Add the actual tab content widget


  def closeWidget(self, restart:bool=True) -> None:
    """
    callback function to close widget, without restarting the entire app

    Args:
      restart (bool): if true, initialize
    """
    self.close()
    if restart:
      self.comm.softRestart.emit()                                                                #send signal
    return
