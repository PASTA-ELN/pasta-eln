""" Base class for all database ORM models in the application. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: orm_model_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Any, Generator

from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase


class OrmModelBase(DeclarativeBase):
  """Base class for all ORM based database models in the application.

  This class provides a foundation for ORM models, including methods for
  iterating over model attributes and retrieving table column names. It also
  defines a mapping for type annotations used in the database.
  """
  # Mapping for type annotations
  type_annotation_map = {
    dict[str, Any]: JSON
  }

  def __iter__(self) -> Generator[tuple[str, Any], None, None]:
    """Iterates over the model's attributes.

    This method yields key-value pairs for each attribute defined in the
    model's table columns, allowing for easy iteration over model data.

    Returns:
        Generator[tuple[str, Any], None, None]: A generator yielding tuples
        of attribute names and their corresponding values.
    """
    for key in self.get_table_columns():
      yield key, getattr(self, key)

  @classmethod
  def get_table_columns(cls) -> list[str]:
    """Retrieves the list of column names for the model.

     This method returns a list of strings representing the names of the columns
     defined in the model. It is intended to be overridden by subclasses to
     provide specific column names.

     Returns:
         list[str]: A list of column names for the model.
     """
    return []
