"""Tutorial panel for quest guidance."""
from __future__ import annotations
from datetime import datetime
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QWidget
from .manager import TutorialManager
from ..guiStyle import widgetAndLayout, TextButton, Label, Image

START_WIDTH = 320

class TutorialPanel(QWidget):
  """Display tutorial quests and progress."""
  def __init__(self, comm, manager: TutorialManager) -> None:
    super().__init__()
    self.manager = manager
    self.comm = comm
    self.setMinimumWidth(START_WIDTH)
    self.layout = QVBoxLayout(self)
    # General quest details
    self.introW, self.introL = widgetAndLayout('V', self.layout, 's',  's','s', 's','s')
    test = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKAAAACgCAIAAAAErfB6AAAB/klEQVR4nOzTsUncARyG4ZD8i6tC0qTIAmmSFQLp0igOYCUiTiC2N4SChWChjVxvfaUjXOEI9hYKbuEPXp5nga94+Zb/X39/mnD493Jk9+zoeGR3b3U1svt5ZJUPI3CcwHECxwkcJ3CcwHECxwkcJ3CcwHECxwkcJ3CcwHECxwkcJ3CcwHECxwkcJ3CcwHECxwkcJ3CcwHECxwkcJ3CcwHECxwkcJ3CcwHECxwkcJ3CcwHHLj823keE/Px9Gdm9225HdzbIb2fXgOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI5bDp5eRoYfn7+P7K7v90d2T09eR3Y9OE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjli/n/0aGt9d3I7u3b79Gdlfri5FdD44TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7gOIHjBI4TOE7guPcAAAD//0PwF4w6gQUpAAAAAElFTkSuQmCC'
    self.image = Image(test, self.introL, width=START_WIDTH)
    self.label = Label(f'Quest: {self.manager.quest.title}','h1', self.introL)
    self.description = Label(self.manager.quest.description, 'h2', self.introL)
    self.description.setWordWrap(True)
    self.startBtn = TextButton('Start quest', self, ['start'], self.introL)
    # Progress
    self.stepsW, self.stepsL = widgetAndLayout('V', self.layout, '0',  's','s', 's','s')
    self.stepsW.hide()
    self.manager.progressChanged.connect(self.refreshSteps)
    self.helpBtn: TextButton | None = None
    # Rating
    self.layout.addStretch(1)
    self.rating = Label('Level: 1', 'h2', self.layout)
    self.rating.hide()


  def execute(self, command: list[str]):
    if command[0] == 'start':
      self.manager.started = datetime.now()
      self.introW.hide()
      self.stepsW.show()
      self.refreshSteps()
      self.rating.show()
    if command[0] == 'help':
      stepIndex =  self.manager.completedSteps.index(False)
      QMessageBox.information(self, 'Help', self.manager.quest.steps[stepIndex].help)


  @Slot()
  def refreshSteps(self) -> None:
    """Refresh step list with progress."""
    stepIndex =  self.manager.completedSteps.index(False)
    for i in reversed(range(self.stepsL.count())):
      self.stepsL.itemAt(i).widget().setParent(None)
    for idx, step in enumerate(self.manager.quest.steps):
      status = '✓' if self.manager.completedSteps[idx] else '•'
      Label(f'{status} {step.title}', 'h2', self.stepsL, style='margin-top: 5px; ')
      if idx == stepIndex:
        if step.image:
          Image(step.image, self.stepsL)
        instructions = Label(step.instruction, 'h3', self.stepsL)
        instructions.setWordWrap(True)
        self.helpBtn = TextButton('Help', self, ['help'], self.stepsL)

    if self.manager.started is not None:
      level = (stepIndex+1) / ((datetime.now() - self.manager.started).total_seconds()/60.+1)
      print(level, stepIndex, (datetime.now() - self.manager.started).total_seconds()/60.)
      self.rating.setText(f'Level {round(level)}')

