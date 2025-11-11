""" Analyser add-on with much functionality: shows how complex add-ons can be. But do not have to."""
import itertools
import matplotlib
import matplotlib.pyplot
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QLineEdit,  # pylint: disable=no-name-in-module
                               QVBoxLayout)
from scipy import stats
from sklearn.metrics import r2_score
from pasta_eln.miscTools import MplCanvas, dfConvertColumns, isFloat
from pasta_eln.UI.guiStyle import Label, space, widgetAndLayout

# The following two variables are mandatory
description  = 'Default metadata plot'  #short description that is shown in the menu
reqParameter = {} #possibility for required parameters: like API-key, etc. {'API': 'text'}


class DataAnalyse(QDialog):
  """ Editor to change metadata of binary file """
  def __init__(self, df, widget):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
      df (pandas dataframe): all data
    """
    super().__init__()
    prop_cycle = matplotlib.pyplot.rcParams['axes.prop_cycle']
    self.colors = itertools.cycle(prop_cycle.by_key()['color'])
    self.setStyleSheet(f"QLineEdit, QComboBox {{  {widget.comm.palette.get('secondaryText','color')} }}")
    self.df = df
    columns = []
    for col in df.columns:
      if pd.api.types.is_numeric_dtype(df[col].dtype):
        columns.append(col)

    # GUI elements
    self.setWindowTitle('Analyze metadata')
    self.setMinimumWidth(1050)  #set size to match 4 blocks of 8bytes
    mainL = QVBoxLayout(self)
    mainL.setSpacing(space['s'])

    #graph
    self.graphW, graphL = widgetAndLayout('V', None)
    self.graph = MplCanvas(self, width=5, height=4, dpi=100)
    self.graphToolbar = NavigationToolbar(self.graph, self)
    self.graphToolbar.setIconSize(QSize(24, 24))
    self.graphToolbar.setStyleSheet('QToolButton {min-width: 18px; min-height: 24px;}')
    graphL.addWidget(self.graphToolbar)
    graphL.addWidget(self.graph)
    mainL.addWidget(self.graphW, stretch=1)

    #Graph type
    _, rowType = widgetAndLayout('H', mainL, 'm', 's', '0', 's')
    Label('graph type:','h2',rowType)
    self.typeCB = QComboBox()
    self.typeCB.addItems(['x-y plot','histogram'])
    self.typeCB.currentTextChanged.connect(self.changePlotType)
    rowType.addWidget(self.typeCB)
    rowType.addSpacing(1)
    self.subtypeCB = QComboBox()
    self.subtypeCB.addItems(['points','points & lines','lines'])
    self.subtypeCB.currentTextChanged.connect(self.refresh)
    rowType.addWidget(self.subtypeCB)
    rowType.addSpacing(1)

    #X-Axis
    self.rowXW, rowXL = widgetAndLayout('H', mainL, 'm', 's', '0', 's')
    Label('x-axis:','h2',rowXL)
    self.xAxisCB = QComboBox()
    self.xAxisCB.addItems(columns)
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
    self.yAxisCB.addItems(columns)
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

    #Coloring
    _, rowCL = widgetAndLayout('H', mainL, 'm', 's', '0', 's')
    Label('color:','h2',rowCL)
    self.cAxisCB = QComboBox()
    self.cAxisCB.addItems(df.columns)
    self.cAxisCB.currentTextChanged.connect(self.refresh)
    rowCL.addWidget(self.cAxisCB)
    Label('min:','',rowCL)
    self.cAxisMin = QLineEdit('')
    self.cAxisMin.textChanged.connect(self.refresh)
    rowCL.addWidget(self.cAxisMin)
    Label('max:','',rowCL)
    self.cAxisMax = QLineEdit('')
    self.cAxisMax.textChanged.connect(self.refresh)
    rowCL.addWidget(self.cAxisMax)
    Label('label:','',rowCL)
    self.cAxisLabel = QLineEdit('')
    self.cAxisLabel.textChanged.connect(self.refresh)
    rowCL.addWidget(self.cAxisLabel)

    #final button box
    buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
    buttonBox.clicked.connect(self.cancel)
    mainL.addWidget(buttonBox)
    self.refresh()

  def changePlotType(self):
    """ change the main plot-type: changes also the list in subType and hence refreshes the graph"""
    if self.typeCB.currentText()=='x-y plot':
      self.rowYW.show()
      self.subtypeCB.clear()
      self.subtypeCB.addItems(['points','points & lines','lines'])
    if self.typeCB.currentText()=='histogram':
      self.rowYW.hide()
      self.subtypeCB.clear()
      self.subtypeCB.addItems(['histogram','cumulative distribution','distribution'])


  def refresh(self):
    """ repaint graph """
    try:
      self.df.sort_values(self.xAxisCB.currentText(), inplace=True)
    except KeyError:
      pass
    x = self.df[self.xAxisCB.currentText()]
    y = self.df[self.yAxisCB.currentText()]
    c = self.df[self.cAxisCB.currentText()]
    try:
      fit = np.polyfit(x, y, 1)
    except np.linalg.LinAlgError:
      fit = [np.nan, np.nan]
    xMin = None if self.xAxisMin.text()=='' or not isFloat(self.xAxisMin.text()) else float(self.xAxisMin.text())
    xMax = None if self.xAxisMax.text()=='' or not isFloat(self.xAxisMax.text()) else float(self.xAxisMax.text())
    yMin = None if self.yAxisMin.text()=='' or not isFloat(self.yAxisMin.text()) else float(self.yAxisMin.text())
    yMax = None if self.yAxisMax.text()=='' or not isFloat(self.yAxisMax.text()) else float(self.yAxisMax.text())
    infoText = ''

    matplotlib.pyplot.close('all')
    self.graph.axes.cla()
    #SCATTER PLOT
    if self.typeCB.currentText()=='x-y plot':
      # fit
      self.graph.axes.plot(x, np.polyval(fit, x), 'k--')
      text = f'y={fit[0]:.3f}*x+{fit[1]:.3f}' # : $R^2$={round(r2_score(y, np.polyval(fit, x)), 2)}' #Comment in and install sklearn
      self.graph.axes.text(x.mean(), np.polyval(fit, x.mean()), text, verticalalignment='top')
      self.graph.axes.set_ylim(bottom=yMin, top=yMax)
      self.graph.axes.set_ylabel(self.yAxisLabel.text() or self.yAxisCB.currentText())
      # real plot
      subType = self.subtypeCB.currentText()
      plotType = 'o' if subType=='points' else 'o-' if subType=='points & lines' else '-'
      for ci in np.unique(c):
        mask = c==ci
        self.graph.axes.plot(x[mask],y[mask], plotType, label=ci)

    # HISTOGRAM
    if self.typeCB.currentText()=='histogram':
      for ci in np.unique(c):
        mask = c==ci
        label = f'{ci} {np.mean(x[mask]):.2e}$\pm${np.std(x[mask]):.2e}'
        if self.subtypeCB.currentText()=='histogram':
          self.graph.axes.hist(x[mask], 20, label=label, alpha=0.5)
          self.graph.axes.set_ylabel('count')
        if self.subtypeCB.currentText()=='cumulative distribution':
          self.graph.axes.ecdf(x[mask], label=label)
          self.graph.axes.set_ylabel('cumulative distribution')
        if self.subtypeCB.currentText()=='distribution':
          res = stats.ecdf(x[mask])
          y_ = (res.cdf.probabilities[1:]-res.cdf.probabilities[:-1])/(res.cdf.quantiles[1:]-res.cdf.quantiles[:-1])
          x_ = (res.cdf.quantiles[1:]+res.cdf.quantiles[:-1])/2
          w_ = (res.cdf.quantiles[1:]-res.cdf.quantiles[:-1])
          color = next(self.colors)
          self.graph.axes.bar(x_, y_, width=w_, label=label, facecolor='none', linestyle='-', linewidth=1, edgecolor=color)
          self.graph.axes.set_ylabel('relative distribution')
      ksStats = stats.ks_2samp(x[mask], x[~mask])
      infoText = f'p-value={ksStats.pvalue:.3f}'

    # for all plots
    self.graph.axes.legend(title = self.cAxisLabel.text() or self.cAxisCB.currentText())
    xlim = self.graph.axes.set_xlim(left=xMin, right=xMax)
    ylim = self.graph.axes.get_ylim()
    self.graph.axes.set_xlabel(self.xAxisLabel.text() or self.xAxisCB.currentText())
    if infoText:
      self.graph.axes.text((xlim[0]+xlim[1])/2, ylim[1], infoText , horizontalalignment='center', verticalalignment='top')
    self.graph.axes.tick_params(axis='both', direction='in')
    self.graph.figure.tight_layout()
    self.graph.draw()
    self.graphToolbar.show()
    self.graph.show()
    return

  def cancel(self, btn):
    """ cancel selectedList to configuration and exit """
    self.reject()
    return


def main(comm, df, widget, parameter={}):
    """ main function: has to exist and is called by the menu
    Args:
        comm (communication): pasta communication layer
        df (Dataframe): dataframe with the data to plot
        widget (QWidget): allows to create new gui dialogs
        parameter (dict): ability to pass parameters

    Returns:
        bool: success
    """
    dataAnalyse = DataAnalyse(dfConvertColumns(df, 10), widget)
    dataAnalyse.exec()
