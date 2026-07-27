"""The Top bar of the tableView containing action-buttons"""
from PySide6.QtWidgets import QWidget

from pasta_eln.ui.gui_communicate import Communicate
from pasta_eln.ui_new.table_view.table_view import TableView


class Buttonbar(QWidget):
  """The Top bar of the tableView containing action-buttons"""

  def __init__(self, comm: Communicate, tableView: TableView, docType: str):
    super().__init__()
    self.comm = comm
    self.tableView = tableView
    self.docType = docType
