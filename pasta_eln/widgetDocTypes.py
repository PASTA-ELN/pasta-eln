""" widget that shows the table and the details of the items """

from random import randint
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QLabel, \
                              QScrollArea     # pylint: disable=no-name-in-module

from .widgetTable import Table
from .widgetDetails import Details

class DocTypes(QWidget):
  """ widget that shows the table and the details of the items """
  def __init__(self, comm):
    super().__init__()

    # GUI elements
    table = Table(comm)
    details = Details(comm)
    splitter = QSplitter()
    splitter.setHandleWidth(10)
    splitter.addWidget(table)
    splitter.addWidget(details)
    splitter.setSizes([1,1])
    mainLayout = QVBoxLayout()
    mainLayout.addWidget(splitter)
    self.setLayout(mainLayout)
