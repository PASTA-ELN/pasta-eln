"""Helpers for creating menu actions."""
import logging
import traceback
from html import escape
from typing import Any
import qtawesome as qta
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu, QWidget
from .message_dialog import showMessage


def action(label: str, widget: QWidget, command: Any, menu: QMenu, keySequence: str | None = None,
           icon: str = '') -> QAction:
  """Create a menu action that forwards a command to its owning widget."""
  actionObject = QAction(widget)
  actionObject.setText(label)
  def triggered() -> None:
    """Dispatch the configured command through the host widget."""
    try:
      widget.execute(command)                                                     # type: ignore[attr-defined]
    except Exception:
      logging.exception('Unable to execute menu action %r', label)
      errorMsg = f'<p>Could not execute “{escape(label)}”.</p><pre>{escape(traceback.format_exc())}</pre>'
      showMessage(widget, 'Action failed', errorMsg, 'Critical')
  actionObject.triggered.connect(triggered)
  if icon:
    color = 'black' if widget is None else widget.comm.palette.text               # type: ignore[attr-defined]
    actionObject.setIcon(qta.icon(icon, color=color, scale_factor=1))
  if keySequence is not None:
    actionObject.setShortcut(QKeySequence(keySequence))
  menu.addAction(actionObject)
  return actionObject
