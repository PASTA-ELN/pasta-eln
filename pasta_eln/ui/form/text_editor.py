"""Plain text editor with line movement and inline spellchecking"""
import re
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import (QAction, QContextMenuEvent, QKeyEvent, QSyntaxHighlighter, QTextCharFormat, QTextCursor,
                           QTextDocument)
from PySide6.QtWidgets import QMenu, QPlainTextEdit
from spellchecker import SpellChecker


class _SpellHighlighter(QSyntaxHighlighter):
  """Highlight misspelled words in an editor document"""
  def __init__(self, document:QTextDocument, checker:SpellChecker):
    """Create a highlighter for a text document
    Args:
      document (QTextDocument): Document whose text should be highlighted
      checker (SpellChecker): Spellchecker used to identify unknown words
    """
    super().__init__(document)
    self.checker = checker
    self.wordPattern = QRegularExpression(r"\b[\w']+\b")
    self.spellFormat = QTextCharFormat()
    self.spellFormat.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
    self.spellFormat.setUnderlineColor(Qt.GlobalColor.red)


  def highlightBlock(self, text:str) -> None:
    """Underline words absent from the configured dictionary
    Args:
      text (str): One block of document text supplied by Qt
    """
    match = self.wordPattern.match(text)
    while match.hasMatch():
      word = match.captured()
      if word.lower() in self.checker.unknown([word]):
        self.setFormat(match.capturedStart(), match.capturedLength(), self.spellFormat)
      match = self.wordPattern.match(text, match.capturedEnd())


class TextEditor(QPlainTextEdit):
  """Plain text editor with Alt-Up/Down line movement and spellchecking"""
  def __init__(self, text:str = '', language:str = 'en'):
    """Initialize the editor with text and a pyspellchecker language
    Args:
      text (str): Initial plain text shown in the editor
      language (str): Language name and code, such as ``English (en)``
    """
    super().__init__(text)
    self.setTabStopDistance(20)
    languageCode = re.search(r'\(([a-z]{2})\)$', language)
    self.checker = SpellChecker(
        language=languageCode[1] if languageCode else 'en', distance=1)
    self.highlighter = _SpellHighlighter(self.document(), self.checker)


  def keyPressEvent(self, event:QKeyEvent) -> None:
    """Move selected lines with Alt-Up/Down, otherwise use normal editing
    Args:
      event (QKeyEvent): Key event received from Qt
    """
    if event.key() == Qt.Key_Up and event.modifiers() == Qt.AltModifier:          # type: ignore[attr-defined]
      self.moveSelectedLines(True)
    elif event.key() == Qt.Key_Down and event.modifiers() == Qt.AltModifier:      # type: ignore[attr-defined]
      self.moveSelectedLines(False)
    else:
      super().keyPressEvent(event)


  def contextMenuEvent(self, event:QContextMenuEvent) -> None:
    """Add spelling suggestions for the word under the context-menu cursor
    Args:
      event (QContextMenuEvent): Context-menu event received from Qt
    """
    menu = self.createStandardContextMenu()
    cursor = self.cursorForPosition(event.pos())
    cursor.select(QTextCursor.SelectionType.WordUnderCursor)
    word = cursor.selectedText()
    if word and word.lower() in self.checker.unknown([word]):
      spellingMenu = QMenu('Spelling suggestions', menu)
      menu.addMenu(spellingMenu)
      suggestions = self.checker.candidates(word) or set()
      for suggestion in sorted(suggestions)[:5]:
        action = QAction(suggestion, menu)
        action.triggered.connect(lambda _checked=False, replacement=suggestion, target=cursor:
                                 self.replaceWord(target, replacement))
        spellingMenu.addAction(action)
    menu.exec(event.globalPos())


  def replaceWord(self, cursor:QTextCursor, replacement:str) -> None:
    """Replace one misspelled word selected for the context menu
    Args:
      cursor (QTextCursor): Cursor selecting the misspelled word
      replacement (str): Corrected text to insert
    """
    current = self.textCursor()
    current.setPosition(cursor.selectionStart())
    current.setPosition(cursor.selectionEnd(), QTextCursor.MoveMode.KeepAnchor)
    self.setTextCursor(current)
    current.insertText(replacement)


  def moveSelectedLines(self, moveUp:bool) -> None:
    """Move the selected lines up or down by one line
    Args:
      moveUp (bool): Whether to move the selected lines towards the document start. Else move down
    """
    # define cursor; initial start and end position
    cursor = self.textCursor()                                                   # Get the current text cursor
    if not cursor.hasSelection():                    # Expand selection to full lines if there is no selection
      cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)       # type: ignore[attr-defined]
    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    # Move the cursor to the start of the first selected line
    cursor.setPosition(start)
    cursor.movePosition(QTextCursor.StartOfBlock)                                 # type: ignore[attr-defined]
    startBlockPos = cursor.position()                             # Store the start of the first selected line

    # Move the cursor to the end of the last selected line
    cursor.setPosition(end)
    if cursor.atBlockStart() and start != end:                    # Adjust selection if it ends at a new block
      cursor.movePosition(QTextCursor.PreviousBlock)                              # type: ignore[attr-defined]
    cursor.movePosition(QTextCursor.EndOfBlock)                                   # type: ignore[attr-defined]
    endBlockPos = cursor.position()                                  # Store the end of the last selected line

    # Select the entire block of selected lines
    cursor.setPosition(startBlockPos)
    cursor.setPosition(endBlockPos+1, QTextCursor.KeepAnchor)                     # type: ignore[attr-defined]
    selectedText = cursor.selection().toPlainText()                                    # Get the selected text
    cursor.removeSelectedText()

    # Move to the previous / next block (line above/below the selected text)
    cursor.setPosition(startBlockPos)
    if cursor.atStart():                                 # If we are at the very first line, we cannot move up
      return
    cursor.movePosition(QTextCursor.PreviousBlock if moveUp else QTextCursor.NextBlock)# type: ignore[attr-defined]
    cursor.insertText(selectedText)                             # Replace the previous line with selected text
    return
