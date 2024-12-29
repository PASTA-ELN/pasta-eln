""" Represents the ORM model for the main project table in the database. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: main_orm_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.database.models.orm_model_base import OrmModelBase


class MainOrmModel(OrmModelBase):
  """Represents the ORM model for the main project table in the database.

  This class defines the structure of the main project model used in the application,
  including fields for ID, name, user, type, creation date, modification date, and comments.
  It provides a method to retrieve the names of the table columns for database operations.
  """
  __tablename__ = 'main'

  id: Mapped[str] = mapped_column(primary_key=True)
  name: Mapped[Optional[str]]
  user: Mapped[Optional[str]]
  type: Mapped[Optional[str]]
  date_created: Mapped[Optional[str]] = mapped_column('dateCreated')
  date_modified: Mapped[Optional[str]] = mapped_column('dateModified')
  comment: Mapped[Optional[str]]

  @classmethod
  def get_table_columns(cls) -> list[str]:
    """Retrieves the list of column names for the main project table.

    This method returns a list of strings representing the names of the columns
    defined in the main project model. It is useful for database operations that
    require knowledge of the table structure.

    Returns:
        list[str]: A list of column names for the main project table.
    """
    return ['id', 'name', 'user', 'type', 'date_created', 'date_modified', 'comment']
