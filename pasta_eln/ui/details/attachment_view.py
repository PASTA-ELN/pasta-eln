"""Read-only instrument attachment history displayed in the Details view."""
from __future__ import annotations
from html import escape
from typing import Any
from PySide6.QtWidgets import QVBoxLayout, QWidget
from pasta_eln.ui.details.details_hier_item import DetailsHierItem
from pasta_eln.ui.gui_style import Button, CommandHost


class AttachmentView(QWidget):
  """Show instrument attachment locations, current state, and immutable histories."""

  def __init__(self, attachments: list[dict[str, Any]], host: CommandHost, addCommand: Any):
    """Create the attachment history view.

    Args:
      attachments: Attachment locations with history and compatible candidates.
      host: Command host that handles the add-attachment action.
      addCommand: Command dispatched when the add button is clicked.
    """
    super().__init__()
    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)
    for attachment in attachments:
      history = attachment['history']
      current = history[0] if history else None
      currentText = self.currentText(current)
      historyText = ''.join(self.historyText(entry) for entry in history) or 'No attachment history yet.'
      section = DetailsHierItem(host.comm, f"{attachment['location']}: {currentText}", [], historyText, startCollapsed=True)
      section.setObjectName(f"attachment:{attachment['location']}")
      layout.addWidget(section)
    Button('Add attachment', host, addCommand, layout, icon='ri.add-line')
    layout.addStretch(0)


  @staticmethod
  def currentText(entry: dict[str, Any] | None) -> str:
    """Return a concise description for a collapsed attachment location.

    Args:
      entry: Latest history entry, or None when no history exists.

    Returns:
      The current attachment name, remark, or an empty-state label.
    """
    if entry is None:
      return 'No attachment'
    if entry['name']:
      return str(entry['name'])
    return str(entry['remark']) or 'Service record'


  @staticmethod
  def historyText(entry: dict[str, Any]) -> str:
    """Format one immutable attachment history record as safe rich text.

    Args:
      entry: History record containing date, item, remark, and user fields.

    Returns:
      Rich text for the history entry.
    """
    item = (f'<a href="pasta-eln://{escape(str(entry["id"]))}">{escape(str(entry["name"]))}</a>'
            if entry['id'] and entry['name'] else '')
    remark = escape(str(entry['remark']))
    details = ' — '.join(part for part in (item, remark) if part) or 'Service record'
    return f'<b>{escape(str(entry["date"]))}</b><br>{details}<br><i>{escape(str(entry["user"]))}</i><br><br>'
