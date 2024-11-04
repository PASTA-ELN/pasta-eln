#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_project_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_orm_project_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_orm_project_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase


class DatabaseOrmPropertiesModel(DatabaseModelBase):
  """ Represents a project model object. """

  __tablename__ = "properties"

  id: Mapped[str] = mapped_column(primary_key=True)
  key: Mapped[str] = mapped_column(primary_key=True)
  value: Mapped[Optional[str]]
  unit: Mapped[Optional[str]]

  def get_table_columns(self) -> list[str]:
    return ["id", "key", "value", "unit"]