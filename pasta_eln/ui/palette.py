"""Color palette allows easy colour access and manages the application theme"""

from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeAlias, TypedDict, cast
import darkdetect
import qdarktheme
from PySide6.QtGui import QColor
from ..constants import THEME_COLOR_VALUES

if TYPE_CHECKING:
  from .gui_communicate import Communicate


class ColorModifiers(TypedDict, total=False):
  """Transformations applied to a category's base colour"""
  darken: float
  lighten: float
  transparent: float


ColorRule: TypeAlias = str | ColorModifiers
ColorCategory: TypeAlias = dict[str, ColorRule]
ThemeColorValues: TypeAlias = dict[str, dict[str, str | ColorCategory]]
ColorChannels: TypeAlias = tuple[int, int, int, int]

def nameColor(tags: str | Iterable[str]) -> QColor | None:
  """Return the first configured name color represented by ``tags``
    Args:
      tags (str | Iterable[str]): tags used to select a color
    Returns:
      QColor | None: Configured color for the first matching tag, if any
  """
  namedColors = {
    '#red': '#d32f2f',
    '#orange': '#ef6c00',
    '#yellow': '#b58900',
    '#green': '#2e7d32',
    '#blue': '#1565c0',
    '#purple': '#6a1b9a',
  }
  if isinstance(tags, str):
    tags = tags.split(',')
  for tag in tags:
    if color:= namedColors.get(str(tag).strip().lower()):
      return QColor(color)
  return None


