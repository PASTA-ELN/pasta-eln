""" Color palette allows easy color access """
import platform
from PySide6.QtWidgets import QMainWindow
from qt_material import get_theme

class Palette():
  """ Color palette allows easy color access """
  def __init__(self, mainWindow:QMainWindow|None, theme:str) -> None:
    self.theme = theme
    if theme=='none':
      if platform.system() == 'Linux':
        self.subtheme = 'light' if mainWindow is None or mainWindow.palette().button().color().red()>128 else 'dark'
      else:
        self.subtheme = 'light'
      self.primary       = '#222222'
      self.secondaryText = '#000000'
    else:
      self.subtheme = 'light' if 'light' in theme else 'dark'
      self.primary       = get_theme(f'{theme}.xml')['primaryColor']
      self.secondaryText =  get_theme(f'{theme}.xml')['primaryTextColor']
    # for all themes
    if self.subtheme == 'dark':
      self.text       = '#EEEEEE'
      self.leafX      = '#222222'
      self.leafO      = '#333333'
      self.leafShadow = 'black'
    else:
      self.text       = '#111111'
      self.leafX      = '#EEEEEE'
      self.leafO      = '#FFFFFF'
      self.leafShadow = '#AAAAAA'


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
      return  f'{prefix}: #EEEEEE; '
    return f'{prefix}: {get_theme(f"{self.theme}.xml")[f"{color}Color"]}; '
