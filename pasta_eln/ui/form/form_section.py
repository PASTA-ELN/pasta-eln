"""Collapsible sections used by the document editor."""
from PySide6.QtWidgets import QFormLayout, QPushButton, QVBoxLayout, QWidget
from pasta_eln.ui.gui_style import SPACE


class FormSection(QWidget):
  """A collapsible form section used for a data-hierarchy group."""

  def __init__(self, title: str, *, expanded: bool = True) -> None:
    super().__init__()
    self.title = title
    self.toggle = QPushButton(f'⌄  {title}')
    self.toggle.setFlat(True)
    self.toggle.setCheckable(True)
    self.toggle.setChecked(expanded)
    self.toggle.setStyleSheet('text-align: left; font-weight: bold; padding: 6px 0;')
    self.toggle.clicked.connect(lambda checked: self.setExpanded(checked))
    self.formW = QWidget()
    self.formL = QFormLayout(self.formW)
    self.formL.setContentsMargins(SPACE.M, SPACE.S, SPACE.M, SPACE.M)
    self.formL.setSpacing(SPACE.S)
    self.formL.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
    self.formW.setVisible(expanded)
    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(self.toggle)
    layout.addWidget(self.formW)

  def setExpanded(self, expanded: bool) -> None:
    """Show or hide the form rows and update the disclosure icon."""
    self.toggle.setChecked(expanded)
    self.formW.setVisible(expanded)
    self.toggle.setText(f"{'⌄' if expanded else '›'}  {self.title}")
