"""A filter row used to filter a document table."""
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QWidget

from pasta_eln.ui.widget import Button

if TYPE_CHECKING:
  from pasta_eln.ui.table.table import TableView


class FilterRow(QWidget):
  """A field selector and text input used to filter a document table."""

  def __init__(self, tableView: 'TableView') -> None:
    """
    Create a new filter row

    Args:
      tableView (TableView): The table view to filter
    """
    super().__init__()
    self.column = QComboBox(self)
    self.column.addItems(tableView.tableData.columns.to_list())
    self.text = QLineEdit(self)
    self.text.setPlaceholderText('Filter text')
    self.removeButton = Button('', tableView, icon='ri.subtract-line', tooltip='Remove filter', flat=True)
    self.removeButton.clicked.connect(lambda: tableView.removeFilter(self))
    self.column.currentTextChanged.connect(lambda _: tableView.paint())
    self.text.textChanged.connect(lambda _: tableView.paint())

    layout = QHBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(self.column)
    layout.addWidget(self.text, stretch=1)
    layout.addWidget(self.removeButton)
