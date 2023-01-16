""" all styling of buttons and other general widgets, some defined colors... """
from PySide6.QtWidgets import QPushButton   # pylint: disable=no-name-in-module
import qtawesome as qta
from qt_material import get_theme


def getColor(backend, color):
  """
  get color from theme

  Args:
    backend (Pasta): backend instance
    color (str): color to get [primary, primaryLight, secondary, secondaryLight, secondaryDark, primaryText, secondaryText]

  Returns:
    str: #123456 color code
  """
  themeName = backend.configuration['GUI']['theme']
  # theme = get_theme(themeName)
  # print(theme)
  ## For dark-blue:
  ## {'primaryColor': '#448aff', 'primaryLightColor': '#83b9ff', 'secondaryColor': '#232629', 'secondaryLightColor': '#4f5b62',
  ##  'secondaryDarkColor': '#31363b', 'primaryTextColor': '#000000', 'secondaryTextColor': '#ffffff'}
  if themeName == 'none':
    return '#000000'
  return get_theme(themeName+'.xml')[color+'Color']


class TextButton(QPushButton):
  """ Button that has only text"""
  def __init__(self, label, function, name='', tooltip='', checkable=False):
    super().__init__()
    self.setText(label)
    self.setCheckable(checkable)
    self.setChecked(checkable)
    self.clicked.connect(function)
    if name != '':
      self.setAccessibleName(name)
    if tooltip != '':
      self.setToolTip(tooltip)


class LetterButton(QPushButton):
  """ Button that has only a letter"""
  def __init__(self, label, function, name=''):
    super().__init__()
    self.setText(label[0])
    self.clicked.connect(function)
    self.setToolTip(label)
    if name != '':
      self.setAccessibleName(name)


class IconButton(QPushButton):
  """ Button that has only an icon"""
  def __init__(self, iconName, function, name='', tooltip='', backend=None):
    super().__init__()
    color = 'black' if backend is None else getColor(backend, 'primary')
    icon = qta.icon(iconName, color=color, scale_factor=1.2)
    self.setIcon(icon)
    self.setText('')
    self.clicked.connect(function)
    if name != '':
      self.setAccessibleName(name)
    if tooltip != '':
      self.setToolTip(tooltip)
