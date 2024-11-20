#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_sqlalchemy_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Any, Generator

from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase


class DatabaseModelBase(DeclarativeBase):
  type_annotation_map = {
    dict[str, Any]: JSON
  }

  def __iter__(self) -> Generator[tuple[str, Any], None, None]:
    """
    Iterates over the attributes of the object and yields key-value pairs.

    Yields:
        tuple[str, Any]: A tuple containing the attribute name and its corresponding value.

    """
    for key in self.get_table_columns():
      yield key, getattr(self, key)

  @classmethod
  def get_table_columns(cls) -> list[str]:
    return []
