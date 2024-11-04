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
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase


class DatabaseOrmUploadModel(DatabaseModelBase):
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

  def get_table_columns(self) -> list[str]:
    return ["id", "data_type", "project_name", "project_doc_id", "status", "created_date_time", "finished_date_time", "log", "dataverse_url"]
