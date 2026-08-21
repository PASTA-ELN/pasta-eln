""" Widget for displaying a project in the ProjectSidebar"""
from typing import Any, override
import pandas as pd
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout
from pasta_eln.misc_tools import makeStringWrappable
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Label


class ProjectCard(QFrame):
  """Widget for displaying a project in the ProjectSidebar"""
  clicked = Signal()

  def __init__(self, comm: Communicate, project: pd.Series[Any]) -> None:
    """
    Create a new project card

    Args:
      comm (Communicate): The communication object
      project (pd.Series[Any]): The project data
    """
    super().__init__()
    self.comm = comm
    self.project = project

    # Title-Label
    hidden = '     \U0001F441' if 'F' in self.project['show'] else ''
    self.titleLabel = Label(makeStringWrappable(self.project['name'] + hidden), 'h3')
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setWordWrap(True)

    # Info-Label (smaller text below name of project)-
    # currently only shows status, could display more or other info like tags and Last edited
    self.infoLabel = Label(makeStringWrappable(self.project['status']))
    self.infoLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.infoLabel.setWordWrap(True)

    # Style
    self.setFrameShape(QFrame.Shape.Panel)
    shadow = QGraphicsDropShadowEffect(self, offset=QPointF(0, 1), blurRadius=8, color=QColor(0, 0, 0, 25))
    self.setGraphicsEffect(shadow)
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    color = self.comm.palette.getThemeColor('background', 'panel')
    borderColor = self.comm.palette.alterColor(self.comm.palette.getThemeColor('border', 'base'), 125)
    selectionColor = self.comm.palette.getThemeColor('primary', 'base')
    self.defaultCSS = f"""
    ProjectCard {{
      background-color: {color};
      border: 1px solid {borderColor};
      border-left: 4px solid transparent;
    }}
    ProjectCard[highlight="true"] {{
      border-left-color: {selectionColor};
    }}
    """
    self.setStyleSheet(self.defaultCSS)

    # Layout
    self.mainL = QVBoxLayout()
    self.mainL.addWidget(self.titleLabel)
    self.mainL.addWidget(self.infoLabel)
    self.setLayout(self.mainL)

    # Signals
    self.clicked.connect(self.onClick)


  @override
  def mousePressEvent(self, event: QMouseEvent) -> None:
    """
    Override Event to simulate click and Position of potential drag start

    Args:
      event (QMouseEvent): The mouse press event
    """
    if event.button() == Qt.MouseButton.LeftButton:
      self.clicked.emit()
    super().mousePressEvent(event)


  def onClick(self) -> None:
    """
    What happens when clicking on this widget
    """
    self.comm.projectID = self.project['id']
    self.comm.changeProject.emit(self.project['id'], '')
    self.comm.changeSidebar.emit('redraw')


  def highlight(self) -> None:
    """
    Updates the Style of this Item to highlight it
    """
    self.setProperty('highlight', True)
    self.setStyleSheet(self.defaultCSS)


  def lowlight(self) -> None:
    """
    Updates the Style of this Item to reset the highlight
    """
    self.setProperty('highlight', False)
    self.setStyleSheet(self.defaultCSS)
