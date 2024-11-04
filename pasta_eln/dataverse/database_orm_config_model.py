#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from typing import Any, Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase


class DatabaseOrmConfigModel(DatabaseModelBase):
  __tablename__ = "config"
  id: Mapped[int] = mapped_column(primary_key=True)
  project_upload_items: Mapped[Optional[dict[str, Any]]]
  parallel_uploads_count: Mapped[Optional[int]]
  dataverse_login_info: Mapped[Optional[dict[str, Any]]]
  metadata_info: Mapped[Optional[dict[str, Any]]]

  def get_table_columns(self) -> list[str]:
    return ["id", "project_upload_items", "parallel_uploads_count", "dataverse_login_info", "metadata_info"]
