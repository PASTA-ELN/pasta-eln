"""Signal adapter for collapsible form sections."""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from .form_section import FormSection


class SectionHost:
  """Signal adapter that keeps :class:`FormSection` self-contained."""

  def __init__(self, section: 'FormSection') -> None:
    self.section = section
    self.comm: Any = None

  def execute(self, _: Any) -> None:
    """Meet the command-host interface used by shared buttons."""

  def toggle(self, _: bool = False) -> None:
    """Toggle the section owned by this adapter."""
    self.section.setExpanded(self.section.toggle.isChecked())
