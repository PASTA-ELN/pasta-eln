""" Widget for displaying a project in the ProjectSidebar"""
from typing import override

import pandas as pd
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout

from pasta_eln.misc_tools import makeStringWrappable
from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui.gui_style import Label


class ProjectCard(QFrame):
  """ Widget for displaying a project in the ProjectSidebar"""
  clicked = Signal()

  def __init__(self, comm: Communicate, project: pd.DataFrame):
    super().__init__()
    self.comm = comm
    self.project = project

    # Title-Label
    self.titleLabel = Label(makeStringWrappable(self.project["name"]), "h3")
    self.titleLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.titleLabel.setWordWrap(True)

    # Info-Label (smaller text below name of project)-
    # currently only shows status, could display more or other info like tags and Last edited
    self.infoLabel = Label(makeStringWrappable(self.project["status"]))
    self.infoLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.infoLabel.setWordWrap(True)

    # Style
    self.setFrameShape(QFrame.Shape.Panel)
    shadow = QGraphicsDropShadowEffect(self, offset=QPointF(0, 1), blurRadius=8, color=QColor(0, 0, 0, 25))
    self.setGraphicsEffect(shadow)
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    color = self.comm.palette.getThemeColor("background", "table")
    borderColor = self.comm.palette.alterColor(self.comm.palette.getThemeColor("border", "base"), 125)
    self.defaultCSS = f"""
    ProjectCard {{
      background-color: {color};
      border: 1px solid {borderColor};
    }}
    ProjectCard[highlight="true"] {{
      background-color:{self.comm.palette.getThemeColor("primary", "base")};
    }}
    ProjectCard[highlight="true"] QLabel{{
      color:{self.comm.palette.getThemeColor("background", "base")};
    }}
    """
    self.setStyleSheet(self.defaultCSS)

    # Layout
    self.mainLayout = QVBoxLayout()
    self.mainLayout.addWidget(self.titleLabel)
    self.mainLayout.addWidget(self.infoLabel)
    # self.mainLayout.setContentsMargins(0,0,0,0)
    # self.mainLayout.setSpacing(0)
    self.setLayout(self.mainLayout)

    # Signals
    self.clicked.connect(self.onClick)

  @override
  def mousePressEvent(self, event):
    """
    Override Event to simulate click and Position of potential drag start.
    """
    if event.button() == Qt.MouseButton.LeftButton:
      self.clicked.emit()
    super().mousePressEvent(event)

  def onClick(self):
    """
    What happens when clicking on this widget
    """
    self.comm.projectID = self.project["id"]
    self.comm.changeProject.emit(self.project["id"], "")

  def highlight(self):
    """
    Updates the Style of this Item to highlight it
    """
    self.setProperty("highlight", True)
    self.setStyleSheet(self.defaultCSS)

  def lowlight(self):
    """
    Updates the Style of this Item to reset the highlight
    """
    self.setProperty("highlight", False)
    self.setStyleSheet(self.defaultCSS)
