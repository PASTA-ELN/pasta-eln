""" MandatoryColumnDelegate  module used for the table views """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: mandatory_column_delegate.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Union
from pandas import DataFrame
from PySide6.QtCore import QAbstractItemModel, QEvent, QModelIndex, QPersistentModelIndex, QRect, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QRadioButton, QStyle, QStyledItemDelegate, QStyleOptionButton,
                               QStyleOptionViewItem, QWidget)


class MandatoryColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the radio buttons for the mandatory column in data hierarchy editor tables
  """

  def __init__(self, df:DataFrame, group:str) -> None:
    """
      Constructor

    Args:
      df (DataFrame): pandas dataframe containing the entire schema
      group (str): string of this group/class
    """
    super().__init__()
    self.df = df
    self.group = group

  def paint(self,
            painter: QPainter,
            option: QStyleOptionViewItem,
            index: Union[QModelIndex, QPersistentModelIndex]) -> None:
    """
    Draws the mandatory radio button within the cell represented by index
    Args:
      painter (QPainter): Painter instance for painting the button.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns: None

    """
    widget = option.widget  # type: ignore[attr-defined]
    style = widget.style() if widget else QApplication.style()
    opt = QStyleOptionButton()
    radio_button = QRadioButton()
    option_rect = option.rect  # type: ignore[attr-defined]
    opt.rect = QRect(option_rect.left() + option_rect.width() / 2 - 10,  # type: ignore[attr-defined]
                     option_rect.top(),
                     option_rect.width(),
                     option_rect.height())
    dfSub = self.df[self.df['class']==self.group]
    if index.row()>len(dfSub):
      return
    trues = dfSub[dfSub['idx']==index.row()]['mandatory'].values
    isMandatory = len(trues)==1 and trues[0]=='T'
    opt.state = QStyle.StateFlag.State_On if isMandatory else QStyle.StateFlag.State_Off  # type: ignore[attr-defined]
    style.drawControl(QStyle.ControlElement.CE_RadioButton, opt, painter, radio_button)


  def editorEvent(self,
                  event: QEvent,
                  model: QAbstractItemModel,
                  option: QStyleOptionViewItem,
                  index: Union[QModelIndex, QPersistentModelIndex]) -> bool:
    """
    In case of mouse click event, the model data is toggled for the respective table cell index
    Args:
      event (QEvent): The editor event information.
      model (QAbstractItemModel): Model data representing the table view.
      option (QStyleOptionViewItem): QStyleOption for the table cell.
      index (Union[QModelIndex, QPersistentModelIndex]): Table cell index.

    Returns (bool): True/False
    """
    if event.type() == QEvent.Type.MouseButtonRelease:
      column= (self.df['class']==self.group) & (self.df['idx']==index.row())
      trues = self.df[column]['mandatory'].values
      isMandatory = len(trues)==1 and trues[0]=='T'
      self.df.loc[column,   'mandatory']= '' if isMandatory else 'T'
    return super().editorEvent(event, model, option, index)


  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index: Union[QModelIndex, QPersistentModelIndex]) -> QWidget:
    """
    Disable the editor for the whole mandatory column by simply returning None
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: None
    """
    return None  # type: ignore[return-value]
