""" Color palette allows easy color access """
import platform, json
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QApplication
from qt_material import apply_stylesheet, get_theme  # of https://github.com/UN-GCPDS/qt-material
from ..fixedStringsJson import CONF_FILE_NAME


class Palette():
  """ Color palette allows easy color access """
  def __init__(self, mainWindow:QMainWindow|None, accent:str) -> None:
    """ Initialize the color palette
    Args:
      mainWindow (QMainWindow): main window for getting system theme
      accent (str): accent color, e.g. 'pink'
    """
    accent = self.cleanAccent(accent)                # given theme #TODO temporary
    systemTheme = 'light' if mainWindow is None or mainWindow.palette().button().color().red()>128 or \
      platform.system() != 'Linux' else 'dark' # system color mode: dark/light
    self.theme = 'none' if accent=='none' else f'{systemTheme}_{accent}' # theme name
    if accent=='none':
      self.primary       = '#222222'
      self.secondaryText = '#000000'
    else:
      self.primary       = get_theme(f'{self.theme}.xml')['primaryColor']
      self.secondaryText =  get_theme(f'{self.theme}.xml')['primaryTextColor']
    # for all themes
    if systemTheme == 'dark':
      self.text       = '#EEEEEE'
      self.leafX      = '#222222'
      self.leafO      = '#333333'
      self.leafShadow = 'black'
    else:
      self.text       = '#111111'
      self.leafX      = '#EEEEEE'
      self.leafO      = '#FFFFFF'
      self.leafShadow = '#AAAAAA'


  def setTheme(self, application:QApplication) -> None:
    """ set theme of application
    Args:
      application (QApplication): application to set the theme
    """
    if self.theme != 'none':
      apply_stylesheet(application, theme=f'{self.theme}.xml')
    return


  def cleanAccent(self, accent:str) -> str:
    """ Clean accent color name

    Args:
      accent (str): accent color, e.g. 'pink'

    Returns:
      str: cleaned accent color
    """
    if '_' in accent:
      newAccent = accent.split('_')[1]
      with open(Path.home()/CONF_FILE_NAME, encoding='utf-8') as fConf:
        configuration =json.load(fConf)
      configuration['GUI']['theme'] = newAccent
      with open(Path.home()/CONF_FILE_NAME, 'w', encoding='utf-8') as fConf:
        fConf.write(json.dumps(configuration, indent=2))
      return newAccent
    return accent


  def get(self, color:str, prefix:str) -> str:
    """ Get color with a prefix for CSS styling

    Args:
      color (str): qt-material colors without the trailing color; buttonText is an additional color
      prefix (str): css-key, e.g. 'background-color'

    Returns:
      str: css-string, e.g. 'background-color: #333421;'
    """
    if self.theme=='none':
      return ''
    if color=='buttonText':
      return  f'{prefix}: {self.text}; '
    return f'{prefix}: {get_theme(f"{self.theme}.xml")[f"{color}Color"]}; '
