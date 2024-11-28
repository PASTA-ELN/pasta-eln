""" Represents a model for data hierarchy definitions. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_hierarchy_definitions_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.database.models.base_model import BaseModel


class DataHierarchyDefinitionModel(BaseModel):
  """Represents a model for data hierarchy definitions.

  This class encapsulates the properties and behaviors associated with a data hierarchy
  definition, including its type, class, index, name, query, unit, IRI, mandatory status,
  and associated metadata. It ensures that all parameters are validated upon initialization.

  Args:
      doc_type (str | None): The document type of the model.
      doc_class (str | None): The class of the document.
      index (str | None): The index of the model.
      name (str | None): The name of the model.
      query (str | None): The query associated with the model.
      unit (str | None): The unit of measurement for the model.
      IRI (str | None): The Internationalized Resource Identifier for the model.
      mandatory (str | None): Indicates if the model is mandatory.
      meta_list (list[str] | None): A list of metadata associated with the model.

  Raises:
      IncorrectParameterError: If any of the provided parameters are of an unexpected type.
  """

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
    """Initializes a DataHierarchyDefinitionModel instance.

    This constructor sets up the properties of the DataHierarchyDefinitionModel,
    ensuring that all provided parameters are of the correct type. If any parameter
    is of an unexpected type, an IncorrectParameterError is raised.

    Args:
        doc_type (str | None): The document type of the model.
        doc_class (str | None): The class of the document.
        index (str | None): The index of the model.
        name (str | None): The name of the model.
        query (str | None): The query associated with the model.
        unit (str | None): The unit of measurement for the model.
        IRI (str | None): The Internationalized Resource Identifier for the model.
        mandatory (str | None): Indicates if the model is mandatory.
        meta_list (list[str] | None): A list of metadata associated with the model.

    Raises:
        IncorrectParameterError: If any of the provided parameters are of an unexpected type.
    """
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
    """Gets the document type of the data hierarchy definition model.

    This property retrieves the value of the document type, which indicates the
    specific type of the data hierarchy definition. It can return None if the
    document type has not been set.

    Returns:
        str | None: The document type of the model, or None if not set.
    """
    return self._doc_type

  @doc_type.setter
  def doc_type(self, value: str | None) -> None:
    """Sets the document type of the data hierarchy definition model.

    This setter method assigns a value to the document type property. It ensures
    that the provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (str | None): The document type to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._doc_type = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @doc_type.deleter
  def doc_type(self) -> None:
    """Deletes the document type of the data hierarchy definition model.

    This deleter method removes the value of the document type property, effectively
    resetting it to None. It allows for the document type to be cleared when no longer needed.
    """
    del self._doc_type

  @property
  def doc_class(self) -> str | None:
    """Gets the document class of the data hierarchy definition model.

    This property retrieves the value of the document class, which indicates the
    specific class of the data hierarchy definition. It can return None if the
    document class has not been set.

    Returns:
        str | None: The document class of the model, or None if not set.
    """
    return self._doc_class

  @doc_class.setter
  def doc_class(self, value: str | None) -> None:
    """Sets the document class of the data hierarchy definition model.

    This setter method assigns a value to the document class property. It ensures
    that the provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (str | None): The document class to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._doc_class = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @doc_class.deleter
  def doc_class(self) -> None:
    """Deletes the document class of the data hierarchy definition model.

    This deleter method removes the value of the document class property, effectively
    resetting it to None. It allows for the document class to be cleared when no longer needed.
    """
    del self._doc_class

  @property
  def index(self) -> str | None:
    """Gets the index of the data hierarchy definition model.

    This property retrieves the value of the index, which indicates the position
    of the data hierarchy definition within a collection. It can return None if the
    index has not been set.

    Returns:
        str | None: The index of the model, or None if not set.
    """
    return self._index

  @index.setter
  def index(self, value: str | None) -> None:
    """Sets the index of the data hierarchy definition model.

    This setter method assigns a value to the index property. It ensures that the
    provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (str | None): The index to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._index = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @index.deleter
  def index(self) -> None:
    """Deletes the index of the data hierarchy definition model.

    This deleter method removes the value of the index property, effectively
    resetting it to None. It allows for the index to be cleared when no longer needed.
    """
    del self._index

  @property
  def name(self) -> str | None:
    """Gets the name of the data hierarchy definition model.

    This property retrieves the value of the name, which represents the
    designation of the data hierarchy definition. It can return None if the
    name has not been set.

    Returns:
        str | None: The name of the model, or None if not set.
    """
    return self._name

  @name.setter
  def name(self, value: str | None) -> None:
    """Sets the name of the data hierarchy definition model.

    This setter method assigns a value to the name property. It ensures that the
    provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (str | None): The name to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._name = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @name.deleter
  def name(self) -> None:
    """Deletes the name of the data hierarchy definition model.

    This deleter method removes the value of the name property, effectively
    resetting it to None. It allows for the name to be cleared when no longer needed.
    """
    del self._name

  @property
  def query(self) -> str | None:
    """Gets the query associated with the data hierarchy definition model.

    This property retrieves the value of the query, which represents the query
    string related to the data hierarchy definition. It can return None if the
    query has not been set.

    Returns:
        str | None: The query of the model, or None if not set.
    """
    return self._query

  @query.setter
  def query(self, value: str | None) -> None:
    """Sets the query associated with the data hierarchy definition model.

    This setter method assigns a value to the query property. It ensures that the
    provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (str | None): The query to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._query = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @query.deleter
  def query(self) -> None:
    """Deletes the query associated with the data hierarchy definition model.

    This deleter method removes the value of the query property, effectively
    resetting it to None. It allows for the query to be cleared when no longer needed.
    """
    del self._query

  @property
  def unit(self) -> str | None:
    """Gets the unit of measurement for the data hierarchy definition model.

    This property retrieves the value of the unit, which indicates the measurement
    unit associated with the data hierarchy definition. It can return None if the
    unit has not been set.

    Returns:
        str | None: The unit of the model, or None if not set.
    """
    return self._unit

  @unit.setter
  def unit(self, value: str | None) -> None:
    """Sets the unit of measurement for the data hierarchy definition model.

    This setter method assigns a value to the unit property. It ensures that the
    provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (str | None): The unit to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._unit = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @unit.deleter
  def unit(self) -> None:
    """Deletes the unit of measurement for the data hierarchy definition model.

    This deleter method removes the value of the unit property, effectively
    resetting it to None. It allows for the unit to be cleared when no longer needed.
    """
    del self._unit

  @property
  def IRI(self) -> str | None:
    """Gets the Internationalized Resource Identifier (IRI) of the data hierarchy definition model.

    This property retrieves the value of the IRI, which uniquely identifies the data
    hierarchy definition in a global context. It can return None if the IRI has not
    been set.

    Returns:
        str | None: The IRI of the model, or None if not set.
    """
    return self._IRI

  @IRI.setter
  def IRI(self, value: str | None) -> None:
    """Sets the Internationalized Resource Identifier (IRI) for the data hierarchy definition model.

    This setter method assigns a value to the IRI property. It ensures that the provided
    value is of the correct type; if not, an IncorrectParameterError is raised.

    Args:
        value (str | None): The IRI to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._IRI = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @IRI.deleter
  def IRI(self) -> None:
    """Deletes the Internationalized Resource Identifier (IRI) of the data hierarchy definition model.

    This deleter method removes the value of the IRI property, effectively resetting it
    to None. It allows for the IRI to be cleared when it is no longer needed.
    """
    del self._IRI

  @property
  def mandatory(self) -> str | None:
    """Gets the mandatory status of the data hierarchy definition model.

    This property retrieves the value indicating whether the data hierarchy definition
    is mandatory. It can return None if the mandatory status has not been set.

    Returns:
        str | None: The mandatory status of the model, or None if not set.
    """
    return self._mandatory

  @mandatory.setter
  def mandatory(self, value: str | None) -> None:
    """Sets the mandatory status of the data hierarchy definition model.

    This setter method assigns a value to the mandatory property. It ensures that the
    provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (str | None): The mandatory status to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a string or None.
    """
    if isinstance(value, dict | None):
      self._mandatory = value
    else:
      raise IncorrectParameterError(f"Expected string type for upload_items but got {type(value)}")

  @mandatory.deleter
  def mandatory(self) -> None:
    """Deletes the mandatory status of the data hierarchy definition model.

    This deleter method removes the value of the mandatory property, effectively
    resetting it to None. It allows for the mandatory status to be cleared when
    it is no longer needed.
    """
    del self._mandatory

  @property
  def meta_list(self) -> list[str] | None:
    """Gets the list of metadata associated with the data hierarchy definition model.

    This property retrieves the value of the meta_list, which contains additional
    information related to the data hierarchy definition. It can return None if the
    meta_list has not been set.

    Returns:
        list[str] | None: The list of metadata for the model, or None if not set.
    """
    return self._meta_list

  @meta_list.setter
  def meta_list(self, value: list[str] | None) -> None:
    """Sets the list of metadata associated with the data hierarchy definition model.

    This setter method assigns a value to the meta_list property. It ensures that the
    provided value is of the correct type; if not, an IncorrectParameterError
    is raised.

    Args:
        value (list[str] | None): The list of metadata to set for the model.

    Raises:
        IncorrectParameterError: If the provided value is not a list or None.
    """
    if isinstance(value, list | None):
      self._meta_list = value
    else:
      raise IncorrectParameterError(f"Expected list type for meta_list but got {type(value)}")

  @meta_list.deleter
  def meta_list(self) -> None:
    """Deletes the list of metadata associated with the data hierarchy definition model.

    This deleter method removes the value of the meta_list property, effectively
    resetting it to None. It allows for the metadata list to be cleared when it is
    no longer needed.
    """
    del self._meta_list

  def __repr__(self) -> str:
    """Returns a string representation of the data hierarchy definition model.

    This method provides a detailed string representation of the model's attributes,
    which is useful for debugging and logging purposes. It includes all relevant
    properties of the model in a formatted manner.

    Returns:
        str: A string representation of the data hierarchy definition model.
    """
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
