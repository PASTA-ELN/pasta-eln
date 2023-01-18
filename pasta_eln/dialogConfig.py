""" Entire config dialog (dialog is blocking the main-window, as opposed to create a new widget-window)"""
import platform, json
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QFormLayout, QLabel, QTextEdit, QGroupBox,\
                              QComboBox  # pylint: disable=no-name-in-module

from .fixedStrings import configurationOverview
from .miscTools import restart
from .style import TextButton
if platform.system()=='Windows':
  from .dialogConfigSetupWindows import ConfigurationSetup
else:
  from .dialogConfigSetupLinux import ConfigurationSetup

class Configuration(QDialog):
  """ Main class of entire config dialog """
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

    # GUI elements
    self.mainL = QVBoxLayout(self)
    self.tabW = QTabWidget(self)
    self.mainL.addWidget(self.tabW)

    # Overview
    # --------
    tabOverview = QTextEdit()
    tabOverview.setMarkdown(configurationOverview)
    self.tabW.addTab(tabOverview, 'Overview')

    # Setup / Troubeshoot Pasta: main widget
    # --------------------------------------
    self.tabSetup = ConfigurationSetup(backend, self.finished)
    self.tabW.addTab(self.tabSetup, 'Setup')

    # Misc configuration: e.g. theming...
    # -----------------------------------
    self.tabAppearanceW = QGroupBox('Change appearance')
    layout = QFormLayout()
    themes = QComboBox()
    themes.addItems(['dark_amber','dark_blue','dark_cyan','dark_lightgreen','dark_pink','dark_purple', \
                     'dark_red','dark_teal','dark_yellow','light_amber','light_blue','light_cyan',\
                     'light_cyan_500','light_lightgreen','light_pink','light_purple','light_red','light_teal',\
                     'light_yellow','none'])
    if 'GUI' in self.backend.configuration and 'theme' in self.backend.configuration['GUI']:  #TODO_P1 GUI2
      themes.setCurrentText(self.backend.configuration['GUI']['theme'])
    else:
      themes.setCurrentText('none')
    themes.currentTextChanged.connect(self.changeTheme)
    layout.addRow(QLabel("Theme"), themes)
    restartBtn = TextButton('Now', restart)
    layout.addRow(QLabel('Restart PASTA-ELN'), restartBtn)
    self.tabAppearanceW.setLayout(layout)
    self.tabW.addTab(self.tabAppearanceW, 'Appearance')

    if startTap=='setup':
      self.tabW.setCurrentWidget(self.tabSetup)
      self.tabW.setTabEnabled(0, False)
      self.tabW.setTabEnabled(2, False)


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
