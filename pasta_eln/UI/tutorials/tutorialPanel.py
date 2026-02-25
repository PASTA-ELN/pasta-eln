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
    self.quest_selector = QComboBox()
    self.title_label = QLabel()
    self.description_label = QLabel()
    self.description_label.setWordWrap(True)
    self.steps_list = QListWidget()
    self.start_button = QPushButton('Start quest')

    layout = QVBoxLayout()
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(6)
    layout.addWidget(QLabel('Tutorials'))
    layout.addWidget(self.quest_selector)
    layout.addWidget(self.title_label)
    layout.addWidget(self.description_label)
    layout.addWidget(self.start_button)
    layout.addWidget(self.steps_list)
    self.setLayout(layout)
    self.setMinimumWidth(280)
    self.manager.progressChanged.connect(self.refresh_steps)

  @Slot()
  def refresh(self) -> None:
    """Refresh quest details."""
    quest = self.manager.active_quest
    if quest is None:
      selected = self._get_quest_from_id(self.quest_selector.currentData())
      if selected is None:
        self.title_label.setText('No tutorials available')
        self.description_label.setText('Add quest YAML files to the tutorials folder.')
        self.steps_list.clear()
      else:
        self.title_label.setText(f'Quest: {selected.title}')
        self.description_label.setText(selected.description)
        self.steps_list.clear()
        item = QListWidgetItem('Press "Start quest" to begin.')
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.steps_list.addItem(item)
      self.start_button.setText('Start quest')
      return
    self.title_label.setText(f'Quest: {quest.title}')
    self.description_label.setText(quest.description)
    self.start_button.setText('Restart quest')
    self.refresh_steps()

  @Slot()
  def refresh_steps(self) -> None:
    """Refresh step list with progress."""
    quest = self.manager.active_quest
    if quest is None:
      return
    self.steps_list.clear()
    for idx, step in enumerate(quest.steps):
      completed = self.manager.completed_steps[idx] if idx < len(self.manager.completed_steps) else False
      status = '✓' if completed else '•'
      item = QListWidgetItem(f'{status} {step.title}: {step.instruction}')
      item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
      self.steps_list.addItem(item)

  def _get_quest_from_id(self, quest_id: object) -> Quest | None:
    """Return a quest by id from the manager."""
    if isinstance(quest_id, str):
      return self.manager.get_quest(quest_id)
    return None
