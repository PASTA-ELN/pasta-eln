""" all styling of buttons and other general widgets, some defined colors... """
from typing import Callable, Optional, Any, Union
from PySide6.QtWidgets import QPushButton, QLabel, QSizePolicy, QMessageBox, QLayout, QWidget, QMenu, QSplitter, \
                              QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QBoxLayout, QComboBox, QScrollArea # pylint: disable=no-name-in-module
from PySide6.QtGui import QImage, QPixmap, QAction, QKeySequence, QMouseEvent               # pylint: disable=no-name-in-module
from PySide6.QtCore import QByteArray, Qt           # pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget         # pylint: disable=no-name-in-module
import qtawesome as qta
from qt_material import get_theme
from .backend import Backend
from .handleDictionaries import dict2ul

space = {'0':0, 's':5, 'm':10, 'l':20, 'xl':200} #spaces: padding and margin

def getColor(backend:Backend, color:str) -> str:
  """
  get color from theme
  - Python access: theme = get_theme(themeName)
  - For dark-blue:
     - {'primaryColor': '#448aff', 'primaryLightColor': '#83b9ff', 'secondaryColor': '#232629', 'secondaryLightColor': '#4f5b62',
     - 'secondaryDarkColor': '#31363b', 'primaryTextColor': '#000000', 'secondaryTextColor': '#ffffff'}

  Args:
    backend (Pasta): backend instance
    color (str): color to get [primary, primaryLight, secondary, secondaryLight, secondaryDark, primaryText, secondaryText]

  Returns:
    str: #123456 color code
  """
  if not hasattr(backend, 'configuration') or backend.configuration['GUI']['theme']=='none':
    return '#000000' if color=='primary' else '#BBBBBB'
  themeName = backend.configuration['GUI']['theme']
  return get_theme(f'{themeName}.xml')[f'{color}Color']


class TextButton(QPushButton):
  """ Button that has only text"""
  def __init__(self, label:str, widget:QWidget, command:list[Any]=[], layout:Optional[QLayout]=None,
               tooltip:str='', checkable:bool=False, style:str='', hide:bool=False, iconName:str=''):
    """
    Args:
      label (str): label printed on button
      widget (QWidget): widget / dialog that host the button and that has the execute function
      command (enum): command that is used in called-function: possibly a list of multiple terms
      layout (QLayout): button to be added to this layout
      tooltip (str): tooltip shown when mouse hovers the button
      checkable (bool): can the button change its background color
      style (str): css style
      hide (bool): hidden or shown initially
    """
    super().__init__()
    self.setText(label)
    self.setCheckable(checkable)
    self.setChecked(checkable)
    self.setAutoDefault(False)
    self.setDefault(False)
    self.clicked.connect(lambda: widget.execute(command))                                                    # type: ignore[attr-defined]
    if tooltip:
      self.setToolTip(tooltip)
    if style:
      self.setStyleSheet(style)
    else:
      primaryColor   = getColor(widget.comm.backend, 'primary')                                              # type: ignore[attr-defined]
      secondaryColor = getColor(widget.comm.backend, 'secondary')                                            # type: ignore[attr-defined]
      self.setStyleSheet(f'border-width: 0px; background-color: {primaryColor}; color: {secondaryColor}')
    if hide:
      self.hide()
    if iconName:
      color = 'black' if widget is None else getColor(widget.comm.backend, 'primary')                        # type: ignore[attr-defined]
      icon = qta.icon(iconName, color=color, scale_factor=1)
      self.setIcon(icon)
    if layout is not None:
      layout.addWidget(self)


class IconButton(QPushButton):
  """ Button that has only an icon"""
  def __init__(self, iconName:str, widget:QWidget, command:list[Any]=[], layout:Optional[QLayout]=None,
               tooltip:str='', style:str='', hide:bool=False):
    """
    Args:
      iconName (str): icon to show on button
      widget (QWidget): widget / dialog that host the button and that has the execute function
      command (enum): command that is used in called-function: possibly a list of multiple terms
      layout (QLayout): button to be added to this layout
      tooltip (str): tooltip shown when mouse hovers the button
      style (str): css style
      hide (bool): hidden or shown initially
    """
    super().__init__()
    color = 'black' if widget is None else getColor(widget.comm.backend, 'primary')                          # type: ignore[attr-defined]
    icon = qta.icon(iconName, color=color, scale_factor=1)  #color change here
    self.setIcon(icon)
    self.clicked.connect(lambda: widget.execute(command))                                                    # type: ignore[attr-defined]
    self.setFixedHeight(30)
    if tooltip:
      self.setToolTip(tooltip)
    if style:
      self.setStyleSheet(style)
    else:
      self.setStyleSheet("border-width:0")
    if hide:
      self.hide()
    if layout is not None:
      layout.addWidget(self)


