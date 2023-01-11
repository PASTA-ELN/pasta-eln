""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import platform, json
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QFormLayout, QLabel, QTextEdit, QGroupBox,\
                              QComboBox   # pylint: disable=no-name-in-module

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
    """
    Initialization

    Args:
      backend (Pasta): backend, not communication
      startTap (str): tab to show initially
    """
    super().__init__()
    self.backend = backend
    self.setWindowTitle('PASTA-ELN configuration')

    # GUI Stuff
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
    self.tabAppearanceW = QGroupBox('Change appearance')
    layout = QFormLayout()
    themes = QComboBox()
    themes.addItems(['dark_amber','dark_blue','dark_cyan','dark_lightgreen','dark_pink','dark_purple', \
                     'dark_red','dark_teal','dark_yellow','light_amber','light_blue','light_cyan',\
                     'light_cyan_500','light_lightgreen','light_pink','light_purple','light_red','light_teal',\
                     'light_yellow','none'])
    if 'GUI' in self.backend.configuration and 'theme' in self.backend.configuration['GUI']:
      themes.setCurrentText(self.backend.configuration['GUI']['theme'])
    else:
      themes.setCurrentText('none')
    themes.currentTextChanged.connect(self.changeTheme)
    layout.addRow(QLabel("Theme"), themes)
    self.tabAppearanceW.setLayout(layout)
    self.tabWidget.addTab(self.tabAppearanceW, 'Appearance')

    if startTap=='setup':
      self.tabWidget.setCurrentWidget(self.tabSetup)
      self.tabWidget.setTabEnabled(0, False)
      self.tabWidget.setTabEnabled(2, False)


  def finished(self):
    """
    callback function to close widget
    """
    self.close()
    self.backend.initialize()  #restart backend
    return


  def changeTheme(self, theme):
    """
    change theme, save result on harddisk

    Args:
      theme (str): theme to change to
    """
    if 'GUI' not in self.backend.configuration:
      self.backend.configuration = {}
    self.backend.configuration['GUI']['theme'] = theme
    with open(Path.home()/'.pastaELN.json', 'w', encoding='utf-8') as fConf:
      fConf.write(json.dumps(self.backend.configuration,indent=2))
    return
