"""Common command-host widgets and buttons for the user interface.

The classes in this module deliberately keep a concise construction style  while giving every interactive host
the same ``execute`` interface.
"""
from collections.abc import Callable
from enum import Enum, auto
from typing import Any, Final, Literal
import qtawesome
from PySide6.QtCore import QSize
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import QLayout, QPushButton, QWidget


class _Spacing:
  """Shared layout distances, in logical pixels."""
  S: Final[int] = 4
  M: Final[int] = 12
  L: Final[int] = 36
SPACE = _Spacing()


class Widget(QWidget):
  """Base class for widgets that receive commands from child controls"""
  comm: Any

  def execute(self, command: Any) -> None:
    """Handle a command issued by a child control

    Args:
      command: command to handle
    """
    raise NotImplementedError(f'{type(self).__name__} does not handle commands')



class ButtonStyle(Enum):
  """The visual role of a :class:`Button`."""
  DEFAULT     = auto()                                     # follows the active Qt theme without local styling
  HIGHLIGHTED = auto()                                                   # uses Qt's default-button appearance
  PRIMARY     = auto()   # keeps the normal button background and applies the theme primary colour to its icon


class Button(QPushButton):
  """A command button that optionally adds itself to a layout"""
  def __init__(self, label: str, widget: Widget, command: Any | None = None,
               layout: QLayout | None = None, *, icon: str | None = None,
               tooltip: str = '', style: ButtonStyle = ButtonStyle.DEFAULT,
               iconSize: Literal['m', 'l'] = 'm', flat: bool = False) -> None:
    """
    Create a new button

    Args:
      label (str): The label to display on the button
      widget (Widget): widget that will handle commands from this button
      command (Any | None): command to send to the widget when the button is clicked
      layout (QLayout | None): layout to add the button to
      icon (str | None): icon to display on the button
      tooltip (str): tooltip to display when the button is hovered
      style (ButtonStyle): style of the button
      iconSize (Literal['m', 'l']): size of the icon ('m' or 'l')
      flat (bool): whether the button should be flat
    """
    super().__init__(label)
    self.iconName = icon
    self.iconStyle = style
    self.buttonIconSize = QSize(32,32) if iconSize=='l' else QSize(20,20)
    self.setAutoDefault(False)
    self.setDefault(style is ButtonStyle.HIGHLIGHTED)
    self.setFlat(flat)
    if not label:
      self.setFixedSize(self.buttonIconSize)
    if command is not None:
      self.clicked.connect(lambda: widget.execute(command))
    if tooltip:
      self.setToolTip(tooltip)
    if icon is not None:
      self.reloadIcon(widget)
    if layout is not None:
      layout.addWidget(self)


  def reloadIcon(self, widget: Widget) -> None:
    """Refresh the icon after the application theme changes

    Args:
      widget (Widget): widget that the button belongs to
    """
    if self.iconName is not None:
      color = widget.comm.palette.getThemeColor('foreground', 'base')
      if self.iconStyle is ButtonStyle.HIGHLIGHTED:
        color = widget.comm.palette.getThemeColor('background', 'base')
      if self.iconStyle is ButtonStyle.PRIMARY:
        color = widget.comm.palette.getThemeColor('primary', 'base')
      self.setIcon(qtawesome.icon(self.iconName, color=color))
      self.setIconSize(self.buttonIconSize)


class Shortcut(QShortcut):
  """Keyboard shortcut which can be added to a widget"""
  def __init__(self, key:str, parent: QWidget, function:Callable[[], None]) -> None:
    """Create a new shortcut

    Args:
      key (str): key combination for the shortcut, using key.parseKeyBinding
      parent (QWidget): widget that the shortcut belongs to
      function (Callable[[], None]): function to call when the shortcut is triggered
    """
    super().__init__(key, parent)
    self.activated.connect(function)
