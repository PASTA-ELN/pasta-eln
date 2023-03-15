from PySide6.QtWidgets import QTreeView, QAbstractItemView
from .widgetProjectLeafRenderer import ProjectLeafRenderer

class TreeView(QTreeView):
  def __init__(self, parent):
    super().__init__(parent)
    self.setHeaderHidden(True)
    self.setStyleSheet('QTreeView::branch {border-image: none;}')
    self.renderer = ProjectLeafRenderer()
    self.setItemDelegate(self.renderer)
    self.setDragDropMode(QAbstractItemView.InternalMove)
