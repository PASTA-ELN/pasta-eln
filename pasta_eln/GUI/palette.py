""" Color pallette allows easy color access """
from PySide6.QtWidgets import QMainWindow
from qt_material import get_theme

class Palette():
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
      #  - For dark-blue:
      # - {'primaryColor': '#448aff', 'primaryLightColor': '#83b9ff', 'secondaryColor': '#232629', 'secondaryLightColor': '#4f5b62',
      # - 'secondaryDarkColor': '#31363b', 'primaryTextColor': '#000000', 'secondaryTextColor': '#ffffff'}

    if self.subtheme == 'dark':
      self.text       = '#FFFFFF'
      self.leafX      = '#222222'
      self.leafO      = '#333333'
      self.leafShadow = 'black'
    else:
      self.text       = '#000000'
      self.leafX      = '#EEEEEE'
      self.leafO      = '#FFFFFF'
      self.leafShadow = '#AAAAAA'


  def get(self, color, prefix):
    if self.theme=='none':
      return ''
    preString = '' if prefix is None else f'{prefix}:'
    postString = '' if prefix is None else '; '
    return preString+get_theme(f'{self.theme}.xml')[f'{color}Color']+postString

    # self.buttonColor = mainWindow.palette().button().color().red()        # The general button background color. This background can be different from Window as some styles require a different background color for buttons.
    # self.windowColor = mainWindow.palette().window().color()        # A general background color.
    # self.windowColor = mainWindow.palette().windowText().color()    # A general foreground color.
    # self.windowColor = mainWindow.palette().base().color()          # Used mostly as the background color for text entry widgets, but can also be used for other painting - such as the background of combobox drop down lists and toolbar handles. It is usually white or another light color.
    # self.windowColor = mainWindow.palette().alternateBase().color() # Used as the alternate background color in views with alternating row colors (see QAbstractItemView::setAlternatingRowColors()).
    # self.windowColor = mainWindow.palette().toolTipBase().color()   # Used as the background color for QToolTip and QWhatsThis. Tool tips use the Inactive color group of QPalette , because tool tips are not active windows.
    # self.windowColor = mainWindow.palette().toolTipText().color()   # Used as the foreground color for QToolTip and QWhatsThis. Tool tips use the Inactive color group of QPalette , because tool tips are not active windows.
    # self.windowColor = mainWindow.palette().placeholderText().color()   # Used as the placeholder color for various text input widgets. This enum value has been introduced in Qt 5.12
    # self.windowColor = mainWindow.palette().text().color()   # The foreground color used with Base. This is usually the same as the WindowText, in which case it must provide good contrast with Window and Base.
    # self.windowColor = mainWindow.palette().buttonText().color()   # A foreground color used with the Button color.
    # self.windowColor = mainWindow.palette().lightText().color()   #
