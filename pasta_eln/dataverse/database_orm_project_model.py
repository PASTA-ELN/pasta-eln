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

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseSqlAlchemyBase


class DatabaseOrmProjectModel(DatabaseSqlAlchemyBase):
  """ Represents a project model object. """

  __tablename__ = "dataverse_project"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[Optional[str]]
  comment: Mapped[Optional[str]]
  user: Mapped[Optional[str]]
  user: Mapped[Optional[str]]
  date: Mapped[Optional[str]]
  status: Mapped[Optional[str]]
  objective: Mapped[Optional[str]]