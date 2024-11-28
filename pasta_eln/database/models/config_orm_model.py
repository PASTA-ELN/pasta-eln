""" Represents the ORM model for the configuration table in the database. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: config_orm_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Any, Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.database.models.orm_model_base import OrmModelBase


class ConfigOrmModel(OrmModelBase):
  """Represents the ORM model for the configuration table in the database.

  This class defines the structure of the configuration model used in the application,
  including fields for project upload items, parallel uploads count, dataverse login
  information, and metadata. It provides a method to retrieve the names of the table
  columns for database operations.
  """
  __tablename__ = "config"
  id: Mapped[int] = mapped_column(primary_key=True)
  project_upload_items: Mapped[Optional[dict[str, Any]]]
  parallel_uploads_count: Mapped[Optional[int]]
  dataverse_login_info: Mapped[Optional[dict[str, Any]]]
  metadata_info: Mapped[Optional[dict[str, Any]]]

  @classmethod
  def get_table_columns(cls) -> list[str]:
    """Retrieves the list of column names for the configuration table.

    This method returns a list of strings representing the names of the columns
    defined in the configuration model. It is useful for database operations that
    require knowledge of the table structure.

    Returns:
        list[str]: A list of column names for the configuration table.
    """
    return ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"]
