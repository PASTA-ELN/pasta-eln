#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_orm_upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_orm_upload_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any, Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseSqlAlchemyBase


class DatabaseOrmUploadModel(DatabaseSqlAlchemyBase):
  __tablename__ = "dataverse_upload"
  id = mapped_column(primary_key=True)
  data_type: Mapped[Optional[str]]
  project_name: Mapped[Optional[str]]
  project_doc_id: Mapped[Optional[str]]
  status: Mapped[Optional[str]]
  created_date_time: Mapped[Optional[str]]
  finished_date_time: Mapped[Optional[str]]
  log: Mapped[Optional[str]]
  dataverse_url: Mapped[Optional[str]]