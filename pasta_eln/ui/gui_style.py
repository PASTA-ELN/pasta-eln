""" all styling of buttons and other general widgets, some defined colors... """
import logging
from collections.abc import Callable
from enum import Enum, auto
from typing import Any, Final, Literal, Protocol
import qtawesome as qta
from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QAction, QImage, QKeySequence, QMouseEvent, QPixmap, QShortcut
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (QBoxLayout, QFrame, QHBoxLayout, QLabel, QLayout, QMenu, QPushButton,
                               QSizePolicy, QSplitter,
                               QVBoxLayout, QWidget)

class _Spacing:
  """Shared layout distances, in logical pixels."""
  S: Final[int]  = 4
  M: Final[int]  = 12
  L: Final[int]  = 36
  XL: Final[int] = 72
SPACE = _Spacing()


class Widget(QWidget):
  """Base class for widgets that receive commands from child controls."""
  comm: Any

  def execute(self, command: Any) -> None:
    """Handle a command issued by a child control."""
    raise NotImplementedError(f'{type(self).__name__} does not handle commands')


class CommandHost(Protocol):
  """Minimal interface required by controls that dispatch commands."""
  comm: Any

  def execute(self, command: Any) -> None:
    """Handle a command issued by a child control."""


class ButtonStyle(Enum):
  """The visual role of a :class:`Button`."""
  DEFAULT     = auto()
  HIGHLIGHTED = auto()
  PRIMARY     = auto()


class Button(QPushButton):
  """A command button that optionally adds itself to a layout."""
  def __init__(self, label: str, widget: CommandHost, command: Any | None = None,
               layout: QLayout | None = None, *, icon: str | None = None,
               tooltip: str = '', style: ButtonStyle = ButtonStyle.DEFAULT,
               iconSize: Literal['m', 'l'] = 'm', flat: bool = False,
               checkable: bool = False) -> None:
    super().__init__(label)
    self.buttonIconSize = QSize(32,32) if iconSize=='l' else QSize(20,20)
    self.setAutoDefault(False)
    self.setDefault(style is ButtonStyle.HIGHLIGHTED)
    self.setFlat(flat)
    self.setCheckable(checkable)
    if not label:
      self.setFixedSize(self.buttonIconSize)
    if command is not None:
      self.clicked.connect(lambda: widget.execute(command))
    if tooltip:
      self.setToolTip(tooltip)
    if icon is not None:
      color = widget.comm.palette.getThemeColor('foreground', 'base')
      if style is ButtonStyle.HIGHLIGHTED:
        color = widget.comm.palette.getThemeColor('background', 'base')
      if style is ButtonStyle.PRIMARY:
        color = widget.comm.palette.getThemeColor('primary', 'base')
      self.setIcon(qta.icon(icon, color=color))
      self.setIconSize(self.buttonIconSize)
    if layout is not None:
      layout.addWidget(self)


class Shortcut(QShortcut):
  """Keyboard shortcut which can be added to a widget."""
  def __init__(self, key:str, parent: QWidget, function:Callable[[], None]) -> None:
    super().__init__(key, parent)
    self.activated.connect(function)


class Action(QAction):
  """ QAction and assign function to menu"""
  def __init__(self, label:str, widget:QWidget, command:Any,
               menu:QMenu, shortcut:str | None=None, icon:str=''):
    """
    Args:
      label (str): label printed on submenu
      widget (QWidget): widget / dialog that host the button and that has the execute function
      command: value forwarded to the host widget's ``execute`` method
      menu (QMenu): button to be added to this menu
      shortcut (str): shortcut (e.g. Ctrl+K)
      icon (str): icon name
    """
    super().__init__()
    self.setParent(widget)
    self.setText(label)
    def _triggered() -> None:
      """Wrapper around calling the execute function, checking that widget still exists"""
      try:
        # if widget is None or not isValid(widget):
        #   return
        widget.execute(command)                                                   # type: ignore[attr-defined]
      except Exception:
        return
    self.triggered.connect(_triggered)
    if icon:
      color = 'black' if widget is None else widget.comm.palette.text             # type: ignore[attr-defined]
      self.setIcon(qta.icon(icon, color=color, scale_factor=1))
    if shortcut is not None:
      self.setShortcut(QKeySequence(shortcut))
    menu.addAction(self)


