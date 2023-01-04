""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import platform
from PySide6.QtWidgets import QDialog, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, \
                              QFormLayout, QLineEdit, QLabel, QTextEdit   # pylint: disable=no-name-in-module

from .fixedStrings import configurationOverview
if platform.system()=='Windows':
  from .widgetConfigSetupWindows import ConfigurationSetup
else:
  from .widgetConfigSetupLinux import ConfigurationSetup

class Configuration(QDialog):
  """
  Main class
  """
  def __init__(self, backend, startTap):
    super().__init__()
    self.backend = backend
    self.setWindowTitle('PASTA-ELN configuration')
    self.mainLayout = QVBoxLayout()
    self.setLayout(self.mainLayout)
    self.tabWidget = QTabWidget(self)
    self.mainLayout.addWidget(self.tabWidget)

    # ---------------------
    # Overview
    tabOverview = QTextEdit()
    tabOverview.setMarkdown(configurationOverview)
    self.tabWidget.addTab(tabOverview, 'Overview')

    # ---------------------
    # Setup / Troubeshoot Pasta: main widget
    self.tabSetup = ConfigurationSetup(backend, self.finished)
    self.tabWidget.addTab(self.tabSetup, 'Setup')

    # ---------------------
    # Misc configuration: e.g. theming...
    self.tabConfig = QWidget()
    self.tabWidget.addTab(self.tabConfig, 'Miscellaneous')

    if startTap=='setup':
      self.tabWidget.setCurrentWidget(self.tabSetup)
      self.tabWidget.setTabEnabled(0, False)
      self.tabWidget.setTabEnabled(2, False)
    #...
    #magic order
    #Comment says what you do
    #1. define widget
    #2. define layout and assign to widget
    #3. define and add elements immediately

  def finished(self):
    """
    callback function to close widget
    """
    self.close()
    self.backend.initialize()  #restart backend
