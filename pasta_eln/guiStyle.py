""" all styling of buttons and other general widgets, some defined colors... """
import logging
import re
from typing import Any, Callable, Optional, Union
import qtawesome as qta
from PySide6.QtCore import QByteArray, Qt                                  # pylint: disable=no-name-in-module
from PySide6.QtGui import QAction, QImage, QKeySequence, QMouseEvent, QPixmap# pylint: disable=no-name-in-module
from PySide6.QtSvgWidgets import QSvgWidget                                # pylint: disable=no-name-in-module
from PySide6.QtWidgets import (QApplication, QBoxLayout, QComboBox, QDialog,# pylint: disable=no-name-in-module
                               QFormLayout, QGridLayout, QHBoxLayout, QLabel, QLayout, QMenu, QMessageBox, QPushButton,
                               QScrollArea, QSizePolicy, QSplitter, QTextEdit, QVBoxLayout, QWidget)
from .textTools.handleDictionaries import dict2ul
from .textTools.stringChanges import markdownEqualizer

space = {'0':0, 's':5, 'm':10, 'l':20, 'xl':200}                                  # spaces: padding and margin


class TextButton(QPushButton):
  """ Button that has only text"""
  def __init__(self, label:str, widget:QWidget, command:list[Any]|None=[], layout:Optional[QLayout]=None,
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
    if command is not None:
      self.clicked.connect(lambda: widget.execute(command))                       # type: ignore[attr-defined]
    if tooltip:
      self.setToolTip(tooltip)
    if style:
      self.setStyleSheet(style)
    else:
      primaryColor   = widget.comm.palette.get('primary',  'background-color')    # type: ignore[attr-defined]
      secondaryColor = widget.comm.palette.get('buttonText','color')              # type: ignore[attr-defined]
      self.setStyleSheet(f'border-width: 0px; {primaryColor} {secondaryColor}')
    if hide:
      self.hide()
    if iconName:
      icon = qta.icon(iconName, scale_factor=1)
      self.setIcon(icon)
    if layout is not None:
      layout.addWidget(self)


class IconButton(QPushButton):
  """ Button that has only an icon"""
  def __init__(self, iconName:str, widget:QWidget, command:list[Any]=[], layout:Optional[QLayout]=None,
               tooltip:str='', style:str='', hide:bool=False, checkable:bool=False):
    """
    Args:
      iconName (str): icon to show on button
      widget (QWidget): widget / dialog that host the button and that has the execute function
      command (enum): command that is used in called-function: possibly a list of multiple terms
      layout (QLayout): button to be added to this layout
      tooltip (str): tooltip shown when mouse hovers the button
      style (str): css style
      hide (bool): hidden or shown initially
      checkable (bool): can the button change its background color
    """
    super().__init__()
    icon = qta.icon(iconName, scale_factor=1)                                              # color change here
    self.setIcon(icon)
    self.setCheckable(checkable)
    self.command = command
    self.clicked.connect(lambda: widget.execute(self.command))                    # type: ignore[attr-defined]
    self.setFixedHeight(30)
    if tooltip:
      self.setToolTip(tooltip)
    if style:
      self.setStyleSheet(f'QPushButton {{{style}}} QPushButton:checked {{border: "red"; border-width: 5px; {style}}}')
    else:
      primaryColor   = widget.comm.palette.get('primary', 'background-color')     # type: ignore[attr-defined]
      secondaryColor = widget.comm.palette.get('secondary','color')               # type: ignore[attr-defined]
      self.setStyleSheet(f'QPushButton {{border-width: 0px; {primaryColor} {secondaryColor}}} QPushButton:checked {{border: 3px solid red; {primaryColor} {secondaryColor}}}')
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
    self.triggered.connect(lambda : widget.execute(command))                      # type: ignore[attr-defined]
    if icon:
      color = 'black' if widget is None else widget.comm.palette.secondaryText    # type: ignore[attr-defined]
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
    if data.startswith('data:image/'):                                                      # jpg or png image
      byteArr = QByteArray.fromBase64(bytearray(data[22:] if data[21]==',' else data[23:], encoding='utf-8'))
      imageW = QImage()
      imageType = data[11:15].upper()
      imageW.loadFromData(byteArr, format=imageType[:-1] if imageType.endswith(';') else imageType)#type: ignore[arg-type]
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
      label.setAlignment(Qt.AlignCenter)                                                        # type: ignore
      if layout is not None:
        layout.addWidget(label, alignment=Qt.AlignHCenter)                                      # type: ignore
    elif data.startswith('<?xml'):                                                                  #svg image
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
        layout.addWidget(imageSVG, alignment=Qt.AlignHCenter)                                   # type: ignore
    elif len(data)>2:
      print(f'WidgetProjectLeaf:What is this image |{data[:50]}|')
    return


class Label(QLabel):
  """ Label widget: headline, ... """
  def __init__(self, text:str='', size:str='', layout:Optional[QLayout]=None,
               function:Optional[Callable[[str, str],None]]=None, docID:str='', tooltip:str='', style:str=''):
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
    if size == 'h1':
      style += 'font-size: 14pt'
    elif size == 'h2':
      style += 'font-size: 12pt'
    elif size == 'h3':
      style += 'font-size: 10pt'
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



def showMessage(parent:QWidget, title:str, text:str, icon:str='Information', style:str='') -> None:
  """
  Show simple message box for little information

  Args:
    parent (QWidget): parent widget (self)
    title (str): title of box
    text (str): text in box
    icon (str): icon: 'Information','Warning','Critical'
    style (str): css style
  """
  iconSize = 40
  color = 'red' if icon=='Critical' else '#ffbc00' if icon=='Warning' else '#'
  iconSymbol = qta.icon('fa5s.minus-circle' if icon=='Critical' else
                  'fa5s.exclamation-circle' if icon=='Warning' else
                  'fa5s.info', color='white', scale_factor=1)
  dialog = QDialog(parent)
  dialog.setWindowTitle(title)
  dialogW, dialogL = widgetAndLayout('V', None, 's', top='s', bottom='s', left='s', right='s')
  dialog.setLayout(dialogL)
  label = QLabel('')
  label.setPixmap(iconSymbol.pixmap(iconSize, iconSize))
  label.setStyleSheet(f'background: {color};')
  label.setMinimumSize(iconSize, iconSize)
  dialogL.addWidget(label, alignment=Qt.AlignHCenter)                                           # type: ignore
  label = Label(text, 'h2', dialogL)
  label.setStyleSheet(style)
  if text.startswith('<') and text.endswith('>'):
    label.setTextFormat(Qt.TextFormat.RichText)
    text = text.replace('<font color="black">',f'<font color="{parent.comm.palette.get("secondaryText", "").strip()[2:-1]}">')# type: ignore[attr-defined]
    label.setText(text)
  else:
    label.setTextFormat(Qt.TextFormat.MarkdownText)
  # final button box
  _, buttonLineL = widgetAndLayout('H', dialogL, 'm', 'm', '0', 'm', 's')
  copyButton = TextButton('Copy message', parent, None, buttonLineL, 'Copy to clipboard')
  def copyToClipboard() -> None:
    """ Copy text to clipboard """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
  copyButton.clicked.connect(copyToClipboard)
  buttonLineL.addStretch(2)
  okButton   = TextButton('OK',   parent, None, buttonLineL, 'Accept')
  okButton.clicked.connect(dialog.accept)
  dialogW.setMinimumWidth(800)
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
    self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())                       # type: ignore


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

