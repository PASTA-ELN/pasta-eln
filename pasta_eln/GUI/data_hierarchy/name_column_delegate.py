""" NameColumnDelegate module used for the table views """
from pandas import DataFrame
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Signal
from PySide6.QtWidgets import QLineEdit, QStyledItemDelegate, QStyleOptionViewItem, QWidget


class NameColumnDelegate(QStyledItemDelegate):
  """
  Delegate for creating the line edit with lookup icon for the iri column in data hierarchy editor tables
  """
  add_row_signal = Signal()

  def __init__(self, df:DataFrame, group:str) -> None:
    """
    Args:
      df (DataFrame): pandas dataframe containing the entire schema
      group (str): string of this group/class
    """
    super().__init__()
    self.df = df
    self.group = group


  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index:  QModelIndex | QPersistentModelIndex) -> QWidget:
    """
    Creates the line edit with lookup icon for the iri column cell represented by index

    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: QLineEdit widget
    """
    dfSub = self.df[self.df['class']==self.group]
    if index.row()>len(dfSub):
      return QWidget(parent)
    trues = dfSub[dfSub['idx']==index.row()]['name'].isin(['name','tags','comment']).values
    if len(trues)>0 and self.group=='' and trues[0]:
      return QWidget(parent)
    lineEdit = QLineEdit(parent)
    return lineEdit


  def destroyEditor(self, editor:QWidget, index:QModelIndex | QPersistentModelIndex) -> None:
    """ destroy the line editor

    Args:
      editor (QWidget): Parent table view
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.
    """
    dfSub = self.df[self.df['class']==self.group]
    if index.row()==len(dfSub):
      self.add_row_signal.emit()
    super().destroyEditor(editor, index)
    return
