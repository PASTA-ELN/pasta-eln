""" Color palette allows easy color access and manages Theme"""

import qdarktheme
import darkdetect
from PySide6.QtGui import QColor

from ..fixed_strings_json import THEME_COLOR_VALUES
from ..misc_tools import rgba_to_argb


class Palette:
  """ Color palette allows easy color access and manages Theme"""

  def __init__(self, theme: str) -> None:
    """ Initialize the color palette
    Args:
      theme (str): 'light' or 'dark' or 'automatic'
    """
    if theme in ['light', 'dark']:
      self.qtheme = theme
    else:
      autoTheme = darkdetect.theme().lower()
      if autoTheme in ['light', 'dark']:
        self.qtheme = autoTheme
      else:
        print(f"DEBUG: darkdetect.theme().lower()={autoTheme} is not recognized")
        self.qtheme = 'light'
    self.primary = self.getThemeColor("primary", "base")
    self.text = self.getThemeColor("foreground", "base")
    self.leafX = self.getThemeColor("border", "base")
    self.leafO = self.getThemeColor("background", "popup")
    self.leafShadow = "#55000000" # Transparent Black

  def setTheme(self, theme: str = "", saveTheme: bool = True) -> None:
    """
    Update the theme of the whole App.
    Args:
      theme: 'automatic'/'dark'/'light' for the dark/light theme. Empty String ('') for update without changing the theme.
      saveTheme: Whether the theme should be changed permanently or just until theme is updated again.
    """
    cornershape = "sharp" # rounded or sharp
    css = """
    QWidget {
    border-radius: 3px;
    }
    
    QDialogButtonBox {
    min-height: 30px;
    padding-bottom: 25px;
    }
    """
    customColors={}#{"background":"#1E3057"}
    if theme == "automatic":
      theme = darkdetect.theme().lower()
    if theme not in ["dark", "light", ""]:
      print("Could not find Theme:", theme)
      return
    if theme != "" and saveTheme:
      self.qtheme = theme
    if theme != "" and not saveTheme:
      qdarktheme.setup_theme(theme, additional_qss=css, corner_shape=cornershape, custom_colors=customColors)
    else:
      qdarktheme.setup_theme(self.qtheme, additional_qss=css, corner_shape=cornershape, custom_colors=customColors)

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
      "primary": self.getThemeColor("primary", "base"),
      "primaryLight": "",
      "secondary": "",
      "secondaryLight": self.getThemeColor("background", "popup"),
      "secondaryDark": self.getThemeColor("background", "table"),
      "primaryText": "",
      "secondaryText": "",
    }
    if color == 'buttonText':
      return f'{prefix}: {self.text}; '
    if colors[color] == "":
      return ""
    return f'{prefix}: {colors[color]}; '

  def getThemeColor(self, category: str, subcategory: str) -> str:
    """
    Returns the computed QColor from the PyQtDarkTheme dict.
    Look at THEME_COLOR_VALUES in fixedStringsJson.py for all possible Categories

    Args:
        category: first level of dict, e.g., "background", "foreground", "primary"
        subcategory: second level of dict, e.g., "base", "panel", "icon", "button.hoverBackground"
    Returns:
        QColor: the computed color
    """
    # 1. Determine base color
    themeDict = THEME_COLOR_VALUES[self.qtheme]
    cat = themeDict.get(category, {})
    if isinstance(cat, str):
      if len(cat) > 7: # Colors in THEME_COLOR_VALUES are #RGBA, not #ARGB like QColor wants.
        cat = rgba_to_argb(cat)
      return QColor(cat).name(format=QColor.NameFormat.HexArgb)
    baseHex = cat.get("base", "#000000")
    color = QColor(baseHex)

    # 2. Get the specific key
    rule = cat.get(subcategory, {})

    # 3. If it's a direct hex string
    if isinstance(rule, str):
      return QColor(rule).name()

    # Helper functions
    def _darken(color: QColor, amount: float) -> QColor:
      h, s, v, a = color.getHsv()
      v = max(0, int(v * (1 - amount)))
      return QColor.fromHsv(h, s, v, a)

    def _lighten(color: QColor, amount: float) -> QColor:
      h, s, v, a = color.getHsv()
      v = min(255, int(v * (1 + amount)))
      return QColor.fromHsv(h, s, v, a)

    # 4. If it's a dict with modifiers
    if isinstance(rule, dict):
      # Apply darken/lighten first
      if "darken" in rule:
        color = _darken(color, rule["darken"])
      if "lighten" in rule:
        color = _lighten(color, rule["lighten"])
      # Apply transparency
      if "transparent" in rule:
        alpha = int((1 - rule["transparent"]) * 255)
        color.setAlpha(alpha)
        r, g, b, a = color.getRgb()
        return f"rgba({r}, {g}, {b}, {a})"
      return color.name()

    # 5. Fallback: return base color
    return color.name()
