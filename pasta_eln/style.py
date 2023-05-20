""" all styling of buttons and other general widgets, some defined colors... """
from typing import Callable, Optional
from PySide6.QtWidgets import QPushButton, QLabel, QSizePolicy, QMessageBox, QLayout, QWidget, QMenu # pylint: disable=no-name-in-module
from PySide6.QtGui import QImage, QPixmap, QAction, QKeySequence, QMouseEvent  # pylint: disable=no-name-in-module
from PySide6.QtCore import QByteArray, Qt           # pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget         # pylint: disable=no-name-in-module
import qtawesome as qta
from qt_material import get_theme
from .backend import Backend

def getColor(backend:Backend, color:str) -> str:
  """
  get color from theme

  Args:
    backend (Pasta): backend instance
    color (str): color to get [primary, primaryLight, secondary, secondaryLight, secondaryDark, primaryText, secondaryText]

  Returns:
    str: #123456 color code
  """
  if hasattr(backend, 'configuration'):
    themeName = backend.configuration['GUI']['theme']
  else:
    themeName = 'none'
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
  def __init__(self, label:str, function:Optional[Callable[[],None]], layout:Optional[QLayout], name:str='',
               tooltip:str='', checkable:bool=False, style:str='', hide:bool=False):
    """
    Args:
      label (str): label printed on button
      function (function): function to be called upon button-click-event
      layout (QLayout): button to be added to this layout
      name (str): name used for button identification in called-function
      tooltip (str): tooltip shown when mouse hovers the button
      checkable (bool): can the button change its background color
      style (str): css style
      hide (bool): hidden or shown initially
    """
    super().__init__()
    self.setText(label)
    self.setCheckable(checkable)
    self.setChecked(checkable)
    self.clicked.connect(function)
    if name != '':
      self.setAccessibleName(name)
    if tooltip != '':
      self.setToolTip(tooltip)
    if style != '':
      self.setStyleSheet(style)
    if hide:
      self.hide()
    if layout is not None:
      layout.addWidget(self)


class LetterButton(QPushButton):
  """ Button that has only a letter"""
  def __init__(self, label:str, function:Callable[[],None], layout:QLayout, name:str='',
               style:str='', hide:bool=False):
    """
    Args:
      label (str): label printed on button
      function (function): function to be called upon button-click-event
      layout (QLayout): button to be added to this layout
      name (str): name used for button identification in called-function
      style (str): css style
      hide (bool): hidden or shown initially
    """
    super().__init__()
    self.setText(label[0])
    self.clicked.connect(function)
    self.setToolTip(label)
    if name != '':
      self.setAccessibleName(name)
    if style != '':
      self.setStyleSheet(style)
    if hide:
      self.hide()
    if layout is not None:
      layout.addWidget(self)


class IconButton(QPushButton):
  """ Button that has only an icon"""
  def __init__(self, iconName:str, function:Callable[[],None], layout:Optional[QLayout], name:str='',
               tooltip:str='', backend:Optional[Backend]=None, style:str='', hide:bool=False, text:str=''):
    """
    Args:
      iconName (str): icon to show on button
      function (function): function to be called upon button-click-event
      layout (QLayout): button to be added to this layout
      name (str): name used for button identification in called-function
      tooltip (str): tooltip shown when mouse hovers the button
      backend (Pasta): pasta backend
      style (str): css style
      hide (bool): hidden or shown initially
      text (str): text shown on button additionally  #TODO_P3 design: what is the difference to TextButton?
    """
    super().__init__()
    color = 'black' if backend is None else getColor(backend, 'primary')
    icon = qta.icon(iconName, color=color, scale_factor=1)
    self.setIcon(icon)
    self.setText(text)
    self.clicked.connect(function)
    self.setFixedHeight(30)
    if name != '':
      self.setAccessibleName(name)
    if tooltip != '':
      self.setToolTip(tooltip)
    if style != '':
      self.setStyleSheet(style)
    if hide:
      self.hide()
    if layout is not None:
      layout.addWidget(self)


class Action(QAction):
  """ QAction and assign function to menu"""
  def __init__(self, label:str, function:Callable[[],None], menu:QMenu, parent:QWidget,
               shortcut:Optional[str]=None, name:Optional[str]=None):
    """
    Args:
      label (str): label printed on submenu
      function (function): function to be called
      menu (QMenu): button to be added to this menu
      parent (QWidget): parent widget
      shortcut (str): shortcut (e.g. Ctrl+K)
      name (str): additional data to transport
    """
    super().__init__()
    self.setParent(parent)
    self.setText(label)
    self.triggered.connect(function)
    if menu is not None:
      menu.addAction(self)
    if shortcut is not None:
      self.setShortcut(QKeySequence(shortcut))
    if name is not None:
      self.setData(name)


class Image():
  """ Image widget depending on type of data """
  def __init__(self, data:str, layout:QLayout, width:int=-1, height:int=-1, anyDimension:int=-1):
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
      imageW.loadFromData(byteArr, format=imageType[:-1] if imageType.endswith(';') else imageType)   # type: ignore
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
      layout.addWidget(label)
    elif data.startswith('<?xml'): #svg image
      imageW = QSvgWidget()
      policy = imageW.sizePolicy()
      policy.setHorizontalPolicy(QSizePolicy.Fixed)
      policy.setVerticalPolicy(QSizePolicy.Fixed)
      imageW.setSizePolicy(policy)
      imageW.renderer().load(bytearray(data, encoding='utf-8'))
      if height>0:
        imageW.setMaximumSize(int(float(imageW.width())/float(imageW.height())*height) ,height)
      if width>0:
        imageW.setMaximumSize(width, int(float(imageW.height())/float(imageW.width())*width))
      if anyDimension>0:
        if imageW.height()>imageW.width():
          imageW.setMaximumSize(int(float(imageW.width())/float(imageW.height())*anyDimension) ,anyDimension)
        else:
          imageW.setMaximumSize(anyDimension, int(float(imageW.height())/float(imageW.width())*anyDimension))
      layout.addWidget(imageW)
      layout.setAlignment(Qt.AlignCenter)  # type: ignore
    elif len(data)>2:
      print('WidgetProjectLeaf:What is this image |'+data[:50]+'|')
    return


class Label(QLabel):
  """ Label widget: headline, ... """
  def __init__(self, text:str='', size:str='', layout:Optional[QLayout]=None,
               function:Optional[Callable[[str, str],None]]=None, docID:str=''):
    """
    Args:
      text (str): text on label
      size (str): size ['h1']
      layout (QLayout): layout to which to add the label
      function (function): function to call on mouse click
      docID (str): docID on other string to connect to this label
    """
    super().__init__()
    self.setText(text)
    if size == 'h1' :
      self.setStyleSheet('font-size: 14pt')
    if layout is not None:
      layout.addWidget(self)
    self.mouseFunction = function
    self.identifier = docID
    return

  def mousePressEvent(self, e:QMouseEvent) -> None:
    """
    Event after mouse press: only use internal members, not the event itself
    """
    if self.mouseFunction is not None:
      self.mouseFunction(self.text(), self.identifier)
    return



def showMessage(parent:QWidget, title:str, text:str, icon:str='', style:str='') -> None:
  """
  Show a message box

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
  if icon in ['Information','Warning','Critical']:
    dialog.setIcon(getattr(QMessageBox, icon))
  if style!='':
    dialog.setStyleSheet(style)
  dialog.exec()
  return
