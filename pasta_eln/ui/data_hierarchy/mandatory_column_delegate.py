""" MandatoryColumnDelegate  module used for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: mandatory_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information

from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QRect
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QRadioButton, QStyle, QStyledItemDelegate, QStyleOptionButton, QStyleOptionViewItem,
                               QWidget)


class MandatoryColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the radio buttons for the mandatory column in data hierarchy editor tables
  """
  def __init__(self) -> None:
    super().__init__()
    self.radioButton = QRadioButton()
    self.radioButton.ensurePolished()                                 # apply theme stylesheet to the template

  def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
    """Hide the raw 'T' value; the radio indicator shows it
    Args:
      option (QStyleOptionViewItem): option for this icon
      index (CellIndex): number of the icon
    """
    super().initStyleOption(option, index)
    option.text = ''


  def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
            ) -> None:
    """
    Draws the mandatory radio indicator centered in the cell; the add-row stays empty
    Args:
      painter (QPainter): Painter instance for painting the button
      option (QStyleOptionViewItem): Style option for the cell represented by index
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index
    """
    super().paint(painter, option, index)                                 # cell background, text hidden below
    if not index.model().index(index.row(), 0).data():
      return
    style = self.radioButton.style()
    opt = QStyleOptionButton()
    opt.initFrom(self.radioButton)
    size     = style.pixelMetric(QStyle.PixelMetric.PM_ExclusiveIndicatorWidth, opt, self.radioButton)
    opt.rect = QRect(0, 0, size, size)
    opt.rect.moveCenter(option.rect.center())
    opt.state |= QStyle.StateFlag.State_On if index.data()=='T' else QStyle.StateFlag.State_Off
    style.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorRadioButton, opt, painter, self.radioButton)


  def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem,
                  index: QModelIndex | QPersistentModelIndex) -> bool:
    """
    In case of mouse click event, the model data is toggled for the respective table cell index
    Args:
      event (QEvent): The editor event information
      model (QAbstractItemModel): Model data representing the table view
      option (QStyleOptionViewItem): QStyleOption for the table cell
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index

    Returns (bool): True/False
    """
    if event.type() == QEvent.Type.MouseButtonRelease:
      indexName = model.index(index.row(), 0)
      if indexName.data():
        isMandatory = index.data()=='T'
        model.setData(index, '' if isMandatory else 'T')                        # invert mandatory after click
    return super().editorEvent(event, model, option, index)


  def createEditor(self, _0: QWidget, _1: QStyleOptionViewItem,
                   _2: QModelIndex | QPersistentModelIndex) -> QWidget:
    """ Disable the editor for the whole mandatory column by simply returning None """
    return None                                                                   # type: ignore[return-value]
