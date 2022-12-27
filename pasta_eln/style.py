from PySide6.QtWidgets import QPushButton
import qtawesome as qta

class TextButton(QPushButton):
  def __init__(self, label, function, name='', tooltip=''):
    super().__init__()
    self.setText(label)
    self.clicked.connect(function)
    if name != '':
      self.setAccessibleName(name)
    if tooltip != '':
      self.setToolTip(tooltip)


class LetterButton(QPushButton):
  def __init__(self, label, function, name=''):
    super().__init__()
    self.setText(label[0])
    self.clicked.connect(function)
    self.setToolTip(label)
    if name != '':
      self.setAccessibleName(name)


class IconButton(QPushButton):
  def __init__(self, iconName, function, name='', tooltip=''):
    super().__init__()
    icon = qta.icon(iconName, color='blue', scale_factor=1.2)
    self.setIcon(icon)
    self.setText('')
    self.clicked.connect(function)
    if name != '':
      self.setAccessibleName(name)
    if tooltip != '':
      self.setToolTip(tooltip)

# from qt_material import get_theme
# get_theme('dark_blue.xml')