class Image():
  """ Image widget depending on type of data """
  def __init__(self, data:str, layout:QLayout | None, width:int=-1, height:int=-1, anyDimension:int=-1):
    """
    Args:
      data (str): image data in byte64-encoding or svg-encoding
      layout (QLayout): to be added to this layout
      width (int): width of image, dominant if both are given
      height (int): height of image
      anyDimension (int): maximum size in any direction
    """
    if data.startswith('data:image/'):                                                      # jpg or png image
      try:
        byteArr = QByteArray.fromBase64(bytearray(data[22:] if data[21]==',' else data[23:], encoding='utf-8'))
        imageW = QImage()
        imageType = data[11:15].upper()
        success = imageW.loadFromData(byteArr, format=imageType[:-1] if imageType.endswith(';') else imageType)#type: ignore[arg-type]
        if not success:
          logging.warning('Could not load image data with format %s', imageType)
          return
        pixmap = QPixmap.fromImage(imageW)
        if height>0:
          pixmap = pixmap.scaledToHeight(height)
        if width>0:
          pixmap = pixmap.scaledToWidth(width)
        if anyDimension>0:
          width0 = max(1, pixmap.size().width())
          height0 = max(1, pixmap.size().height())
          if height0 > width0:
            pixmap = pixmap.scaledToHeight(min(anyDimension, height0*2))
          else:
            pixmap = pixmap.scaledToWidth(min(anyDimension, width0*2))
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)                                                      # type: ignore
        if layout is not None:
          layout.addWidget(label, alignment=Qt.AlignHCenter)                                    # type: ignore
      except Exception as e:
        logging.warning('Error processing base64-image %s', e)
    elif data.startswith('<?xml'):                                                                  #svg image
      imageSVG = QSvgWidget()
      policy = imageSVG.sizePolicy()
      policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
      policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
      imageSVG.setSizePolicy(policy)
      imageSVG.load(bytearray(data, encoding='utf-8'))
      if height>0:
        imageSVG.setMaximumSize(int(float(imageSVG.width())/float(imageSVG.height())*height) ,height)
      if width>0:
        imageSVG.setMaximumSize(width, int(float(imageSVG.height())/float(imageSVG.width())*width))
      if anyDimension>0:
        if imageSVG.height()>imageSVG.width():
          imageSVG.setMaximumSize(int(float(imageSVG.width())/float(imageSVG.height())*anyDimension) ,anyDimension)
        else:
          imageSVG.setMaximumSize(anyDimension, int(float(imageSVG.height())/float(imageSVG.width())*anyDimension))
      if layout is not None:
        layout.addWidget(imageSVG, alignment=Qt.AlignHCenter)                                   # type: ignore
    elif len(data)>2:
      logging.error('guiStyle.Image: %s', data[:50], exc_info=True)
    return


class Label(QLabel):
  """ Label widget: headline, ... """
  def __init__(self, text:str='', size:str='', layout:QLayout | None=None,
               function:Callable[[str, str],None] | None=None, docID:str='', tooltip:str='', style:str=''):
    """ Label widget with given font-size and functions:
    - text selection: if only character, easy selection
      - if formatted text: right-mouse-button to select all (There is no other way, apparently)

    Args:
      text (str): text on label
      size (str): size ['h1','h2','h3']
      layout (QLayout): layout to which to add the label
      function (function): function to call on mouse click
      docID (str): docID on other string to connect to this label
      tooltip (str): tooltip shown when mouse hovers the button
      style (str): css style
    """
    super().__init__()
    self.setText(text)
    if text.startswith('#') or text.startswith('<'):
      self.setTextFormat(Qt.TextFormat.RichText)
    self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
    style += 'border: none;'
    if size == 'h1':
      style += 'font-size: 18pt;'
    elif size == 'h2':
      style += 'font-size: 14pt;'
    elif size == 'h3':
      style += 'font-size: 12pt;'
    if style:
      self.setStyleSheet(style)
    if layout is not None:
      layout.addWidget(self)
    self.mouseFunction = function
    self.identifier = docID
    if tooltip != '':
      self.setToolTip(tooltip)
    return

  def mousePressEvent(self, _:QMouseEvent) -> None:
    """
    Event after mouse press: only use internal members, not the event itself
    """
    if self.mouseFunction is not None:
      self.mouseFunction(self.text(), self.identifier)
    return


def widgetAndLayout(direction:str='V', parentLayout:QLayout |QSplitter | None=None, spacing:str='0', left:str='0',
                    top:str='0', right:str='0', bottom:str='0') -> tuple[QWidget, QBoxLayout]:
  """
  Convenient function for widget and a boxLayout

  Spacings and margins:
  - different than in css/html
  - spacing is the space between elements in the orientation of the BoxLayout
  - is the padding that surrounds the content in the layout

  Distances are given in
  - '0': zero distance
  - 's': small distance used as padding round elements, or vertical spacings
  - 'm': medium used as space between horizontal elements
  - 'l': large used when things need to be separated
  - 'xl': extra large indentations, frames

  Args:
    direction (str): type of layout [H,V]
    parentLayout (QLayout): to which layout should the widget be added. If none, no adding
    spacing (str): spacing
    left (str): padding on left
    top (str): padding on top
    right (str): padding on right
    bottom (str): padding on bottom
  """
  distance = {'0':0, 's':SPACE.S, 'm':SPACE.M, 'l':SPACE.L, 'xl':SPACE.XL}
  widget = QWidget()
  layout = QVBoxLayout(widget) if direction=='V' else QHBoxLayout(widget)
  layout.setSpacing(distance[spacing])
  layout.setContentsMargins(distance[left], distance[top], distance[right], distance[bottom])
  if parentLayout is not None:
    parentLayout.addWidget(widget)
  return widget, layout


class HSeparator(QFrame):
  """
  Horizontal Separator
  """

  def __init__(self) -> None:
    super().__init__()
    self.setFrameShape(QFrame.Shape.HLine)
    self.setFrameShadow(QFrame.Shadow.Sunken)
    self.setLineWidth(1)
