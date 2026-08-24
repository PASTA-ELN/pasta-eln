"""Collapsible sections used by the document editor."""
from PySide6.QtWidgets import QFormLayout, QWidget
from pasta_eln.ui.gui_style import SPACE, CollapsibleSection


class FormSection(CollapsibleSection):
  """A collapsible form section used for a data-hierarchy group."""

  def __init__(self, title: str, *, expanded: bool = True) -> None:
    """Initialize a form section with a title and expansion state.

    Args:
      title (str): Heading displayed above the section's form fields.
      expanded (bool): Whether the section's contents are initially visible.
    """
    self.formW = QWidget()
    self.formL = QFormLayout(self.formW)
    self.formL.setContentsMargins(SPACE.M, SPACE.S, SPACE.M, SPACE.M)
    self.formL.setSpacing(SPACE.S)
    self.formL.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
    super().__init__(title, self.formW, expanded=expanded, boldTitle=True)
