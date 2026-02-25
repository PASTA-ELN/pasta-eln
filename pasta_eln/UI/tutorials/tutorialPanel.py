"""Tutorial panel for quest guidance."""
from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget
from .manager import Quest, TutorialManager

class TutorialPanel(QWidget):
  """Display tutorial quests and progress."""
  def __init__(self, manager: TutorialManager) -> None:
    super().__init__()
    self.manager = manager
    self.titleLabel = QLabel()
    self.descriptionLabel = QLabel()
    self.descriptionLabel.setWordWrap(True)
    self.stepsList = QListWidget()

    layout = QVBoxLayout()
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(6)
    layout.addWidget(QLabel('Tutorials'))
    layout.addWidget(self.titleLabel)
    layout.addWidget(self.descriptionLabel)
    layout.addWidget(self.stepsList)
    self.setLayout(layout)
    self.setMinimumWidth(280)
    self.manager.progressChanged.connect(self.refreshSteps)
    self.refresh()


  @Slot()
  def refresh(self) -> None:
    """Refresh quest details."""
    self.titleLabel.setText(f'Quest: {self.manager.quest.title}')
    self.descriptionLabel.setText(self.manager.quest.description)
    self.refreshSteps()


  @Slot()
  def refreshSteps(self) -> None:
    """Refresh step list with progress."""
    self.stepsList.clear()
    for idx, step in enumerate(self.manager.quest.steps):
      completed = self.manager.completedSteps[idx] if idx < len(self.manager.completedSteps) else False
      status = '✓' if completed else '•'
      item = QListWidgetItem(f'{status} {step.title}: {step.instruction}')
      item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
      self.stepsList.addItem(item)
