""" ListItemDelegate module used for the table views """
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QStyleOptionViewItem, QWidget


class ListItemDelegate(QStyledItemDelegate):
  """
  Delegate for creating the line edit with lookup icon for the iri column in data hierarchy editor tables
  """
  def __init__(self, docTypesLabels:list[tuple[str,str]]):
    """
    Args:
      docTypeLabels (list): list of docTypes and docLabels
    """
    super().__init__()
    self.docTypesLabels = docTypesLabels


  def createEditor(self,
                   parent: QWidget,
                   option: QStyleOptionViewItem,
                   index:  QModelIndex | QPersistentModelIndex) -> QWidget:
    """
    Disable the editor for the whole column by simply returning None
    Args:
      parent (QWidget): Parent table view.
      option (QStyleOptionViewItem): Style option for the cell represented by index.
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.

    Returns: QLineEdit widget
    """
    # skip last row
    indexName = index.model().index(index.row(), 0)
    if not indexName.data():
      return None                                                                 # type: ignore[return-value]
    # remove listItem data
    indexListFree = index.model().index(index.row(), 5)
    index.model().setData(indexListFree, '')
    # do conventional step
    comboBox = QComboBox(parent)
    _ = [comboBox.addItem(text, data) for (data, text) in [('','')]+self.docTypesLabels]
    return comboBox

  def setEditorData(self,
                    editor: QWidget,
                    index: QModelIndex | QPersistentModelIndex) -> None:
    """
    Set the data in the editor

    Args:
      editor (QWidget): widget to set data in
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.
    """
    current_text = index.data(Qt. EditRole)                                       # type: ignore[attr-defined]
    editor.setCurrentText(current_text)                                           # type: ignore[attr-defined]
    return


  def setModelData(self,
                   editor: QWidget,
                   model: QAbstractItemModel,
                   index: QModelIndex | QPersistentModelIndex) -> None:
    """
    Change data in model accordingly

    Args:
      editor (QWidget): widget to set data in
      model (QAbstractItemModel): model to change
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.
    """
    model.setData(index, editor.currentText(), Qt.EditRole)                       # type: ignore[attr-defined]
    return


  def updateEditorGeometry(self,
                           editor: QWidget,
                           option: QStyleOptionViewItem,
                           index: QModelIndex | QPersistentModelIndex) -> None:
    """
    Change size of field

    Args:
      editor (QWidget): widget to set data in
      option (QStyledOptionViewItem): information on the geometry, same as paint
      index (Union[QModelIndex, QPersistentModelIndex]): Cell index.
    """
    editor.setGeometry(option.rect)                                               # type: ignore[attr-defined]
    return
