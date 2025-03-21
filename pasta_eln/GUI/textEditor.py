from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtGui import QTextCursor, QKeyEvent
from PySide6.QtCore import Qt

class TextEditor(QTextEdit):
  def __init__(self, text):
    super().__init__(text)
    self.setTabStopDistance(20)


  def keyPressEvent(self, event: QKeyEvent):
    """
    Captures key press events. If Alt+Up is pressed, move selected lines up.
    Otherwise, call the default behavior.
    """
    if event.key() == Qt.Key_Up and event.modifiers() == Qt.AltModifier:
      self.move_selected_lines(True)
    elif event.key() == Qt.Key_Down and event.modifiers() == Qt.AltModifier:
      self.move_selected_lines(False)
    else:
      super().keyPressEvent(event)


  def move_selected_lines(self, moveUp):
    """Moves the selected lines up by swapping them with the previous line."""
    # define cursor; initial start and end position
    cursor = self.textCursor()  # Get the current text cursor
    if not cursor.hasSelection():  # Expand selection to full lines if there is no selection
      cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    # Move the cursor to the start of the first selected line
    cursor.setPosition(start)
    cursor.movePosition(QTextCursor.StartOfBlock)
    start_block_pos = cursor.position()  # Store the start of the first selected line

    # Move the cursor to the end of the last selected line
    cursor.setPosition(end)
    if cursor.atBlockStart() and start != end:
      cursor.movePosition(QTextCursor.PreviousBlock)  # Adjust selection if it ends at a new block
    cursor.movePosition(QTextCursor.EndOfBlock)
    end_block_pos = cursor.position()  # Store the end of the last selected line

    # Select the entire block of selected lines
    cursor.setPosition(start_block_pos)
    cursor.setPosition(end_block_pos+1, QTextCursor.KeepAnchor)
    selected_text = cursor.selection().toPlainText()  # Get the selected text
    cursor.removeSelectedText()

    # Move to the previous / next block (line above/below the selected text)
    cursor.setPosition(start_block_pos)
    if cursor.atStart():  # If we are at the very first line, we cannot move up
      return
    cursor.movePosition(QTextCursor.PreviousBlock if moveUp else QTextCursor.NextBlock)
    cursor.insertText(selected_text)  # Replace the previous line with selected text
    return
