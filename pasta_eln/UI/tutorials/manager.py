"""Tutorial quest loader and state manager.
- remember to use "yq .  main.yml > main.json" in each folder (automatically done in release script)
"""
from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from PySide6.QtCore import QObject, Signal, Slot
from ...backendWorker.worker import Task


@dataclass(frozen=True)
class QuestStep:
  """Definition of a quest step."""
  stepID: str
  title: str
  instruction: str
  trigger: dict[str, Any]
  help:str = 'No help information provided.'
  image: str = ''


@dataclass(frozen=True)
class Quest:
  """Definition of a quest."""
  title: str
  description: str
  steps: list[QuestStep]
  image: str = ''


class TutorialManager(QObject):
  """Load quests from JSON files and track progress in memory."""
  progressChanged = Signal()
  def __init__(self, questName:str) -> None:
    super().__init__()
    self.questDir = Path(__file__).resolve().parent.parent.parent / 'Resources' / 'Tutorials' / questName
    self.started: datetime | None = None
    # Parse a quest definition
    data = json.load((self.questDir / 'main.json').open(encoding='utf-8'))
    if not isinstance(data, dict):
      logging.error('Tutorial file %s is invalid', self.questDir)
    else:
      title = str(data.get('title', self.questDir.name))
      description = str(data.get('description', ''))
      stepsRaw = data.get('steps', [])
      steps: list[QuestStep] = []
      for step in stepsRaw:
        stepNew = QuestStep(stepID=str(step.get('id', '')), title=str(step.get('title', '')),
                                instruction=str(step.get('instruction', '')), image=step.get('image', ''),
                                trigger=step.get('trigger', {}), help=step.get('help', ''))
        steps.append(stepNew)
      self.quest = Quest(title=title, description=description, steps=steps, image=data.get('image', ''))
      self.completedSteps = [False] * len(self.quest.steps)
      self.level = 1
      self.durationSec = 0


  def start(self) -> None:
    """Start the quest."""
    self.started = datetime.now()
    self.completedSteps = [False] * len(self.quest.steps)
    return


  @Slot(Task, dict)
  def handleTask(self, task: Task, data: dict[str, Any]) -> None:
    """Handle task events emitted by the UI."""
    stepIndex = self.completedSteps.index(False)
    step = self.quest.steps[stepIndex]
    if self._match_trigger(step.trigger, task, data):
      self.completedSteps[stepIndex] = True
      if self.started is None:
        self.durationSec = 0
      else:
        self.durationSec = round((datetime.now()-self.started).total_seconds())
      self.level = 1 if stepIndex==0 else round((stepIndex+1)**2/(self.durationSec/60.+1))
      self.progressChanged.emit()


  def _match_trigger(self, trigger: dict[str, str], task: Task, data: dict[str, Any]) -> bool:
    """Return True when a task matches the trigger definition."""
    for triggerK, triggerV in trigger.items():
      if triggerK == 'event':
        if Task[triggerV] is not task:
          return False
      elif triggerK=='docType' and 'docType' in data:
        if data.get('docType') != triggerV:
          return False
      elif triggerK=='_count_':
        if len(data['items'])!=int(triggerV):
          return False
      else:
        doc = data.get('doc', {})
        if triggerV=='_non_empty_':
          if not doc.get(triggerK):
            return False
        elif triggerV.lower() not in str(doc.get(triggerK, '')).lower():
          return False
    return True
