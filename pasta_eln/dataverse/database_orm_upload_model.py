""" Represents the ORM model for the upload table in the database. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase


class DatabaseOrmUploadModel(DatabaseModelBase):
  """Represents the ORM model for the upload table in the database.

  This class defines the structure of the upload model used in the application,
  including fields for ID, data type, project name, project document ID, status,
  creation date, finished date, log, and dataverse URL. It provides a method to
  retrieve the names of the table columns for database operations.
  """
  __tablename__ = "upload"
  id: Mapped[int] = mapped_column(primary_key=True)
  data_type: Mapped[Optional[str]]
  project_name: Mapped[Optional[str]]
  project_doc_id: Mapped[Optional[str]]
  status: Mapped[Optional[str]]
  created_date_time: Mapped[Optional[str]]
  finished_date_time: Mapped[Optional[str]]
  log: Mapped[Optional[str]]
  dataverse_url: Mapped[Optional[str]]

  @classmethod
  def get_table_columns(cls) -> list[str]:
    """Retrieves the list of column names for the upload table.

    This method returns a list of strings representing the names of the columns
    defined in the upload model. It is useful for database operations that
    require knowledge of the table structure.

    Returns:
        list[str]: A list of column names for the upload table.
    """
    return ["id", "data_type", "project_name", "project_doc_id", "status", "created_date_time", "finished_date_time",
            "log", "dataverse_url"]
