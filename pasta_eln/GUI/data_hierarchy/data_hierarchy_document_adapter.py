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
  @classmethod
  def to_data_hierarchy_document(cls, data: DataHierarchyModel) -> dict[str, Any]:
    if data is None or data.doc_type is None:
      return {}
    meta = {}
    if data.definitions:
      meta = {
        meta_class if meta_class else 'default': [
          {
            "name": item.name,
            "query": item.query,
            "mandatory": item.mandatory == 'T',
            "unit": item.unit,
            "IRI": item.IRI,
            "list": item.meta_list
          } for item in list(group)] for meta_class, group in itertools.groupby(data.definitions, lambda x: x.doc_class)
      }
    return {
      data.doc_type: {
        "IRI": data.IRI,
        "attachments": [],
        "title": data.title,
        "icon": data.icon,
        "shortcut": data.shortcut,
        "view": data.view,
        "meta": meta,
      }
    }

  @classmethod
  def to_data_hierarchy_model_list(cls, data: dict[str, Any]) -> list[DataHierarchyModel] | None:
    if not data:
      return None
    items: list[DataHierarchyModel] = []
    for key, value in data.items():
      definitions = []
      for meta_key, meta_value in value.get("meta", {}).items():
        item_index = 0
        for item in meta_value:
          definitions.append(DataHierarchyDefinitionModel(
            doc_type=key,
            doc_class="" if meta_key == "default" else meta_key,
            index=str(item_index),
            name=item.get("name", None),
            query=item.get("query", None),
            mandatory='T' if item.get("mandatory", False) else 'F',
            unit=item.get("unit"),
            meta_list=item.get("list", []),
            IRI=item.get("IRI"),
          ))
          item_index += 1
      items.append(
        DataHierarchyModel(
          doc_type=key,
          IRI=value.get("IRI", None),
          title=value.get("title", None),
          icon=value.get("icon", None),
          shortcut=value.get("shortcut", None),
          view=value.get("view", None),
          definitions=definitions
        ))
    return items
