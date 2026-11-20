"""Lab companion: ask an LLM about the item last shown in Details

Only created when the configuration has an 'llm' section and the provider package is installed;
the API key is read by the provider package from ANTHROPIC_API_KEY / OPENAI_API_KEY
"""
import json
from collections.abc import Callable
from enum import Enum
from typing import Any
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QPlainTextEdit, QTextEdit, QVBoxLayout
from ..ui.details.context import DetailContext
from ..ui.gui_communicate import Communicate
from ..ui.gui_style import Button, ButtonStyle, Widget, shortcut
from ..ui.wait_dialog import Worker

SYSTEM_PROMPT = ('You answer questions about one item of the scientific electronic lab notebook PASTA-ELN. '
                 'The item is given as JSON. Be concise. Say when the item does not contain the answer.')


class Command(Enum):
  """Commands of the lab companion"""
  ASK = 1


class LabCompanion(Widget):
  """Ask an LLM a question about the item last shown in Details"""

  def __init__(self, comm: Communicate, configuration: dict[str, str]):
    """Initialize the lab companion

    Args:
      comm (Communicate): Shared communication object
      configuration (dict): 'llm' section of the configuration: provider, model, optional baseURL
    """
    super().__init__()
    self.comm = comm
    self.configuration = configuration
    self.docID = ''
    self.doc: dict[str, Any] = {}
    self.worker: Worker | None = None

    # Widgets
    self.answer = QTextEdit(readOnly=True)
    self.question = QPlainTextEdit(placeholderText='Question about the item shown in Details')
    self.question.setMaximumHeight(self.question.fontMetrics().lineSpacing() * 4)

    # Layout
    mainL = QVBoxLayout(self)
    mainL.addWidget(self.answer)
    questionL = QHBoxLayout()
    questionL.addWidget(self.question)
    self.askButton = Button('Ask', self, Command.ASK, questionL, icon='fa5s.paper-plane',
                            tooltip='Ctrl+Return', style=ButtonStyle.HIGHLIGHTED)
    mainL.addLayout(questionL)

    # Signals
    self.askShortcut = shortcut('Ctrl+Return', self, lambda: self.execute(Command.ASK))
    self.askShortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)    # only while focus is in this panel
    self.comm.changeDetails.connect(self.onDetailsChanged)
    self.comm.backendThread.worker.beSendDoc.connect(self.onGetData)


  @Slot(object)
  def onDetailsChanged(self, context: DetailContext) -> None:
    """Remember which item Details shows

    Args:
      context (DetailContext): Document shown in Details; empty if Details is hidden
    """
    self.docID = context.docID
    if not self.docID:
      self.doc = {}


  @Slot(dict)
  def onGetData(self, data: dict[str, Any]) -> None:
    """Keep the document if it is the one shown in Details; beSendDoc also carries documents for other widgets

    Args:
      data (dict): document sent by the backend
    """
    if data.get('id') == self.docID:
      self.doc = data


  @Slot(str, str)
  def onAnswer(self, kind: str, text: str) -> None:
    """Show the answer or error from the worker thread

    Args:
      kind (str): 'answer' (Markdown) or 'error' (plain text)
      text (str): content to show
    """
    if kind == 'answer':
      self.answer.setMarkdown(text)
    else:
      self.answer.setPlainText(text)
    self.askButton.setEnabled(True)


  def execute(self, command: Command) -> None:
    """Handle a command from a child control

    Args:
      command (Command): command to execute
    """
    if command is Command.ASK:
      question = self.question.toPlainText().strip()
      if not question:
        return
      if not self.doc:
        self.answer.setPlainText('Select an item first.')
        return
      # =========================================================================================
      # IMAGES ARE REMOVED BEFORE SENDING: the 'image' field (base64 / SVG preview) is large and
      # adds little. Everything else, including the full metaVendor, is sent to the provider.
      # =========================================================================================
      doc = {key: value for key, value in self.doc.items() if key != 'image'}
      userText = f'Item:\n{json.dumps(doc, default=str)}\n\nQuestion:\n{question}'
      provider, model = self.configuration['provider'], self.configuration['model']
      baseURL = self.configuration.get('baseURL') or None

      def requestAnswer(progress: Callable[[str, str], None]) -> None:
        """Send item and question to the provider; runs in the worker thread

        Args:
          progress (Callable): emits (kind, text) to the UI thread
        """
        try:
          if provider == 'anthropic':
            import anthropic
            response = anthropic.Anthropic().messages.create(
              model=model, max_tokens=16000, system=SYSTEM_PROMPT,
              messages=[{'role': 'user', 'content': userText}])
            text = ''.join(block.text for block in response.content if block.type == 'text')
            progress('answer', text or f'No answer (stop reason: {response.stop_reason})')
          else:
            import openai
            completion = openai.OpenAI(base_url=baseURL).chat.completions.create(
              model=model, messages=[{'role': 'system', 'content': SYSTEM_PROMPT},
                                     {'role': 'user', 'content': userText}])
            progress('answer', completion.choices[0].message.content or 'No answer')
        except Exception as error:                     # network, authentication, model, and context errors
          progress('error', f'{type(error).__name__}: {error}')

      self.askButton.setEnabled(False)
      self.answer.setPlainText('Waiting for answer…')
      self.worker = Worker(requestAnswer)
      self.worker.progress.connect(self.onAnswer)
      self.worker.start()
