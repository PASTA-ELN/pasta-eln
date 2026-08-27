""" Widgets inside the details-sidebar that consist of a button and a collapsible area that shows info.
"""
import logging
import re
from typing import Any
from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QSizePolicy
from pasta_eln.misc_tools import isDocID, makeStringWrappable
from pasta_eln.text_tools.markdown2html import markdown2html  # type: ignore[attr-defined]
from pasta_eln.text_tools.string_changes import markdownEqualizer, tuple2html
from pasta_eln.ui.details.context import DetailContext, DetailOrigin
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import CollapsibleSection


class DetailsHierItem(CollapsibleSection):
  """
  Widget inside the details-sidebar that consists of a button and a collapsible area that shows info.
  """

  def __init__(self, comm: Communicate, categoryName: str, dataHierarchyNode: list[dict[str, Any]],
               initialContent: str = '', startCollapsed: bool = False) -> None:
    """Initialize a collapsible section for one entry

    Args:
      comm (Communicate): Shared communication object.
      categoryName (str): Display label of the entry.
      dataHierarchyNode (list[dict[str, Any]]): Hierarchy data used to populate the section.
      initialContent (str): Text shown before additional content is loaded.
      startCollapsed (bool): Whether the section starts in its collapsed state.
    """
    self.comm = comm
    self.categoryName = categoryName
    self.content = initialContent
    self.dataHierarchyNode = dataHierarchyNode

    # contentLabel
    self.contentLabel = QLabel(self.content)
    self.contentLabel.setWordWrap(True)
    self.contentLabel.setTextFormat(Qt.TextFormat.RichText)
    self.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse |
                                              Qt.TextInteractionFlag.LinksAccessibleByMouse)
    self.contentLabel.linkActivated.connect(self.openLink)

    super().__init__(self.categoryName, self.contentLabel, expanded=not startCollapsed,
                     iconSize=QSize(32, 32), outlined=True)
    self.button = self.toggle

    #
    self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)


  def collapse(self) -> None:
    """Hide this section's content."""
    self.setExpanded(False)


  def expand(self) -> None:
    """Show this section's content."""
    self.setExpanded(True)


  def formatContent(self, key: str, value: Any) -> str:
    """ Format content

    Args:
      key: key of the datapoint to add. E.g. 'user'
      value: value of the corresponding datapoint. E.g. 'rroeske'

    Returns:
      The formatted String that can be displayed in the Label of this Widget or appended using self.addContent
    """
    if isinstance(value, dict):                          # Original, : if not key and isinstance(value, dict):
      return '\n'.join([self.formatContent(k, v) for k, v in value.items()])
    if not value:
      return ''
    labelStr = ''
    isMarkdown = key == 'comment' or (isinstance(value, str) and '\n' in value)# will become html: do not makeWrappable
    if key == 'tags':
      rating = ['\u2605' * int(i[1]) for i in value if re.match(r'^_\d$', i)]
      tags = [i for i in value if not re.match(r'^_\d$', i)]
      labelStr = f'<b>Rating:</b><br>{rating[0]}<br><br>' if rating else ''
      labelStr = f'{labelStr}   <b>Tags:</b><br>' + ', '.join(tags) + '<br><br>'
    elif isMarkdown:                                                                 # long values or comments
      labelStr = f'<b>{key.capitalize()}:</b><br>{markdown2html(markdownEqualizer(value))}<br><br>'
    else:
      dataHierarchyItems = [dict(i) for i in self.dataHierarchyNode if i['name'] == key]
      if len(dataHierarchyItems) == 1 and 'list' in dataHierarchyItems[0] and dataHierarchyItems[0]['list'] and \
        ',' not in dataHierarchyItems[0]['list'] and ' ' not in dataHierarchyItems[0]['list']:# A single-choice docType is represented as a tuple.
        if not isinstance(value, tuple):
          logging.info('Not a tuple: %s : %s', key, value)
        if not isDocID(value[0]):
          value = value[0]
      elif isinstance(value, list):
        value = ', '.join([str(i) for i in value])
      labelStr = f'<b>{key}:</b><br>{value}<br><br>'
      if isinstance(value, tuple) and len(value) == 4:
        k, v = tuple2html(key, value)
        if isDocID(value[0]):
          k = key
          valueText = f'<a href="pasta-eln://{value[0]}">{value[2] or value[1]}</a>'
          v = valueText if value[3] is None or value[3] == '' else \
              f'{valueText}&nbsp;<b><a href="{value[3]}">&uArr;</a></b>'
        labelStr = f'<b>{k}:</b><br>{v}<br><br>'
    # Wrapping can force an HTML-statement wrap in rare cases
    return labelStr if isMarkdown or '<a href=' in labelStr else makeStringWrappable(labelStr)


  def addContent(self, key: str, value: Any) -> None:
    """Append a formatted metadata value to the section.

    Args:
      key: Metadata field name.
      value: Metadata field value.
    """
    self.content += self.formatContent(key, value)
    self.contentLabel.setText(self.content.removesuffix('<br><br>'))


  def openLink(self, link: str) -> None:
    """Open an internal item link in Details or delegate an external URL to Qt.

    Args:
      link: URL activated in the rich-text label.
    """
    if link.startswith('pasta-eln://') and isDocID(link.removeprefix('pasta-eln://')):
      self.comm.changeDetails.emit(DetailContext(link.removeprefix('pasta-eln://'), origin=DetailOrigin.LINK))
    else:
      QDesktopServices.openUrl(QUrl(link))
