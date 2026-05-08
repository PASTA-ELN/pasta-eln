""" Widget for displaying a project in the ProjectSidebar"""
from typing import override

import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout

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
    color = self.comm.palette.getThemeColor("foreground", "disabled")
    self.infoLabel.setStyleSheet(f"color: {color}; border: none;")

    # Style
    self.setFrameShape(QFrame.Shape.Panel)
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    color = self.comm.palette.getThemeColor("background", "table")
    self.defaultCSS = f"""
    ProjectCard {{
      background-color: {color};
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
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.titleLabel)
    self.layout.addWidget(self.infoLabel)
    # self.layout.setContentsMargins(0,0,0,0)
    # self.layout.setSpacing(0)
    self.setLayout(self.layout)

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