class Action(QAction):
  """ QAction and assign function to menu"""
  def __init__(self, label:str, widget:QWidget, command:list[Any],
               menu:QMenu, shortcut:Optional[str]=None, icon:str=''):
    """
    Args:
      label (str): label printed on submenu
      widget (QWidget): widget / dialog that host the button and that has the execute function
      command (enum): command that is used in called-function: possibly a list of multiple terms
      menu (QMenu): button to be added to this menu
      shortcut (str): shortcut (e.g. Ctrl+K)
      icon (str): icon name
    """
    super().__init__()
    self.setParent(widget)
    self.setText(label)
    self.triggered.connect(lambda : widget.execute(command))                                                 # type: ignore[attr-defined]
    if icon:
      color = 'black' if widget is None else getColor(widget.comm.backend, 'secondaryText')                  # type: ignore[attr-defined]
      self.setIcon(qta.icon(icon, color=color, scale_factor=1))
    if shortcut is not None:
      self.setShortcut(QKeySequence(shortcut))
    menu.addAction(self)


class Image():
  """ Image widget depending on type of data """
  def __init__(self, data:str, layout:Optional[QLayout], width:int=-1, height:int=-1, anyDimension:int=-1):
    """
    Args:
      data (str): image data in byte64-encoding or svg-encoding
      layout (QLayout): to be added to this layout
      width (int): width of image, dominant if both are given
      height (int): height of image
      anyDimension (int): maximum size in any direction
    """
    if data.startswith('data:image/'): #jpg or png image
      byteArr = QByteArray.fromBase64(bytearray(data[22:] if data[21]==',' else data[23:], encoding='utf-8'))
      imageW = QImage()
      imageType = data[11:15].upper()
      imageW.loadFromData(byteArr, format=imageType[:-1] if imageType.endswith(';') else imageType)
      pixmap = QPixmap.fromImage(imageW)
      if height>0:
        pixmap = pixmap.scaledToHeight(height)
      if width>0:
        pixmap = pixmap.scaledToWidth(width)
      if anyDimension>0:
        if pixmap.size().height()>pixmap.size().width():
          pixmap = pixmap.scaledToHeight(anyDimension)
        else:
          pixmap = pixmap.scaledToWidth(anyDimension)
      label = QLabel()
      label.setPixmap(pixmap)
      label.setAlignment(Qt.AlignCenter) # type: ignore
      if layout is not None:
        layout.addWidget(label, alignment=Qt.AlignHCenter)  # type: ignore
    elif data.startswith('<?xml'): #svg image
      imageSVG = QSvgWidget()
      policy = imageSVG.sizePolicy()
      policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
      policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
      imageSVG.setSizePolicy(policy)
      imageSVG.renderer().load(bytearray(data, encoding='utf-8'))
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
        layout.addWidget(imageSVG, alignment=Qt.AlignHCenter) # type: ignore
    elif len(data)>2:
      print(f'WidgetProjectLeaf:What is this image |{data[:50]}|')
    return


class Label(QLabel):
  """ Label widget: headline, ... """
  def __init__(self, text:str='', size:str='', layout:Optional[QLayout]=None,
               function:Optional[Callable[[str, str],None]]=None, docID:str='', tooltip:str=''):
    """
    Args:
      text (str): text on label
      size (str): size ['h1','h2','h3']
      layout (QLayout): layout to which to add the label
      function (function): function to call on mouse click
      docID (str): docID on other string to connect to this label
      tooltip (str): tooltip shown when mouse hovers the button
    """
    super().__init__()
    self.setText(text)
    if size == 'h1':
      self.setStyleSheet('font-size: 14pt')
    elif size == 'h2':
      self.setStyleSheet('font-size: 12pt')
    elif size == 'h3':
      self.setStyleSheet('font-size: 10pt')
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



