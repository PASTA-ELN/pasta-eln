""" Widgets inside the details-sidebar that consist of a button and a collapsible area that shows info.
"""
import logging
import re
from typing import Any

import qtawesome
from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from pasta_eln.misc_tools import isDocID, makeStringWrappable
from pasta_eln.text_tools.string_changes import tuple2html
from pasta_eln.ui.gui_communicate import Communicate


class DetailsHierItem(QWidget):
  """
  Widget inside the details-sidebar that consists of a button and a collapsible area that shows info.
  """

  def __init__(self, comm: Communicate, categoryName: str, dataHierarchyNode: list[dict[str, Any]],
               initialContent: str = "", startCollapsed: bool = False) -> None:
    super().__init__()
    self.comm = comm
    self.categoryName = categoryName
    self.content = initialContent
    self.dataHierarchyNode = dataHierarchyNode

    # Button to Expand and Collapse Content
    self.button = QPushButton(self.categoryName)
    self.button.setCheckable(True)
    self.button.setFlat(True)
    self.button.setIconSize(QSize(30, 30))
    self.button.setStyleSheet("text-align: left; border-radius:0px;")
    self.button.clicked.connect(self.onButtonClicked)

    # contentLabel
    self.contentLabel = QLabel(self.content)
    self.contentLabel.setWordWrap(True)
    self.contentLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    # Main Layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.setContentsMargins(0, 0, 0, 0)
    self.mainLayout.addWidget(self.button)
    self.mainLayout.addWidget(self.contentLabel)
    self.setLayout(self.mainLayout)

    #
    self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

    # CODE
    if startCollapsed:
      self.collapse()
    else:
      self.button.setChecked(True)
      self.expand()

  @Slot()
  def onButtonClicked(self) -> None:
    """
    What happens when the button is clicked
    -> Collapse/Expand Content
    """
    if self.button.isChecked():
      self.expand()
    else:
      self.collapse()

  def collapse(self) -> None:
    """Hide the content of this widget"""
    self.contentLabel.hide()
    self.button.setIcon(qtawesome.icon("ri.arrow-drop-right-line"))

  def expand(self) -> None:
    """Show the content of this widget"""
    self.contentLabel.show()
    self.button.setIcon(qtawesome.icon("ri.arrow-drop-down-line"))

  def formatContent(self, key: str, value: Any) -> str:
    """

    Args:
      key: key of the datapoint to add. E.g. 'user'
      value: value of the corresponding datapoint. E.g. 'rroeske'

    Returns:
      The formatted String that can be displayed in the Label of this Widget or appended using self.addContent
    """
    if isinstance(value, dict):  # Original, : if not key and isinstance(value, dict):
      return '\n'.join([self.formatContent(k, v) for k, v in value.items()])
    if not value:
      return ''
    labelStr = ''
    if key == 'tags':
      rating = ['\u2605' * int(i[1]) for i in value if re.match(r'^_\d$', i)]
      tags = [i for i in value if not re.match(r'^_\d$', i)]
      labelStr = f'<b>Rating:</b><br>{rating[0]}<br><br>' if rating else ''
      labelStr = f'{labelStr}   <b>Tags:</b><br>' + ', '.join(tags) + "<br><br>"
    elif (isinstance(value, str) and '\n' in value) or key == 'comment':  # long values with /s or comments
      labelStr = f'<b>{key.capitalize()}:</b><br>{value}<br><br>'
    else:
      dataHierarchyItems = [dict(i) for i in self.dataHierarchyNode if i['name'] == key]
      if len(dataHierarchyItems) == 1 and 'list' in dataHierarchyItems[0] and dataHierarchyItems[0]['list'] and \
        ',' not in dataHierarchyItems[0]['list'] and ' ' not in dataHierarchyItems[0]['list']:  # choice among docType
        if not isinstance(value, tuple):
          logging.info('Not a tuple: %s : %s', key, value)
        if not isDocID(value[0]):
          value = value[0]
        elif value[2]:
          value = value[2]
      elif isinstance(value, list):
        value = ', '.join([str(i) for i in value])
      if isinstance(value, tuple) and len(value) == 4 and isDocID(value[0]):
        value = 'Cannot resolve link'
      labelStr = f'<b>{key}:</b><br>{value}<br><br>'
      if isinstance(value, tuple) and len(value) == 4:
        k, v = tuple2html(key, value)
        labelStr = f'<b>{k}:</b><br>{v}<br><br>'
      # if isinstance(value, dict):
      # newValue = {}
      # for k, v in value.items():
      #   if isinstance(v, tuple) and len(v) == 4:
      #     k2, v2 = tuple2html(k, v)
      #     newValue[k2] = v2
      #   elif isinstance(v, (list, tuple)):
      #     newValue[k] = v[0]
      #   else:
      #     newValue[k] = v
      # labelStr = f'{cssStyleHtmlEditors}<b>{key}:</b><br>{dict2ul(newValue)}<br><br>'
    return makeStringWrappable(labelStr)  # makeStringsWrappable could force wrap in html-statement in rare cases

  def addContent(self, key: str, value: Any) -> None:
    """Appends formatted Content to the Label of this Widget, see self.formatContent for details"""
    self.content += self.formatContent(key, value)
    self.contentLabel.setText(self.content.removesuffix("<br><br>"))
