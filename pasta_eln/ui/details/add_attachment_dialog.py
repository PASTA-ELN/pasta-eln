"""Dialog for adding an existing compatible item to an instrument attachment location"""
from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout, QWidget


class AddAttachmentDialog(QDialog):
  """Choose a compatible existing item and add it to an attachment location"""

  def __init__(self, attachments: list[dict[str, Any]], parent: QWidget):
    """Create the attachment selection dialog

    Args:
      attachments (list[dict[str, Any]]): Attachment locations and their compatible existing items
      parent (QWidget): Parent widget for the modal dialog
    """
    super().__init__(parent)
    self.attachments = attachments
    self.setWindowTitle('Add attachment')
    layout = QVBoxLayout(self)
    form = QFormLayout()
    layout.addLayout(form)
    self.location = QComboBox()
    self.location.setAccessibleName('attachment location')
    self.item = QComboBox()
    self.item.setAccessibleName('attachment item')
    self.remark = QLineEdit()
    self.remark.setAccessibleName('attachment remark')
    form.addRow('Location', self.location)
    form.addRow('Attachment', self.item)
    form.addRow('Remark', self.remark)
    for attachment in attachments:
      self.location.addItem(str(attachment['location']))
    self.location.currentIndexChanged.connect(self.updateItems)
    self.updateItems(0)
    self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
    self.buttons.accepted.connect(self.accept)
    self.buttons.rejected.connect(self.reject)
    layout.addWidget(self.buttons)


  def updateItems(self, index: int) -> None:
    """Update compatible candidates after the location changes

    Args:
      index (int): Index of the selected attachment location
    """
    self.item.clear()
    if index < 0:
      return
    for candidate in self.attachments[index]['candidates']:
      self.item.addItem(f"{candidate['name']} ({candidate['type']})", candidate['id'])
    self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self.item.count() > 0)


  def selectedAttachment(self) -> tuple[str, str, str]:
    """Return the location, item ID, and optional remark selected by the user

    Returns:
      A tuple containing location, existing item ID, and trimmed remark
    """
    return self.location.currentText(), str(self.item.currentData()), self.remark.text().strip()
