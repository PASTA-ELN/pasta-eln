""" Dialog that shows a message and possibly an image """
from enum import Enum, auto
from typing import Any
import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget
from .gui_style import Image, Label
from ..text_tools.handle_dictionaries import dict2ul
from .widget import SPACE, Button, ButtonStyle

iconSize = 40                                                              # size of the icon at top of dialog

class MessageDialog(QDialog):
  """ Dialog that shows a message and the progress-bar """
  def __init__(self, parent:QWidget | None, title:str, text:str | dict[str, Any], icon:str='', image:str='',
               minWidth:int=-1, style:str='') -> None:
    """
    Show message box for little information and possibly an image

    Args:
      parent (QWidget): parent widget (self)
      title (str): title of box
      text (str | dict): text or sectioned content in box
      icon (str): icon: 'Information','Warning','Critical'
      image (str): image to show
      minWidth (int): minimum width of dialog
      style (str): additional style sheet
    """
    super().__init__(parent)
    self.comm:Any = getattr(parent, 'comm', None)
    color = 'red' if icon=='Critical' else '#ffbc00' if icon=='Warning' else '#'
    iconSymbol = qta.icon('fa5s.minus-circle' if icon=='Critical' else
                    'fa5s.exclamation-circle' if icon=='Warning' else
                    'fa5s.info', color='white', scale_factor=1)
    self.setWindowTitle(title)
    if style:
      self.setStyleSheet(style)
    if minWidth > 0:
      self.setMinimumWidth(minWidth)
    else:
      self.setMinimumWidth(800)
    mainL = QVBoxLayout(self)
    mainL.setContentsMargins(SPACE.M, SPACE.M, SPACE.M, SPACE.M)
    mainL.setSpacing(SPACE.S)
    if icon:
      iconLabel = QLabel('')
      iconLabel.setPixmap(iconSymbol.pixmap(iconSize, iconSize))
      if color!='#':
        iconLabel.setStyleSheet(f'background: {color};')
      iconLabel.setMinimumSize(iconSize, iconSize)
      mainL.addWidget(iconLabel, alignment=Qt.AlignHCenter)                                     # type: ignore
    if image:
      Image(image, mainL, anyDimension=400)
    if isinstance(text, dict):
      self.messageText = dict2ul(text)
      sectionsWidget = QWidget()
      sectionsLayout = QVBoxLayout(sectionsWidget)
      sectionsLayout.setContentsMargins(SPACE.S, SPACE.S, SPACE.S, SPACE.S)
      sectionsLayout.setSpacing(SPACE.S)
      cssStyle = ('<style> ul {list-style-type: none; padding-left: 0; margin: 0; '
                  'text-indent: -20px; padding-left: -20px;} </style>')
      for sectionTitle, sectionContent in text.items():
        Label(sectionTitle, 'h2', sectionsLayout)
        sectionLabel = QLabel(cssStyle + dict2ul(sectionContent))
        sectionLabel.setWordWrap(True)
        sectionLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        sectionsLayout.addWidget(sectionLabel)
      scrollArea = QScrollArea(widgetResizable=True)
      scrollArea.setWidget(sectionsWidget)
      mainL.addWidget(scrollArea, stretch=1)
    else:
      self.messageText = text
      textLabel = Label(text, 'h2', mainL)
      if text.startswith('<') and text.endswith('>'):
        textLabel.setTextFormat(Qt.TextFormat.RichText)
        if self.comm is not None:
          text = text.replace('<font color="black">',
                              f'<font color="{self.comm.palette.get("secondaryText", "").strip()[2:-1]}">')
        textLabel.setText(text)
      else:
        textLabel.setTextFormat(Qt.TextFormat.MarkdownText)
    buttonLineL = QHBoxLayout()
    buttonLineL.setContentsMargins(0, SPACE.S, 0, 0)
    self.copyButton = Button('Copy message', self, Command.COPY, buttonLineL, tooltip='Copy to clipboard')
    buttonLineL.addStretch(2)
    self.okButton = Button('OK', self, Command.ACCEPT, buttonLineL, tooltip='Accept', style=ButtonStyle.HIGHLIGHTED)
    mainL.addLayout(buttonLineL)


  def copyToClipboard(self, text:str) -> None:
    """ Copy text to clipboard
    Args:
      text (str): text to copy
    """
    if text.startswith('<') and text.endswith('>'):
      doc = QTextDocument()
      doc.setHtml(text)
      text = doc.toPlainText()
    clipboard = QApplication.clipboard()
    clipboard.setText(text)


  def execute(self, command:'Command') -> None:
    """Handle actions in the message footer."""
    if command is Command.COPY:
      self.copyToClipboard(self.messageText)
    elif command is Command.ACCEPT:
      self.accept()


class Command(Enum):
  """Commands available in the message dialog."""
  COPY = auto()
  ACCEPT = auto()


def showMessage(parent:QWidget, title:str, text:str, icon:str='', image:str='', minWidth:int=-1) -> None:
  """
  Show message box for little information and possibly an image

  Args:
    parent (QWidget): parent widget (self)
    title (str): title of box
    text (str): text in box
    icon (str): icon: 'Information','Warning','Critical'
    image (Any): image to show
    minWidth (int): minimum width of dialog
  """
  dialogM = MessageDialog(parent, title, text, icon, image, minWidth)
  dialogM.exec()
