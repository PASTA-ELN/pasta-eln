""" filter manager for table models in pasta_eln UI"""
from enum import Enum
from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QComboBox, QLineEdit, QWidget
from .guiStyle import IconButton


class FilterItem:
  """Represents a single filter with its model and associated widgets"""

  def __init__(self, filterID: int, headerOptions: list[str], parentWidget:QWidget):
    """ Initialize

    Args:
      filterID (int): Unique identifier for the filter
      headerOptions (list[str]): List of column headers to filter on
      parentWidget: Parent widget for GUI elements
    """
    self.id = filterID
    self.model = QSortFilterProxyModel()
    self.model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    self.model.setFilterKeyColumn(0)

    # Create widgets
    self.select = QComboBox()
    self.select.addItems(headerOptions + ['rating'] if 'tag' in headerOptions else headerOptions)
    self.select.setMinimumWidth(max(len(i) for i in headerOptions) * 14)
    self.text = QLineEdit('')
    self.inverse = IconButton('ph.selection-inverse-fill', parentWidget,
                              [FilterCommand.SET_FILTER, filterID, 'invert'], None, checkable=True)
    self.delete = IconButton('fa5s.minus-square', parentWidget,
                              [FilterCommand.DELETE_FILTER, filterID], None)


class FilterManager:
  """Manages the chain of filters applied to a table model"""

  def __init__(self, baseModel: QStandardItemModel):
    """ Initialize the FilterManager
    Args:
      baseModel (QStandardItemModel): The initial model to apply filters to
    """
    self.baseModel = baseModel
    self.filters: dict[int, FilterItem] = {}
    self.nextID = 1
    self.modelChain: list[QStandardItemModel | QSortFilterProxyModel] = [baseModel]


  def addFilter(self, headerOptions: list[str], parentWidget:QWidget) -> FilterItem:
    """Add a new filter to the chain"""
    filterID = self.nextID
    self.nextID += 1
    filterItem = FilterItem(filterID, headerOptions, parentWidget)
    self.filters[filterID] = filterItem
    # Link to the current end of the chain
    filterItem.model.setSourceModel(self.modelChain[-1])
    self.modelChain.append(filterItem.model)
    return filterItem


  def removeFilter(self, filterID: int) -> None:
    """Remove a filter and rebuild the chain"""
    if filterID not in self.filters:
      return
    del self.filters[filterID]
    self.rebuildChain()
    return


  def rebuildChain(self) -> None:
    """Rebuild the model chain after filter removal"""
    self.modelChain = [self.baseModel]
    for filterID in sorted(self.filters.keys()):
      filterItem = self.filters[filterID]
      filterItem.model.setSourceModel(self.modelChain[-1])
      self.modelChain.append(filterItem.model)


  def getFinalModel(self) -> QStandardItemModel | QSortFilterProxyModel:
    """Get the final model in the chain (for table display)"""
    return self.modelChain[-1]


  def getFilter(self, filterID: int) -> FilterItem | None:
    """Get a specific filter by ID"""
    return self.filters.get(filterID)


  def clearAll(self) -> None:
    """Remove all filters"""
    self.filters.clear()
    self.modelChain = [self.baseModel]


  def setBaseModel(self, newBaseModel: QStandardItemModel) -> None:
    """Update the base model and rebuild chain"""
    self.baseModel = newBaseModel
    self.modelChain[0] = newBaseModel
    self.rebuildChain()


class FilterCommand(Enum):
  """ Commands used in this file """
  ADD_FILTER       = 1
  DELETE_FILTER    = 2
  SET_FILTER       = 3
