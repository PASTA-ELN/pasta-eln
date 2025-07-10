""" Dialog that shows a message and possibly an image """
import qtawesome as qta
from PySide6.QtCore import Qt                                              # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QDialog, QVBoxLayout
from .guiStyle import TextButton, Label, Image, widgetAndLayout    # pylint: disable=relative-beyond-top-level

ICON_SIZE = 40                                                             # size of the icon at top of dialog

class MessageDialog(QDialog):
  """ Dialog that shows a message and the progress-bar """
  def __init__(self, parent:QWidget, title:str, text:str, icon:str='', image:str='', minWidth:int=-1) -> None:
    """
    Show message box for little information and possibly an image

    Args:
      parent (QWidget): parent widget (self)
      title (str): title of box
      text (str): text in box
      icon (str): icon: 'Information','Warning','Critical'
      image (str): image to show
      minWidth (int): minimum width of dialog
    """
    super().__init__(parent)
    color = 'red' if icon=='Critical' else '#ffbc00' if icon=='Warning' else '#'
    iconSymbol = qta.icon('fa5s.minus-circle' if icon=='Critical' else
                    'fa5s.exclamation-circle' if icon=='Warning' else
                    'fa5s.info', color='white', scale_factor=1)
    self.setWindowTitle(title)
    if minWidth > 0:
      self.setMinimumWidth(minWidth)
    mainL = QVBoxLayout(self)
    if icon:
      iconLabel = QLabel('')
      iconLabel.setPixmap(iconSymbol.pixmap(ICON_SIZE, ICON_SIZE))
      iconLabel.setStyleSheet(f'background: {color};')
      iconLabel.setMinimumSize(ICON_SIZE, ICON_SIZE)
      mainL.addWidget(iconLabel, alignment=Qt.AlignHCenter)                                     # type: ignore
    if image is not None:
      Image(image, mainL, anyDimension=400)
    textLabel = Label(text, 'h2', mainL)
    if text.startswith('<') and text.endswith('>'):
      textLabel.setTextFormat(Qt.TextFormat.RichText)
      text = text.replace('<font color="black">',f'<font color="{parent.comm.palette.get("secondaryText", "").strip()[2:-1]}">')# type: ignore[attr-defined]
      textLabel.setText(text)
    else:
      textLabel.setTextFormat(Qt.TextFormat.MarkdownText)
    # final button box
    _, buttonLineL = widgetAndLayout('H', mainL, 'm', 'm', '0', 'm', 's')
    self.copyButton = TextButton('Copy message', parent, None, buttonLineL, 'Copy to clipboard')
    self.copyButton.clicked.connect(lambda: self.copyToClipboard(text))
    buttonLineL.addStretch(2)
    self.okButton   = TextButton('OK',   parent, None, buttonLineL, 'Accept')
    self.okButton.clicked.connect(self.accept)
    self.setMinimumWidth(800)


  def copyToClipboard(self, text:str) -> None:
    """ Copy text to clipboard
    Args:
      text (str): text to copy
    """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)


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
