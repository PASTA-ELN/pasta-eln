"""Qt relationship graph used by the Details pane."""
from __future__ import annotations

import math
from collections import deque
from typing import Any

from PySide6.QtCore import QPointF, Qt, Slot
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (QCheckBox, QGraphicsLineItem, QGraphicsScene,
                               QGraphicsSimpleTextItem, QGraphicsView, QLabel, QSpinBox, QVBoxLayout, QWidget)
from pasta_eln.ui.details.node_item import NodeItem
from pasta_eln.ui.gui_communicate import Communicate


class RelationshipView(QWidget):
  """Interactive, bounded relationship view for a selected document."""

  def __init__(self, comm: Communicate, parent: QWidget | None = None) -> None:
    super().__init__(parent)
    self.comm = comm
    self.graph: dict[str, Any] = {'nodes': [], 'edges': []}
    self.rootID = ''
    self.scene = QGraphicsScene(self)
    self.view = QGraphicsView(self.scene)
    self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    self.depth = QSpinBox()
    self.depth.setRange(1, 10)
    self.depth.setValue(2)
    self.depth.setToolTip('Number of relationship levels shown from the selected item')
    self.neighbours = QSpinBox()
    self.neighbours.setRange(1, 500)
    self.neighbours.setValue(50)
    self.neighbours.setToolTip('Maximum neighbours considered for each node')
    self.showHierarchy = QCheckBox('Hierarchy')
    self.showHierarchy.setChecked(True)
    self.showLinks = QCheckBox('Links')
    self.showLinks.setChecked(True)
    self.comm.backendThread.worker.beSendRelationships.connect(self.onGetRelationships)
    controls = QVBoxLayout()
    controls.setContentsMargins(0, 0, 0, 0)
    controls.addWidget(QLabel('Levels from selected item'))
    controls.addWidget(self.depth)
    controls.addWidget(QLabel('Neighbours per node'))
    controls.addWidget(self.neighbours)
    controls.addWidget(self.showHierarchy)
    controls.addWidget(self.showLinks)
    layout = QVBoxLayout(self)
    layout.addLayout(controls)
    layout.addWidget(self.view)
    # Signals -> always paint
    self.depth.valueChanged.connect(self.paint)
    self.neighbours.valueChanged.connect(self.paint)
    self.showHierarchy.toggled.connect(self.paint)
    self.showLinks.toggled.connect(self.paint)

  def setRootID(self, rootID: str) -> None:
    """Set the document around which the relationship graph is rendered."""
    self.rootID = rootID
    self.paint()

  @Slot(dict)
  def onGetRelationships(self, graph: dict[str, Any]) -> None:
    """Store backend relationship data and render it for the selected document."""
    if self.rootID:
      self.graph = graph
      self.paint()

  def centreOnNode(self, docID: str) -> None:
    """Centre the view on a visible node."""
    for item in self.scene.items():
      if isinstance(item, NodeItem) and item.docID == docID:
        self.view.centerOn(item)
        return

  def paint(self) -> None:
    """Render the selected neighbourhood using a compact radial layout."""
    self.scene.clear()
    if not self.rootID:
      return
    nodes = {node['id']: node for node in self.graph.get('nodes', [])}
    if self.rootID not in nodes:
      return
    edgeKinds = {'hierarchy', 'link'} if self.showLinks.isChecked() else {'hierarchy'}
    if not self.showHierarchy.isChecked():
      edgeKinds.discard('hierarchy')
    adjacency: dict[str, list[tuple[str, str]]] = {docID: [] for docID in nodes}
    edges = [edge for edge in self.graph.get('edges', []) if edge['kind'] in edgeKinds]
    for edge in edges:
      if edge['source'] in adjacency and edge['target'] in adjacency:
        adjacency[edge['source']].append((edge['target'], edge['kind']))
        adjacency[edge['target']].append((edge['source'], edge['kind']))
    limit = self.neighbours.value()
    adjacency = {docID: values[:limit] for docID, values in adjacency.items()}
    distances = {self.rootID: 0}
    queue = deque([self.rootID])
    while queue:
      current = queue.popleft()
      if distances[current] >= self.depth.value():
        continue
      for neighbour, _ in adjacency.get(current, []):
        if neighbour not in distances:
          distances[neighbour] = distances[current] + 1
          queue.append(neighbour)
    visible = {docID for docID in distances if docID in nodes}
    positions: dict[str, QPointF] = {self.rootID: QPointF(0, 0)}
    for level in range(1, self.depth.value() + 1):
      levelNodes = sorted(docID for docID in visible if distances[docID] == level)
      for index, docID in enumerate(levelNodes):
        angle = (index / max(1, len(levelNodes))) * 6.28318
        radius = 140 * level
        positions[docID] = QPointF(radius * math.cos(angle), radius * math.sin(angle))
    for edge in edges:
      if edge['source'] in visible and edge['target'] in visible:
        line = QGraphicsLineItem(positions[edge['source']].x(), positions[edge['source']].y(),
                                 positions[edge['target']].x(), positions[edge['target']].y())
        line.setPen(QPen(QColor('#8a8a8a' if edge['kind'] == 'hierarchy' else '#4d8dcc'), 1.5))
        self.scene.addItem(line)
    for docID, position in positions.items():
      item = NodeItem(docID, QColor('#d8b365' if docID == self.rootID else '#82b7d9'))
      item.setToolTip(nodes[docID]['name'])
      item.clicked.connect(self.centreOnNode)
      item.setPos(position)
      self.scene.addItem(item)
      label = QGraphicsSimpleTextItem(str(nodes[docID]['name'])[:28], item)
      label.setPos(-label.boundingRect().width() / 2, 27)
    self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-40, -40, 40, 40))
    self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
