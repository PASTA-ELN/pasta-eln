"""The Top bar of the tableView containing action-buttons"""
from PySide6.QtWidgets import QWidget

from gui_communicate import Communicate
from ui_new.table_view.table_view import TableView


class Buttonbar(QWidget):
  """ """

  def __init__(self, comm: Communicate, tableView: TableView, docType: str):
    super().__init__()
    self.comm = comm
    self.tableView = tableView
    self.docType = docType
