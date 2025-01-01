""" Represents data hierarchy document adapter. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_hierarchy_document_adapter.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import itertools
from typing import Any
from pasta_eln.database.models.data_hierarchy_definition_model import DataHierarchyDefinitionModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel


class DataHierarchyDocumentAdapter:
  """A class for converting between DataHierarchyModel instances and their dictionary representations.

  This class provides methods to transform DataHierarchyModel instances into a structured
  dictionary format suitable for data hierarchy documents, and vice versa. It ensures that
  the data is organized and accessible for further processing.
  """

  @classmethod
  def to_data_hierarchy_document(cls, data: DataHierarchyModel) -> dict[str, Any]:
    """Converts a DataHierarchyModel instance into a dictionary representation.

    This method checks if the provided data model is valid and constructs a dictionary
    that represents the data hierarchy document. It organizes the model's definitions
    into a structured format, allowing for easy access to its properties.

    Args:
        data (DataHierarchyModel): The DataHierarchyModel instance to convert.

    Returns:
        dict[str, Any]: A dictionary representation of the data hierarchy document,
        or an empty dictionary if the data is invalid.

    Raises:
        None: This method does not raise exceptions but returns an empty dictionary
        for invalid input.
    """
    if data is None or data.doc_type is None:
      return {}
    meta = {}
    if data.definitions:
      meta = {
        meta_class or 'default': [
          {
            'name': item.name,
            'query': item.query,
            'mandatory': item.mandatory == 'T',
            'unit': item.unit,
            'IRI': item.IRI,
            'list': item.meta_list
          } for item in list(group)] for meta_class, group in itertools.groupby(data.definitions, lambda x: x.doc_class)
      }
    return {
      data.doc_type: {
        'IRI': data.IRI,
        'attachments': [],
        'title': data.title,
        'icon': data.icon,
        'shortcut': data.shortcut,
        'view': data.view,
        'meta': meta,
      }
    }

  @classmethod
  def to_data_hierarchy_model_list(cls, data: dict[str, Any]) -> list[DataHierarchyModel]:
    """Converts a dictionary representation of data hierarchy into a list of DataHierarchyModel instances.

    This method processes the provided data dictionary, extracting relevant information
    to create DataHierarchyModel instances. It handles the conversion of definitions into
    DataHierarchyDefinitionModel instances and organizes them accordingly.

    Args:
        data (dict[str, Any]): A dictionary containing data hierarchy information.

    Returns:
        list[DataHierarchyModel]: A list of DataHierarchyModel instances created from the provided data.

    Raises:
        None: This method does not raise exceptions but returns an empty list for invalid input.
    """
    if not data:
      return []
    items: list[DataHierarchyModel] = []
    for key, value in data.items():
      definitions: list[DataHierarchyDefinitionModel] = []
      for meta_key, meta_value in value.get('meta', {}).items():
        definitions.extend(
          DataHierarchyDefinitionModel(
            doc_type=key,
            doc_class='' if meta_key == 'default' else meta_key,
            index=str(item_index),
            name=item.get('name', None),
            query=item.get('query', None),
            mandatory='T' if item.get('mandatory', False) else 'F',
            unit=item.get('unit'),
            meta_list=item.get('list', []),
            IRI=item.get('IRI'),
          ) for item_index, item in enumerate(meta_value))
      items.append(
        DataHierarchyModel(
          doc_type=key,
          IRI=value.get('IRI', None),
          title=value.get('title', None),
          icon=value.get('icon', None),
          shortcut=value.get('shortcut', None),
          view=value.get('view', None),
          definitions=definitions
        ))
    return items
