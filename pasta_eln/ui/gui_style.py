""" all styling of buttons and other general widgets, some defined colors... """
import logging
from collections.abc import Callable
from enum import Enum, auto
from typing import Any, Final, Literal, Protocol
import qtawesome as qta
from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QImage, QMouseEvent, QPixmap, QShortcut
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame, QLabel, QLayout, QPushButton, QSizePolicy, QVBoxLayout, QWidget


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
    """Create a command button and optionally add it to a layout.

    Args:
      label (str): Text shown on the button; an empty label creates an icon-only button.
      widget (CommandHost): Command host that receives the button's command.
      command (Any | None): Command passed to the host when the button is clicked.
      layout (QLayout | None): Optional layout to which the button is added.
      icon (str | None): Optional QtAwesome icon name.
      tooltip (str): Optional explanatory text shown on hover.
      style (ButtonStyle): Visual role controlling button emphasis and icon color.
      iconSize (Literal['m', 'l']): Named size of the icon-only or displayed icon button.
      flat (bool): Whether the button should omit its default frame.
      checkable (bool): Whether the button maintains a checked state.
    """
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


class CollapsibleSection(QFrame):
  """A titled section whose content can be shown or hidden."""

  def __init__(self, title: str, contentWidget: QWidget, *, expanded: bool = True,
               iconSize: QSize = QSize(16, 16), boldTitle: bool = False,
               outlined: bool = False) -> None:
    """

    Args:
      title (str): title of the section
      contentWidget (QWidget): widget to be shown or hidden
      expanded (bool): whether the section should be expanded by default
      iconSize (QSize): size of the icon
      boldTitle (bool): whether the title should be bold
      outlined (bool): whether the section should be outlined
    """
    super().__init__()
    self.title = title
    self.contentWidget = contentWidget
    self.outlined = outlined

    self.toggle = QPushButton(title)
    self.toggle.setCheckable(True)
    self.toggle.setFlat(True)
    self.toggle.setIconSize(iconSize)
    titleStyle = ' font-weight: bold;' if boldTitle else ''
    self.toggle.setStyleSheet(f'text-align: left; border: 0; padding: 6px 0;{titleStyle}')
    self.toggle.clicked.connect(self.setExpanded)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(4, 0, 4, 4)
    layout.setSpacing(0)
    layout.addWidget(self.toggle)
    layout.addWidget(self.contentWidget)

    self.setExpanded(expanded)

  def setExpanded(self, expanded: bool) -> None:
    """Show or hide the content and update the disclosure icon
    Args:
      expanded (bool): True if the content should be shown, False otherwise
    """
    self.toggle.setChecked(expanded)
    self.contentWidget.setVisible(expanded)
    iconName = 'ri.arrow-drop-down-line' if expanded else 'ri.arrow-drop-right-line'
    self.toggle.setIcon(qta.icon(iconName))
    if self.outlined:
      self.setFrameShape(QFrame.Shape.NoFrame if expanded else QFrame.Shape.Box)
      self.setFrameShadow(QFrame.Shadow.Plain)
      self.setLineWidth(1)


def shortcut(key: str, parent: QWidget, function: Callable[[], None]) -> QShortcut:
  """Create a keyboard shortcut owned by ``parent``.
    Args:
      key (str): shortcut key (e.g. Ctrl+K)
      parent (QWidget): widget / dialog that host the button and that has the execute function
      function (callable): function to be called when shortcut is triggered
  """
  shortcutObject = QShortcut(key, parent)                                    # pylint: disable=qt-local-widget
  shortcutObject.activated.connect(function)
  return shortcutObject


def image(data: str, layout: QLayout | None, width: int = -1, height: int = -1,
          anyDimension: int = -1) -> QWidget | None:
  """Create an image widget from base64 raster or SVG data and add it to a layout.
    Args:
      data (str): image data in byte64-encoding or svg-encoding
      layout (QLayout): to be added to this layout
      width (int): width of image, dominant if both are given
      height (int): height of image
      anyDimension (int): maximum size in any direction
  """
  if data.startswith('data:image/'):
    try:
      byteArr = QByteArray.fromBase64(bytearray(data[22:] if data[21] == ',' else data[23:], encoding='utf-8'))
      imageW = QImage.fromData(byteArr.data())
      if imageW.isNull():
        logging.warning('Could not load image data')
        return None
      pixmap = QPixmap.fromImage(imageW)
      if height > 0:
        pixmap = pixmap.scaledToHeight(height)
      if width > 0:
        pixmap = pixmap.scaledToWidth(width)
      if anyDimension > 0:
        width0 = max(1, pixmap.size().width())
        height0 = max(1, pixmap.size().height())
        if height0 > width0:
          pixmap = pixmap.scaledToHeight(min(anyDimension, height0 * 2))
        else:
          pixmap = pixmap.scaledToWidth(min(anyDimension, width0 * 2))
      label = QLabel()
      label.setPixmap(pixmap)
      label.setAlignment(Qt.AlignCenter)                                                        # type: ignore
      if layout is not None:
        layout.addWidget(label, alignment=Qt.AlignHCenter)                                      # type: ignore
      return label
    except Exception as error:
      logging.warning('Error processing base64 image %s', error)
      return None
  if data.startswith('<?xml'):
    imageSVG = QSvgWidget()
    policy = imageSVG.sizePolicy()
    policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
    policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
    imageSVG.setSizePolicy(policy)
    imageSVG.load(bytearray(data, encoding='utf-8'))
    if height > 0:
      imageSVG.setMaximumSize(int(float(imageSVG.width()) / float(imageSVG.height()) * height), height)
    if width > 0:
      imageSVG.setMaximumSize(width, int(float(imageSVG.height()) / float(imageSVG.width()) * width))
    if anyDimension > 0:
      if imageSVG.height() > imageSVG.width():
        imageSVG.setMaximumSize(int(float(imageSVG.width()) / float(imageSVG.height()) * anyDimension), anyDimension)
      else:
        imageSVG.setMaximumSize(anyDimension, int(float(imageSVG.height()) / float(imageSVG.width()) * anyDimension))
    if layout is not None:
      layout.addWidget(imageSVG, alignment=Qt.AlignHCenter)                                     # type: ignore
    return imageSVG
  if len(data) > 2:
    logging.error('gui_style.Image: %s', data[:50], exc_info=True)
  return None


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


class HSeparator(QFrame):
  """
  Horizontal Separator
  """
  def __init__(self) -> None:
    super().__init__()
    self.setFrameShape(QFrame.Shape.HLine)
    self.setFrameShadow(QFrame.Shadow.Sunken)
    self.setLineWidth(1)