CSS_STYLE = """
<style> ul {list-style-type: none; padding-left: 0; margin: 0;} a:link {text-decoration: none;}
a:visited {text-decoration: none;} a:hover {text-decoration: none;} a:active {text-decoration: none;} </style>
"""

def addDocDetails(widget:QWidget, layout:QLayout, key:str, value:Any, dataHierarchyNode:list[dict[str,Any]]) -> str:
  """ add document details to a widget's layout: take care of all the formatting

  Args:
    widget (QWidget): widget from which to get the communication
    layout (QLayout): layout to which to add
    key    (str): key/label to add
    value  (Any): information
    dataHierarchyNode (list): information on data-structure

  Returns:
    str: /n separated lines of text
  """
  if not key and isinstance(value,dict):
    return '\n'.join([addDocDetails(widget, layout, k, v, dataHierarchyNode) for k, v in value.items()])
  link = False
  if not value:
    return ''
  labelStr = ''
  if key=='tags':
    rating = ['\u2605'*int(i[1]) for i in value if re.match(r'^_\d$', i)]
    tags = ['_curated_' if i=='_curated' else i for i in value]
    tags = [i for i in tags if not re.match(r'^_\d$', i)]
    labelStr = f'Rating: {rating[0]}' if rating else ''
    labelStr = f'{labelStr}   Tags: '+' '.join(tags)
    if layout is not None:
      label = QLabel(labelStr)
      label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
      layout.addWidget(label)
  elif (isinstance(value,str) and '\n' in value) or key=='comment':          # long values with /s or comments
    labelW, labelL = widgetAndLayout('H', layout, top='s', bottom='s')
    labelL.addWidget(QLabel(f'{key}: '), alignment=Qt.AlignmentFlag.AlignTop)
    text = QTextEdit()
    text.setMarkdown(markdownEqualizer(value))
    bgColor = widget.comm.palette.get('secondaryDark', 'background-color')        # type: ignore[attr-defined]
    fgColor = widget.comm.palette.get('secondaryText', 'color')                   # type: ignore[attr-defined]
    text.setStyleSheet(f"QTextEdit {{ border: none; padding: 0px; {bgColor} {fgColor}}}")
    text.document().setTextWidth(labelW.width())
    if hasattr(widget, 'rescaleTexts'):
      widget.rescaleTexts.append(text)
    height:int = text.document().size().toTuple()[1]                                      # type:ignore[index]
    text.setFixedHeight(height)
    text.setReadOnly(True)
    labelL.addWidget(text, stretch=1)
  else:
    dataHierarchyItems = [dict(i) for i in dataHierarchyNode if i['name']==key]
    docID = ''
    if len(dataHierarchyItems)==1 and 'list' in dataHierarchyItems[0] and dataHierarchyItems[0]['list'] and \
        not isinstance(dataHierarchyItems[0]['list'], list):                             #choice among docType
      table  = widget.comm.backend.db.getView('viewDocType/'+dataHierarchyItems[0]['list'])# type: ignore[attr-defined]
      names= list(table[table.id==value[0]]['name'])
      if len(names)==1:                                                # default find one item that we link to
        docID = value[0]
        value = '\u260D '+names[0]
        link = True
      elif not names:            # likely empty link because the value was not yet defined: just print to show
        value = value[0] if isinstance(value,tuple) else value
      else:
        raise ValueError(f'list target exists multiple times. Key: {key}')
    elif isinstance(value, list):
      value = ', '.join([str(i) for i in value])
    labelStr = f'<b>{key.capitalize()}</b>: {value}'
    if isinstance(value, tuple) and len(value)==4:
      key = key if value[2] is None or value[2]=='' else value[2]
      valueString = f'{value[0]} {value[1]}'
      valueString = valueString if value[3] is None or value[3]=='' else \
                    f'{valueString}&nbsp;<b><a href="{value[3]}">&uArr;</a></b>'
      labelStr = f'{key.capitalize()}: {valueString}<br>'
    if isinstance(value, dict):
      value = {k:(v[0] if isinstance(v, (list,tuple)) else v) for k,v in value.items()}
      labelStr = f'{CSS_STYLE}{key.capitalize()}: {dict2ul(value)}'
    if layout is not None:
      label = Label(labelStr, function=lambda x,y: clickLink(widget,x,y) if link else None, docID=docID)
      label.setOpenExternalLinks(True)
      label.setWordWrap(True)
      layout.addWidget(label)
  return labelStr


def clickLink(widget:QWidget, label:str, docID:str) -> None:
  """
  Click link in details

  Args:
    widget (QWidget): widget to expose the communication
    label (str): label on link
    docID (str): docID to which to link
  """
  logging.debug('used link on %s|%s',label,docID)
  widget.comm.changeDetails.emit(docID)                                           # type: ignore[attr-defined]
  return
