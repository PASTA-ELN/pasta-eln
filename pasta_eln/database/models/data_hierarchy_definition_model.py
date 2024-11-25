#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_hierarchy_definitions_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from pasta_eln.database.models.base_model import BaseModel
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class DataHierarchyDefinitionModel(BaseModel):
  def __init__(self,
               doc_type: str | None = None,
               doc_class: str | None = None,
               index: str | None = None,
               name: str | None = None,
               query: str | None = None,
               unit: str | None = None,
               IRI: str | None = None,
               mandatory: str | None = None,
               meta_list: list[str] | None = None,
               ):
    super().__init__(None)
    if isinstance(doc_type, str | None):
      self._doc_type: str | None = doc_type
    else:
      raise IncorrectParameterError(f"Expected string type for doc_type but got {type(doc_type)}")
    if isinstance(doc_class, str | None):
      self._doc_class: str | None = doc_class
    else:
      raise IncorrectParameterError(f"Expected string type for doc_class but got {type(doc_class)}")
    if isinstance(index, str | None):
      self._index: str | None = index
    else:
      raise IncorrectParameterError(f"Expected string type for index but got {type(index)}")
    if isinstance(name, str | None):
      self._name: str | None = name
    else:
      raise IncorrectParameterError(f"Expected string type for name but got {type(name)}")
    if isinstance(query, str | None):
      self._query: str | None = query
    else:
      raise IncorrectParameterError(f"Expected string type for query but got {type(query)}")
    if isinstance(unit, str | None):
      self._unit: str | None = unit
    else:
      raise IncorrectParameterError(f"Expected string type for unit but got {type(unit)}")
    if isinstance(IRI, str | None):
      self._IRI: str | None = IRI
    else:
      raise IncorrectParameterError(f"Expected string type for IRI but got {type(IRI)}")
    if isinstance(mandatory, str | None):
      self._mandatory: str | None = mandatory
    else:
      raise IncorrectParameterError(f"Expected string type for mandatory but got {type(mandatory)}")
    if isinstance(meta_list, list | None):
      self._meta_list: list[str] | None = meta_list
    else:
      raise IncorrectParameterError(f"Expected list type for meta_list but got {type(meta_list)}")

  @property
  def doc_type(self) -> str | None:
    return self._doc_type

  @doc_type.setter
  def doc_type(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._doc_type = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @doc_type.deleter
  def doc_type(self) -> None:
    del self._doc_type

  @property
  def doc_class(self) -> str | None:
    return self._doc_class

  @doc_class.setter
  def doc_class(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._doc_class = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @doc_class.deleter
  def doc_class(self) -> None:
    del self._doc_class

  @property
  def index(self) -> str | None:
    return self._index

  @index.setter
  def index(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._index = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @index.deleter
  def index(self) -> None:
    del self._index

  @property
  def name(self) -> str | None:
    return self._name

  @name.setter
  def name(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._name = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @name.deleter
  def name(self) -> None:
    del self._name

  @property
  def query(self) -> str | None:
    return self._query

  @query.setter
  def query(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._query = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @query.deleter
  def query(self) -> None:
    del self._query

  @property
  def unit(self) -> str | None:
    return self._unit

  @unit.setter
  def unit(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._unit = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @unit.deleter
  def unit(self) -> None:
    del self._unit

  @property
  def IRI(self) -> str | None:
    return self._IRI

  @IRI.setter
  def IRI(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._IRI = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @IRI.deleter
  def IRI(self) -> None:
    del self._IRI

  @property
  def mandatory(self) -> str | None:
    return self._mandatory

  @mandatory.setter
  def mandatory(self, value: str | None) -> None:
    if isinstance(value, dict | None):
      self._mandatory = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @mandatory.deleter
  def mandatory(self) -> None:
    del self._mandatory

  @property
  def meta_list(self) -> list[str] | None:
    return self._meta_list

  @meta_list.setter
  def meta_list(self, value: list[str] | None) -> None:
    if isinstance(value, list | None):
      self._meta_list = value
    else:
      raise IncorrectParameterError(f"Expected list type for meta_list but got {type(value)}")

  @meta_list.deleter
  def meta_list(self) -> None:
    del self._meta_list

  def __repr__(self) -> str:
    return (
      f"{self.__class__.__name__}("
      f"doc_type={self.doc_type}, "
      f"doc_class={self.doc_class}, "
      f"index={self.index}, "
      f"name={self.name}, "
      f"query={self.query}, "
      f"unit={self.unit}, "
      f"IRI={self.IRI}, "
      f"mandatory={self.mandatory}, "
      f"meta_list={self.meta_list}"
      f")"
    )
