""" Represents the ORM model for the data hierarchy table in the database. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_data_hierarchy_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_orm_data_hierarchy_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from pasta_eln.database.models.data_hierarchy_definition_orm_model import DataHierarchyDefinitionOrmModel
from pasta_eln.database.models.orm_model_base import OrmModelBase


class DataHierarchyOrmModel(OrmModelBase):
  """Represents the ORM model for the data hierarchy table in the database.

  This class defines the structure of the data hierarchy model used in the application,
  including fields for document type, IRI, title, icon, shortcut, and view. It provides
  a method to retrieve the names of the table columns for database operations.
  """
  __tablename__ = "dataHierarchy"
  doc_type: Mapped[str] = mapped_column("docType", primary_key=True)
  IRI: Mapped[Optional[str]]
  title: Mapped[Optional[str]]
  icon: Mapped[Optional[str]]
  shortcut: Mapped[Optional[str]]
  view: Mapped[Optional[str]]
  definitions = relationship(
    DataHierarchyDefinitionOrmModel,
    primaryjoin="DataHierarchyDefinitionOrmModel.doc_type==DataHierarchyOrmModel.doc_type",
    foreign_keys='DataHierarchyDefinitionOrmModel.doc_type'
  )

  @classmethod
  def get_table_columns(cls) -> list[str]:
    """Retrieves the list of column names for the data hierarchy table.

    This method returns a list of strings representing the names of the columns
    defined in the data hierarchy model. It is useful for database operations that
    require knowledge of the table structure.

    Returns:
        list[str]: A list of column names for the data hierarchy table.
    """
    return ["doc_type", "IRI", "title", "icon", "shortcut", "view", "definitions"]
