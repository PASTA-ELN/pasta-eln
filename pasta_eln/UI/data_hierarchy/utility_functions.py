""" Utility function used by the data hierarchy configuration module """
#  PASTA-ELN and all its sub-parts are covered by the MIT license
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: utility_functions.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information

from PySide6.QtCore import QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QStyleOptionViewItem


def is_click_within_bounds(event: QEvent,
                           option: QStyleOptionViewItem) -> bool:
  """
  Check if the click event happened within the rect area of the QStyleOptionViewItem
  Args:
    event (QEvent): Mouse event captured from the view
    option (QStyleOptionViewItem): Option send during the edit event

  Returns (bool): True/False

  """
  if (event and option
      and event.type() == QEvent.Type.MouseButtonRelease
      and isinstance(event, QMouseEvent)):
    e = QMouseEvent(event)
    click_x = e.x()
    click_y = e.y()
    r = option.rect                                                               # type: ignore[attr-defined]
    return (r.left() < click_x < r.left() + r.width()
            and r.top() < click_y < r.top() + r.height())
  return False
