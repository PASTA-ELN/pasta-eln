"""Tutorial quest loader and state manager."""
from __future__ import annotations

from dataclasses import dataclass
import logging
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from PySide6.QtCore import QObject, Signal, Slot
from ...backendWorker.worker import Task


@dataclass(frozen=True)
class QuestStep:
  """Definition of a quest step."""
  stepID: str
  title: str
  instruction: str
  trigger: dict[str, Any]
  image: str = ''


@dataclass(frozen=True)
class Quest:
  """Definition of a quest."""
  title: str
  description: str
  steps: list[QuestStep]


class TutorialManager(QObject):
  """Load quests from JSON files and track progress in memory."""
  activeQuestChanged = Signal()
  progressChanged = Signal()


  def __init__(self, questName:str) -> None:
    super().__init__()
    self.questDir = Path(__file__).resolve().parent.parent.parent / 'Resources' / 'Tutorials' / questName

    # Parse a quest definition
    data = json.load((self.questDir / 'main.json').open(encoding='utf-8'))
    if not isinstance(data, dict):
      logging.error('Tutorial file %s is invalid', self.questDir)
      return None
    title = str(data.get('title', self.questDir.name))
    description = str(data.get('description', ''))
    stepsRaw = data.get('steps', [])
    steps: list[QuestStep] = []
    for step in stepsRaw:
      steps.append( QuestStep(stepID=str(step.get('id', '')), title=str(step.get('title', '')),
                              instruction=str(step.get('instruction', '')), image=str(step.get('image', '')),
                              trigger=step.get('trigger', {})))
    self.quest = Quest(title=title, description=description, steps=steps)
    self.completedSteps = [False] * len(self.quest.steps)


  @Slot(Task, dict)
  def handle_task(self, task: Task, data: dict[str, Any]) -> None:
    """Handle task events emitted by the UI."""
    stepIndex = -1
    for idx, done in enumerate(self.completedSteps):
      if not done:
        stepIndex = idx
        break
    step = self.quest.steps[stepIndex]
    if self._match_trigger(step.trigger, task, data):
      self.completedSteps[stepIndex] = True
      self.progressChanged.emit()


  def _match_trigger(self, trigger: dict[str, Any], task: Task, data: dict[str, Any]) -> bool:
    """Return True when a task matches the trigger definition."""
    eventName = trigger.get('event')
    if Task[eventName.replace('Task.', '').strip()] is not task:
      return False
    if 'docType' in trigger and data.get('docType') != trigger.get('docType'):
      return False
    if 'name' in trigger:
      doc = data.get('doc', {})
      if not isinstance(doc, dict) or doc.get('name') != trigger.get('name'):
        return False
    if 'file' in trigger:
      if not self._match_file_trigger(str(trigger.get('file')), data):
        return False
    return True


  def _match_file_trigger(self, target_file: str, data: dict[str, Any]) -> bool:
    """Check whether a task references a target filename."""
    file_name = data.get('fileName')
    if isinstance(file_name, str) and Path(file_name).name == target_file:
      return True
    items = data.get('items', [])
    if isinstance(items, (list, tuple)):
      for item in items:
        candidate = self._normalize_item_path(item)
        if candidate and Path(candidate).name == target_file:
          return True
    return False

  @staticmethod
  def _normalize_item_path(item: Any) -> str | None:
    """Normalize dropped items into a filesystem path."""
    if hasattr(item, 'toLocalFile'):
      return item.toLocalFile()
    if not item:
      return None
    item_str = str(item)
    if item_str.startswith('file://'):
      return urlparse(item_str).path
    return item_str
