"""Tutorial panel for quest guidance."""
from __future__ import annotations
import base64
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import QAbstractScrollArea, QMessageBox, QTextBrowser, QVBoxLayout, QWidget
from ..guiCommunicate import Communicate
from ..guiStyle import Image, Label, TextButton, widgetAndLayout
from .manager import TutorialManager

START_WIDTH = 480

class TutorialPanel(QWidget):
  """Display tutorial quests and progress."""
  def __init__(self, comm:Communicate, manager: TutorialManager) -> None:
    super().__init__()
    self.manager = manager
    self.comm = comm
    self.setFixedWidth(START_WIDTH)
    self.mainL = QVBoxLayout(self)
    # General quest details
    self.introW, self.introL = widgetAndLayout('V', self.mainL, 's',  's','s', 's','s')
    imgData = ''
    if self.manager.quest.image:
      with open(self.manager.questDir / self.manager.quest.image, 'rb') as image_file:
        imgData = base64.b64encode(image_file.read()).decode('ascii')
      imgData = f"data:image/jpg;base64,{imgData}"
    self.image = Image(imgData, self.introL, width=START_WIDTH)
    self.textBrowser = QTextBrowser(self)
    text = f'## {self.manager.quest.title}\n\n{self.manager.quest.description}'
    self.textBrowser.setMarkdown(text)
    self.textBrowser.setOpenExternalLinks(True)
    self.textBrowser.setMinimumHeight(int(START_WIDTH*0.8))
    self.introL.addWidget(self.textBrowser)
    self.startBtn = TextButton('Start quest', self, ['start'], self.introL)
    # Progress
    self.stepsW, self.stepsL = widgetAndLayout('V', self.mainL, '0',  's','s', 's','s')
    self.stepsW.hide()
    self.manager.progressChanged.connect(self.refreshSteps)
    self.helpBtn: TextButton | None = None
    # Rating
    self.mainL.addStretch(1)
    self.rating = Label('Level: 1', 'h2', self.mainL)
    self.rating.hide()


  def execute(self, command: list[str]) -> None:
    """ execute commands
    Args:
      command (list): list of commands
   """
    if command[0] == 'start':
      self.manager.start()
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
    try:
      stepIndex =  self.manager.completedSteps.index(False)
    except ValueError:
      self.introW.show()
      self.stepsW.hide()
      self.startBtn.hide()
      stepIndex = len(self.manager.quest.steps)
      text = f'## {self.manager.quest.title}\n\n🎉 Quest complete! 🎉\n⏱️ You took {self.manager.durationSec} sec.'
      self.textBrowser.setMarkdown(text)
      return
    for i in reversed(range(self.stepsL.count())):
      self.stepsL.itemAt(i).widget().setParent(None)
    for idx, step in enumerate(self.manager.quest.steps):
      status = '✓' if self.manager.completedSteps[idx] else '•'
      Label(f'{status} {step.title}', 'h2', self.stepsL, style='margin-top: 5px; ')
      if idx == stepIndex:
        if step.image:
          Image(step.image, self.stepsL)
        self.instructions = QTextBrowser(self)
        self.instructions.setMarkdown(step.instruction)
        self.instructions.setOpenExternalLinks(True)
        self.instructions.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._updateInstructionHeight()
        QTimer.singleShot(0, self._updateInstructionHeight)
        self.stepsL.addWidget(self.instructions)
        self.helpBtn = TextButton('Help', self, ['help'], self.stepsL, style='margin-bottom: 20px; ')
    self.rating.setText(f'Level {self.manager.level}')


  def _updateInstructionHeight(self) -> None:
    """ Update instructions height to text content """
    document = self.instructions.document()
    document.setTextWidth(START_WIDTH-20)
    document.adjustSize()
    height = int(document.size().height() - 20)
    self.instructions.setFixedHeight(height)
    self.instructions.setMaximumHeight(height)
