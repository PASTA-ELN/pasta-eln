""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
from PySide6.QtWidgets import QDialog, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, \
                              QFormLayout, QLineEdit, QLabel, QTextEdit   # pylint: disable=no-name-in-module

from widgetConfigSetup import ConfigurationSetup
from fixedStrings import configurationOverview

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
    self.tabSetup = ConfigurationSetup(backend)
    self.tabWidget.addTab(self.tabSetup, 'Setup')
    if startTap=='setup':
      self.tabWidget.setCurrentWidget(self.tabSetup)

    # ---------------------
    # Misc configuration: e.g. theming...
    self.tabConfig = QWidget()
    self.tabWidget.addTab(self.tabConfig, 'Miscellaneous')
    #...
    #magic order
    #Comment says what you do
    #1. define widget
    #2. define layout and assign to widget
    #3. define and add elements immediately
