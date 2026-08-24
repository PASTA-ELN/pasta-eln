"""Selection context for the Details pane."""
from dataclasses import dataclass
from enum import Enum


class DetailOrigin(Enum):
  """View that selected the item shown in Details."""
  PROJECT = 'project'
  TABLE = 'table'
  LINK = 'link'


@dataclass(frozen=True)
class DetailContext:
  """Document and optional project-tree location shown in Details."""
  docID: str = ''
  treeStack: str = ''
  origin: DetailOrigin | None = None