class Palette:
  """ Color palette allows easy color access and manages Theme"""

  def __init__(self, comm: 'Communicate', theme: str) -> None:
    """ Initialize the color palette
    Args:
      comm ('Communicate'): shared communication object
      theme (str): 'light' or 'dark' or 'automatic'
    """
    self.comm = comm
    if theme in {'light', 'dark'}:
      self.qtheme = theme
    else:
      autoTheme = darkdetect.theme().lower()
      if autoTheme in ['light', 'dark']:
        self.qtheme = autoTheme
      else:
        print(f"DEBUG: darkdetect.theme().lower()={autoTheme} is not recognized")
        self.qtheme = 'light'
    self.primary = self.getThemeColor('primary', 'base')
    self.text = self.getThemeColor('foreground', 'base')
    self.leafX = self.getThemeColor('border', 'base')
    self.leafO = self.getThemeColor('background', 'popup')
    self.leafShadow = '#55000000'                                                          # Transparent Black


  def setTheme(self, theme: str = '', saveTheme: bool = True) -> None:
    """
    Update the theme of the whole App
    Args:
      theme (str): 'automatic'/'dark'/'light' for the dark/light theme. Empty String ('') for update without changing the theme
      saveTheme (bool): Whether the theme should be changed permanently or just until theme is updated again
    """
    cornershape = 'sharp'                                                                   # rounded or sharp
    css = """
    QWidget {
    border-radius: 3px;
    }

    QDialogButtonBox {
    min-height: 30px;
    padding-bottom: 25px;
    }
    """
    customColors: dict[str, str] = {}
    if theme == 'automatic':
      theme = darkdetect.theme().lower()
    if theme not in ['dark', 'light', '']:
      print('Could not find Theme:', theme)
      return
    if theme != '' and saveTheme:
      self.qtheme = theme
    if theme != '' and not saveTheme:
      qdarktheme.setup_theme(theme, additional_qss=css, corner_shape=cornershape, custom_colors=customColors)
    else:
      qdarktheme.setup_theme(self.qtheme, additional_qss=css, corner_shape=cornershape, custom_colors=customColors)
    self.comm.themeUpdated.emit()


  def get(self, color: str, prefix: str) -> str:
    """
    Get color with a prefix for CSS styling

    Args:
        color (str): qt-material colors without the trailing color; 'buttonText' is an additional color
        prefix (str): CSS key, e.g., 'background-color'

    Returns:
        str: CSS string, e.g., 'background-color: #333421;'. Returns an empty string if the theme is 'none'
    """
    colors = {
      'primary': self.getThemeColor('primary', 'base'),
      'primaryLight': '',
      'secondary': '',
      'secondaryLight': self.getThemeColor('background', 'popup'),
      'secondaryDark': self.getThemeColor('background', 'table'),
      'primaryText': '',
      'secondaryText': '',
    }
    if color == 'buttonText':
      return f'{prefix}: {self.text}; '
    return '' if colors[color] == '' else f'{prefix}: {colors[color]}; '


  def getThemeColor(self, category: str, subcategory: str) -> str:
    """
    Returns the computed QColor from the PyQtDarkTheme dict
    Look at THEME_COLOR_VALUES in constants.py for all possible categories

    Args:
        category (str): first level of dict, e.g., "background", "foreground", "primary"
        subcategory (str): second level of dict, e.g., "base", "panel", "icon", "button.hoverBackground"
    Returns:
        QColor: the computed color
    """
    # 1. Determine base color
    themeDict = cast(ThemeColorValues, THEME_COLOR_VALUES)[self.qtheme]
    cat: str | ColorCategory = themeDict.get(category, {})
    if isinstance(cat, str):
      if len(cat) > 7:                   # Colors in THEME_COLOR_VALUES are #RGBA, not #ARGB like QColor wants
        cat = rgba2argb(cat)
      return QColor(cat).name(format=QColor.NameFormat.HexArgb)
    baseHex = cat.get('base', '#000000')
    color = QColor(baseHex)

    # 2. Get the specific key
    rule = cat.get(subcategory, {})

    # 3. If it's a direct hex string
    if isinstance(rule, str):
      return QColor(rule).name()

    # Helper functions
    def _darken(color: QColor, amount: float) -> QColor:
      """Reduce the value channel of a color by the requested fraction

      Args:
        color (QColor): Color whose brightness should be reduced
        amount (float): Fraction by which the HSV value channel is reduced

      Returns:
        QColor: Color with the adjusted value and original hue, saturation, and alpha
      """
      h, s, v, a = cast(ColorChannels, color.getHsv())
      v = max(0, int(v * (1 - amount)))
      return QColor.fromHsv(h, s, v, a)

    def _lighten(color: QColor, amount: float) -> QColor:
      """Increase the value channel of a color by the requested fraction

      Args:
        color (QColor): Color whose brightness should be increased
        amount (float): Fraction by which the HSV value channel is increased

      Returns:
        QColor: Color with the adjusted value and original hue, saturation, and alpha
      """
      h, s, v, a = cast(ColorChannels, color.getHsv())
      v = min(255, int(v * (1 + amount)))
      return QColor.fromHsv(h, s, v, a)
    # 4. If it's a dict with modifiers
    if isinstance(rule, dict):
      # Apply darken/lighten first
      if 'darken' in rule:
        color = _darken(color, rule['darken'])
      if 'lighten' in rule:
        color = _lighten(color, rule['lighten'])
      # Apply transparency
      if 'transparent' in rule:
        alpha = int((1 - rule['transparent']) * 255)
        color.setAlpha(alpha)
        r, g, b, a = cast(ColorChannels, color.getRgb())
        return f"rgba({r}, {g}, {b}, {a})"
      return color.name()
    # 5. Fallback: return base color
    return color.name()


  def alterColor(self, colorHex:str, newAlpha:int=255) -> str:
    """ Change the color

    Args:
      colorHex (str): hex value of the color
      newAlpha (int): alpha value of the new color

    Returns:
      str: new color
    """
    newColor = QColor(colorHex)
    r, g, b, _ = cast(ColorChannels, newColor.getRgb())
    return f"rgba({r}, {g}, {b}, {newAlpha})"


def rgba2argb(hexColor: str) -> str:
  """Convert an RRGGBBAA color string to AARRGGBB
    Args:
      hexColor (str): RRGGBBAA color string to convert
    Returns:
      str: The color string reordered from RRGGBBAA to AARRGGBB
  """
  hexColor = hexColor.lstrip('#')
  red, green, blue, alpha = hexColor[:2], hexColor[2:4], hexColor[4:6], hexColor[6:8]
  return f'#{alpha}{red}{green}{blue}'