def showMessage(parent:QWidget, title:str, text:str, icon:str='', style:str='') -> None:
  """
  Show simple message box for little information

  Args:
    parent (QWidget): parent widget (self)
    title (str): title of box
    text (str): text in box
    icon (str): icon: 'Information','Warning','Critical'
    style (str): css style
  """
  dialog = QMessageBox(parent)
  dialog.setWindowTitle(title)
  dialog.setText(text)
  if not (text.startswith('<') and text.endswith('>')):
    dialog.setTextFormat(Qt.TextFormat.MarkdownText)
  if icon in {'Information', 'Warning', 'Critical'}:
    dialog.setIcon(getattr(QMessageBox, icon))
  if style!='':
    dialog.setStyleSheet(style)
  dialog.exec()
  return


class ScrollMessageBox(QMessageBox):
  """ Scrollable message box for lots of dictionary information """
  def __init__(self, title:str, content:dict[str,Any], style:str=''):
    """
    Args:
      title (str): title
      content (dict): dictionary of lots of information
      style (str): css style
    """
    cssStyle = '<style> ul {list-style-type: none; padding-left: 0; margin: 0; text-indent: -20px; padding-left: -20px;} </style>'
    QMessageBox.__init__(self)
    self.setWindowTitle(title)
    if not style:
      self.setStyleSheet('QScrollArea{min-width:300 px; min-height: 400px}')
    else:
      self.setStyleSheet(style)
    scroll = QScrollArea(self)
    scroll.setWidgetResizable(True)
    self.content = QLabel()
    self.content.setWordWrap(True)
    self.content.setText(cssStyle+dict2ul(content))
    self.content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    scroll.setWidget(self.content)
    self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount()) # type: ignore


def widgetAndLayout(direction:str='V', parentLayout:Optional[Union[QLayout,QSplitter]]=None, spacing:str='0', left:str='0',
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
  widget = QWidget()
  layout = QVBoxLayout(widget) if direction=='V' else QHBoxLayout(widget)
  layout.setSpacing(space[spacing])
  layout.setContentsMargins(space[left], space[top], space[right], space[bottom])
  if parentLayout is not None:
    parentLayout.addWidget(widget)
  return widget, layout


def widgetAndLayoutForm(parentLayout:Optional[Union[QLayout,QSplitter]]=None, spacing:str='0', left:str='0',
                    top:str='0', right:str='0', bottom:str='0') -> tuple[QWidget, QFormLayout]:
  """
  Convenient function for widget and a form layout
  - comment see above

  Args:
    parentLayout (QLayout): to which layout should the widget be added. If none, no adding
    spacing (str): spacing
    left (str): padding on left
    top (str): padding on top
    right (str): padding on right
    bottom (str): padding on bottom
  """
  widget = QWidget()
  layout = QFormLayout(widget)
  layout.setSpacing(space[spacing])
  layout.setContentsMargins(space[left], space[top], space[right], space[bottom])
  if parentLayout is not None:
    parentLayout.addWidget(widget)
  return widget, layout


def widgetAndLayoutGrid(parentLayout:Optional[QLayout]=None, spacing:str='0', left:str='0',
                    top:str='0', right:str='0', bottom:str='0') -> tuple[QWidget, QGridLayout]:
  """
  Convenient function for widget and a grid layout
  - comment see above

  Args:
    parentLayout (QLayout): to which layout should the widget be added. If none, no adding
    spacing (str): spacing
    left (str): padding on left
    top (str): padding on top
    right (str): padding on right
    bottom (str): padding on bottom
  """
  widget = QWidget()
  layout = QGridLayout(widget)
  layout.setSpacing(space[spacing])
  layout.setContentsMargins(space[left], space[top], space[right], space[bottom])
  if parentLayout is not None:
    parentLayout.addWidget(widget)
  return widget, layout


def addRowList(layout:QFormLayout, label:str, default:str, itemList:list[str]) -> QComboBox:
  """
  Add a row with a combo-box to the form

  Args:
    layout (QLayout): layout to add row to
    label (str): label used in form
    default (str): default value
    itemList (list(str)): items to choose from

  Returns:
    QCombobox: filled combobox
  """
  widget = QComboBox()
  widget.addItems(itemList)
  widget.setCurrentText(default)
  layout.addRow(QLabel(label), widget)
  return widget
