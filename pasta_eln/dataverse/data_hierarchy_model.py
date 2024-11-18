from pasta_eln.dataverse.base_model import BaseModel
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class DataHierarchyModel(BaseModel):
  def __init__(self, docType: str | None = None, IRI: str | None = None, title: str | None = None,
               icon: str | None = None, shortcut: str | None = None, view: str | None = None):
    super().__init__(None)
    if isinstance(docType, str | None):
      self._docType: str | None = docType
    else:
      raise IncorrectParameterError(f"Expected string type for docType but got {type(docType)}")
    if isinstance(IRI, str | None):
      self._iri: str | None = IRI
    else:
      raise IncorrectParameterError(f"Expected string type for IRI but got {type(IRI)}")
    if isinstance(title, str | None):
      self._title: str | None = title
    else:
      raise IncorrectParameterError(f"Expected string type for title but got {type(title)}")
    if isinstance(icon, str | None):
      self._icon: str | None = title
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

  @property
  def docType(self) -> str | None:
    return self._docType

  @docType.setter
  def docType(self, value: str | None) -> None:
    if isinstance(value, str | None):
      self._docType = value
    else:
      raise IncorrectParameterError(f"Expected string type for docType but got {type(value)}")

  @docType.deleter
  def docType(self) -> None:
    del self._docType

  @property
  def iri(self) -> str | None:
    return self._iri

  @iri.setter
  def iri(self, value: str | None) -> None:
    if isinstance(value, str | None):
      self._iri = value
    else:
      raise IncorrectParameterError(f"Expected string type for iri but got {type(value)}")

  @iri.deleter
  def iri(self) -> None:
    del self._iri

  @property
  def title(self) -> str | None:
    return self._title

  @title.setter
  def title(self, value: str | None) -> None:
    if isinstance(value, str | None):
      self._title = value
    else:
      raise IncorrectParameterError(f"Expected string type for title but got {type(value)}")

  @title.deleter
  def title(self) -> None:
    del self._title

  @property
  def icon(self) -> str | None:
    return self._icon

  @icon.setter
  def icon(self, value: str | None) -> None:
    if isinstance(value, str | None):
      self._icon = value
    else:
      raise IncorrectParameterError(f"Expected string type for icon but got {type(value)}")

  @icon.deleter
  def icon(self) -> None:
    del self._icon

  @property
  def shortcut(self) -> str | None:
    return self._shortcut

  @shortcut.setter
  def shortcut(self, value: str | None) -> None:
    if isinstance(value, str | None):
      self._shortcut = value
    else:
      raise IncorrectParameterError(f"Expected string type for shortcut but got {type(value)}")

  @shortcut.deleter
  def shortcut(self) -> None:
    del self._shortcut

  @property
  def view(self) -> str | None:
    return self._view

  @view.setter
  def view(self, value: str | None) -> None:
    if isinstance(value, str | None):
      self._view = value
    else:
      raise IncorrectParameterError(f"Expected string type for view but got {type(value)}")

  @view.deleter
  def view(self) -> None:
    del self._view
