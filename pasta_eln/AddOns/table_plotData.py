"""example add-on: plot data from files

THIS IS A VERY ADVANCED ADD-ON TUTORIAL
This tutorial teaches
- how to plot the data from files
"""
import matplotlib
import pandas as pd
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem
from pasta_eln.miscTools import MplCanvas, callDataExtractor, getDoc, isFloat
from pasta_eln.UI.guiStyle import Label, space, widgetAndLayout

# The following two variables are mandatory
description  = 'Default data plot'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}


class DataAnalyse(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, df, data, widget):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      df (pandas dataframe): all metadata
      data (list): all data
    """
    super().__init__()
    self.df = df
    self.data = data
        # GUI elements
    self.setWindowTitle('Analyze data')
    self.setMinimumWidth(1050)  #set size to match 4 blocks of 8bytes
    masterL = QHBoxLayout(self)
    masterL.setSpacing(space['s'])
    self.setStyleSheet(f"QLineEdit, QComboBox {{  {widget.comm.palette.get('secondaryText','color')} }}")
    _, mainL = widgetAndLayout('V', masterL, spacing='s')
    self.rightW = QTableWidget(self.df.shape[0], 1)
    for row in range(self.rightW.rowCount()):
      item = QTableWidgetItem(self.df['name'].iloc[row])
      item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
      item.setCheckState(Qt.CheckState.Checked)
      self.rightW.setItem(row, 0, item)
    self.rightW.setStyleSheet('QTableView::indicator {width: 24px; height: 24px;}')
    self.rightW.verticalHeader().hide()
    self.rightW.horizontalHeader().hide()
    self.rightW.clicked.connect(self.cellClicked)
    self.rightW.setAlternatingRowColors(True)
    header = self.rightW.horizontalHeader()
    header.setStyleSheet('QHeaderView::section {padding: 0px 5px; margin: 0px;}')
    header.setStretchLastSection(True)
    masterL.addWidget(self.rightW)
    self.columns = list(data[0].columns)

    #graph
    self.graphW, graphL = widgetAndLayout('V', None)
    self.graph = MplCanvas(self, width=5, height=4, dpi=100)
    self.graphToolbar = NavigationToolbar(self.graph, self)
    self.graphToolbar.setIconSize(QSize(24, 24))
    self.graphToolbar.setStyleSheet('QToolButton {min-width: 18px; min-height: 24px;}')
    graphL.addWidget(self.graphToolbar)
    graphL.addWidget(self.graph)
    mainL.addWidget(self.graphW, stretch=1)

    #X-Axis
    _, rowXL = widgetAndLayout('H', mainL, 'm', 's', '0', 's')
    Label('x-axis:','h2',rowXL)
    self.xAxisCB = QComboBox()
    self.xAxisCB.addItems(self.columns)
    self.xAxisCB.currentTextChanged.connect(self.refresh)
    rowXL.addWidget(self.xAxisCB)
    Label('min:','',rowXL)
    self.xAxisMin = QLineEdit('')
    self.xAxisMin.textChanged.connect(self.refresh)
    rowXL.addWidget(self.xAxisMin)
    Label('max:','',rowXL)
    self.xAxisMax = QLineEdit('')
    self.xAxisMax.textChanged.connect(self.refresh)
    rowXL.addWidget(self.xAxisMax)
    Label('label:','',rowXL)
    self.xAxisLabel = QLineEdit('')
    self.xAxisLabel.textChanged.connect(self.refresh)
    rowXL.addWidget(self.xAxisLabel)

    #Y-Axis
    self.rowYW, rowYL = widgetAndLayout('H', mainL, 'm', 's', '0', 's')
    Label('y-axis:','h2',rowYL)
    self.yAxisCB = QComboBox()
    self.yAxisCB.addItems(self.columns)
    self.yAxisCB.currentTextChanged.connect(self.refresh)
    rowYL.addWidget(self.yAxisCB)
    Label('min:','',rowYL)
    self.yAxisMin = QLineEdit('')
    self.yAxisMin.textChanged.connect(self.refresh)
    rowYL.addWidget(self.yAxisMin)
    Label('max:','',rowYL)
    self.yAxisMax = QLineEdit('')
    self.yAxisMax.textChanged.connect(self.refresh)
    rowYL.addWidget(self.yAxisMax)
    Label('label:','',rowYL)
    self.yAxisLabel = QLineEdit('')
    self.yAxisLabel.textChanged.connect(self.refresh)
    rowYL.addWidget(self.yAxisLabel)

    self.refresh()

  def refresh(self):
    matplotlib.pyplot.close('all')
    self.graph.axes.cla()
    for idx, iData in enumerate(self.data):
      item = self.rightW.item(idx, 0)
      if item.checkState() != Qt.CheckState.Checked:
        continue
      x = iData[self.xAxisCB.currentText()]
      y = iData[self.yAxisCB.currentText()]
      label = list(self.df['name'])[idx]
      self.graph.axes.plot(x, y, label=label)
    self.graph.axes.legend()
    xMin = None if self.xAxisMin.text()=='' or not isFloat(self.xAxisMin.text()) else float(self.xAxisMin.text())
    xMax = None if self.xAxisMax.text()=='' or not isFloat(self.xAxisMin.text()) else float(self.xAxisMax.text())
    yMin = None if self.yAxisMin.text()=='' or not isFloat(self.xAxisMin.text()) else float(self.yAxisMin.text())
    yMax = None if self.yAxisMax.text()=='' or not isFloat(self.xAxisMin.text()) else float(self.yAxisMax.text())
    self.graph.axes.set_xlabel(self.xAxisLabel.text() or self.xAxisCB.currentText())
    self.graph.axes.set_ylabel(self.yAxisLabel.text() or self.yAxisCB.currentText())
    self.graph.axes.set_xlim(left=xMin, right=xMax)
    self.graph.axes.set_ylim(bottom=yMin, top=yMax)
    self.graph.axes.tick_params(axis='both', direction='in')
    self.graph.draw() # Trigger the canvas to update and redraw
    self.graphToolbar.show()
    self.graph.show()


  def cellClicked(self, item):
    """ after table is clicked: refresh graph """
    self.refresh()


def main(comm, df, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        comm (communication): pasta communication layer
        df (Dataframe): dataframe with the data to plot. The docIDand path columns are of most interest
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    # no cleaning needed since we only use id and path columns
    data = []
    for idx, row in df.iterrows():
        res = callDataExtractor(row['docID'], comm)
        if res is None:
            continue
        # Here you can process the extracted data further, e.g., plot it
        if isinstance(res, pd.DataFrame):
            data.append(res)
        else:
            print(f"Extracted data is not a DataFrame. {row['path']}")
    if data:
        dataAnalyse = DataAnalyse(df, data, widget)
        dataAnalyse.exec()
    return True
