""" Color pallette allows easy color access """
from PySide6.QtWidgets import QMainWindow
from qt_material import get_theme

class Palette():
  """ Color pallette allows easy color access """
  def __init__(self, mainWindow:QMainWindow, theme:str) -> None:
    self.theme = theme
    if theme=='none':
      self.subtheme = 'light' if mainWindow.palette().button().color().red()>128 else 'dark'
      self.primary       = '#222222'
      self.secondaryText = '#000000'
    else:
      self.subtheme = 'light' if 'light' in theme else 'dark'
      self.primary       = get_theme(f'{theme}.xml')['primaryColor']
      self.secondaryText =  get_theme(f'{theme}.xml')['primaryTextColor']
      #  qt_material - dark-blue:
      # - {'primaryColor': '#448aff', 'primaryLightColor': '#83b9ff', 'secondaryColor': '#232629', 'secondaryLightColor': '#4f5b62',
      # - 'secondaryDarkColor': '#31363b', 'primaryTextColor': '#000000', 'secondaryTextColor': '#ffffff'}
      #   _amber: button text color could be changed : #TODO later
      # - get table of all colors
      # - test with slideShowGui
      #  from docu: apply_stylesheet(
      #         app,
      #         theme + '.xml',
      #         invert_secondary=('light' in theme and 'dark' not in theme),
      #         extra=extra,
      #     )
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
