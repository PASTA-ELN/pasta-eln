""" Represents a data hierarchy model. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_hierarchy_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.database.models.base_model import BaseModel
from pasta_eln.database.models.data_hierarchy_definition_model import DataHierarchyDefinitionModel


class DataHierarchyModel(BaseModel):
  """Represents a data hierarchy model with various attributes.

  This class is used to define a data hierarchy model that includes properties
  such as document type, IRI, title, icon, shortcut, and view. It ensures that
  the values assigned to these properties are of the correct type and raises
  errors if invalid types are provided.

  Args:
      doc_type (str | None): The type of document.
      IRI (str | None): The Internationalized Resource Identifier.
      title (str | None): The title of the model.
      icon (str | None): The icon associated with the model.
      shortcut (str | None): A shortcut key for the model.
      view (str | None): The view associated with the model.
      definitions (list[DataHierarchyDefinitionModel] | None): A list of data hierarchy definitions.

  Raises:
      IncorrectParameterError: If any of the parameters are not of the expected type.
  """

  def __init__(self,
               doc_type: str | None = None,
               IRI: str | None = None,
               title: str | None = None,
               icon: str | None = None,
               shortcut: str | None = None,
               view: str | None = None,
               definitions: list[DataHierarchyDefinitionModel] | None = []):
    super().__init__(None)
    if isinstance(doc_type, str | None):
      self._doc_type: str | None = doc_type
    else:
      raise IncorrectParameterError(f"Expected string type for doc_type but got {type(doc_type)}")
    if isinstance(IRI, str | None):
      self._IRI: str | None = IRI
    else:
      raise IncorrectParameterError(f"Expected string type for IRI but got {type(IRI)}")
    if isinstance(title, str | None):
      self._title: str | None = title
    else:
      raise IncorrectParameterError(f"Expected string type for title but got {type(title)}")
    if isinstance(icon, str | None):
      self._icon: str | None = icon
    else:
      raise IncorrectParameterError(f"Expected string type for icon but got {type(icon)}")
    if isinstance(shortcut, str | None):
      self._shortcut: str | None = shortcut
    else:
      raise IncorrectParameterError(f"Expected string type for shortcut but got {type(shortcut)}")
    if isinstance(view, str | None):
      self._view: str | None = view
    else:
      raise IncorrectParameterError(f"Expected string type for view but got {type(view)}")
    if isinstance(definitions, list | None):
      self._definitions: list[DataHierarchyDefinitionModel] | None = definitions
    else:
      raise IncorrectParameterError(f"Expected list type for definitions but got {type(definitions)}")

  @property
  def doc_type(self) -> str | None:
    """Gets the document type of the data hierarchy model.

    This property retrieves the current document type associated with the
    data hierarchy model. It returns the document type as a string or
    None if it has not been set.

    Returns:
        str | None: The document type of the model, or None if not set.
    """
    return self._doc_type

  @doc_type.setter
  def doc_type(self, value: str | None) -> None:
    """Sets the document type of the data hierarchy model.

    This setter allows the assignment of a document type to the data hierarchy model.
    It ensures that the value being set is either a string or None, raising an error
    if the value is of an incorrect type.

    Args:
        value (str | None): The document type to set for the model.

    Raises:
        IncorrectParameterError: If the value is not a string or None.
    """
    if isinstance(value, str | None):
      self._doc_type = value
    else:
      raise IncorrectParameterError(f"Expected string type for doc_type but got {type(value)}")

  @doc_type.deleter
  def doc_type(self) -> None:
    """Deletes the document type of the data hierarchy model.

    This deleter removes the current document type from the data hierarchy model,
    effectively setting it to None. It allows for the clearing of the document type
    when it is no longer needed.

    Raises:
        AttributeError: If the document type has already been deleted.
    """
    del self._doc_type

  @property
  def IRI(self) -> str | None:
    """Gets the Internationalized Resource Identifier (IRI) of the data hierarchy model.

    This property retrieves the current IRI associated with the data hierarchy model.
    It returns the IRI as a string or None if it has not been set.

    Returns:
        str | None: The IRI of the model, or None if not set.
    """
    return self._IRI

  @IRI.setter
  def IRI(self, value: str | None) -> None:
    """Sets the Internationalized Resource Identifier (IRI) of the data hierarchy model.

    This setter allows the assignment of an IRI to the data hierarchy model.
    It ensures that the value being set is either a string or None, raising an error
    if the value is of an incorrect type.

    Args:
        value (str | None): The IRI to set for the model.

    Raises:
        IncorrectParameterError: If the value is not a string or None.
    """
    if isinstance(value, str | None):
      self._IRI = value
    else:
      raise IncorrectParameterError(f"Expected string type for iri but got {type(value)}")

  @IRI.deleter
  def IRI(self) -> None:
    """Deletes the Internationalized Resource Identifier (IRI) of the data hierarchy model.

    This deleter removes the current IRI associated with the data hierarchy model,
    effectively setting it to None. It allows for the clearing of the IRI when it
    is no longer needed.

    Raises:
        AttributeError: If the IRI has already been deleted.
    """
    del self._IRI

  @property
  def title(self) -> str | None:
    """Gets the title of the data hierarchy model.

    This property retrieves the current title associated with the data hierarchy model.
    It returns the title as a string or None if it has not been set.

    Returns:
        str | None: The title of the model, or None if not set.
    """
    return self._title

  @title.setter
  def title(self, value: str | None) -> None:
    """Sets the title of the data hierarchy model.

    This setter allows the assignment of a title to the data hierarchy model.
    It ensures that the value being set is either a string or None, raising an error
    if the value is of an incorrect type.

    Args:
        value (str | None): The title to set for the model.

    Raises:
        IncorrectParameterError: If the value is not a string or None.
    """
    if isinstance(value, str | None):
      self._title = value
    else:
      raise IncorrectParameterError(f"Expected string type for title but got {type(value)}")

  @title.deleter
  def title(self) -> None:
    """Deletes the title of the data hierarchy model.

    This deleter removes the current title associated with the data hierarchy model,
    effectively setting it to None. It allows for the clearing of the title when it
    is no longer needed.

    Raises:
        AttributeError: If the title has already been deleted.
    """
    del self._title

  @property
  def icon(self) -> str | None:
    """Gets the icon of the data hierarchy model.

    This property retrieves the current icon associated with the data hierarchy model.
    It returns the icon as a string or None if it has not been set.

    Returns:
        str | None: The icon of the model, or None if not set.
    """
    return self._icon

  @icon.setter
  def icon(self, value: str | None) -> None:
    """Sets the icon of the data hierarchy model.

    This setter allows the assignment of an icon to the data hierarchy model.
    It ensures that the value being set is either a string or None, raising an error
    if the value is of an incorrect type.

    Args:
        value (str | None): The icon to set for the model.

    Raises:
        IncorrectParameterError: If the value is not a string or None.
    """
    if isinstance(value, str | None):
      self._icon = value
    else:
      raise IncorrectParameterError(f"Expected string type for icon but got {type(value)}")

  @icon.deleter
  def icon(self) -> None:
    """Deletes the icon of the data hierarchy model.

    This deleter removes the current icon associated with the data hierarchy model,
    effectively setting it to None. It allows for the clearing of the icon when it
    is no longer needed.

    Raises:
        AttributeError: If the icon has already been deleted.
    """
    del self._icon

  @property
  def shortcut(self) -> str | None:
    """Gets the shortcut of the data hierarchy model.

    This property retrieves the current shortcut associated with the data hierarchy model.
    It returns the shortcut as a string or None if it has not been set.

    Returns:
        str | None: The shortcut of the model, or None if not set.
    """
    return self._shortcut

  @shortcut.setter
  def shortcut(self, value: str | None) -> None:
    """Sets the shortcut of the data hierarchy model.

    This setter allows the assignment of a shortcut to the data hierarchy model.
    It ensures that the value being set is either a string or None, raising an error
    if the value is of an incorrect type.

    Args:
        value (str | None): The shortcut to set for the model.

    Raises:
        IncorrectParameterError: If the value is not a string or None.
    """
    if isinstance(value, str | None):
      self._shortcut = value
    else:
      raise IncorrectParameterError(f"Expected string type for shortcut but got {type(value)}")

  @shortcut.deleter
  def shortcut(self) -> None:
    """Deletes the shortcut of the data hierarchy model.

    This deleter removes the current shortcut associated with the data hierarchy model,
    effectively setting it to None. It allows for the clearing of the shortcut when it
    is no longer needed.

    Raises:
        AttributeError: If the shortcut has already been deleted.
    """
    del self._shortcut

  @property
  def view(self) -> str | None:
    """Gets the view of the data hierarchy model.

        This property retrieves the current view associated with the data hierarchy model.
        It returns the view as a string or None if it has not been set.

        Returns:
            str | None: The view of the model, or None if not set.
        """
    return self._view

  @view.setter
  def view(self, value: str | None) -> None:
    """Sets the view of the data hierarchy model.

    This setter allows the assignment of a view to the data hierarchy model.
    It ensures that the value being set is either a string or None, raising an error
    if the value is of an incorrect type.

    Args:
        value (str | None): The view to set for the model.

    Raises:
        IncorrectParameterError: If the value is not a string or None.
    """
    if isinstance(value, str | None):
      self._view = value
    else:
      raise IncorrectParameterError(f"Expected string type for view but got {type(value)}")

  @view.deleter
  def view(self) -> None:
    """Deletes the view of the data hierarchy model.

    This deleter removes the current view associated with the data hierarchy model,
    effectively setting it to None. It allows for the clearing of the view when it
    is no longer needed.

    Raises:
        AttributeError: If the view has already been deleted.
    """
    del self._view

  @property
  def definitions(self) -> list[DataHierarchyDefinitionModel] | None:
    """Gets the definitions of the data hierarchy model.

    This property retrieves the current definitions associated with the data hierarchy model.
    It returns the definitions as a list of DataHierarchyDefinitionsModel objects or None
    if it has not been set.

    Returns:
        list[DataHierarchyDefinitionModel] | None: The definitions of the model, or None if not set.
    """
    return self._definitions

  @definitions.setter
  def definitions(self, value: list[DataHierarchyDefinitionModel] | None) -> None:
    """Sets the definitions of the data hierarchy model.

    This setter allows the assignment of a list of definitions to the data hierarchy model.
    It ensures that the value being set is either a list of DataHierarchyDefinitionsModel
    objects or None, raising an error if the value is of an incorrect type.

    Args:
        value (list[DataHierarchyDefinitionModel] | None): The definitions to set for the model.

    Raises:
        IncorrectParameterError: If the value is not a list of DataHierarchyDefinitionsModel objects or None.
    """
    if isinstance(value, list | None):
      self._definitions = value
    else:
      raise IncorrectParameterError(f"Expected list type for definitions but got {type(value)}")

  @definitions.deleter
  def definitions(self) -> None:
    """Deletes the definitions of the data hierarchy model.

    This deleter removes the current definitions associated with the data hierarchy model,
    effectively setting it to None. It allows for the clearing of the definitions when it
    is no longer needed.

    Raises:
        AttributeError: If the definitions have already been deleted.
    """
    del self._definitions

  def __repr__(self) -> str:
    return (f"{self.__class__.__name__}"
            f"(doc_type={self.doc_type}, "
            f"IRI={self.IRI}, "
            f"title={self.title}, "
            f"icon={self.icon}, "
            f"shortcut={self.shortcut}, "
            f"view={self.view}, "
            f"definitions={self.definitions})")
