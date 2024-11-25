""" Represents the ORM model for the data hierarchy table in the database. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_hierarchy_definition_orm_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.database.models.orm_model_base import OrmModelBase


class DataHierarchyDefinitionOrmModel(OrmModelBase):
  __tablename__ = "definitions"
  doc_type: Mapped[str] = mapped_column("docType", primary_key=True)
  doc_class: Mapped[Optional[str]] = mapped_column("class", primary_key=True)
  index: Mapped[Optional[str]] = mapped_column("idx", primary_key=True)
  name: Mapped[Optional[str]]
  query: Mapped[Optional[str]]
  unit: Mapped[Optional[str]]
  IRI: Mapped[Optional[str]]
  mandatory: Mapped[Optional[str]]
  meta_list: Mapped[Optional[str]] = mapped_column("list")

  @classmethod
  def get_table_columns(cls) -> list[str]:
    return [
      "doc_type",
      "doc_class",
      "index",
      "name",
      "query",
      "unit",
      "IRI",
      "mandatory",
      "meta_list"
    ]
