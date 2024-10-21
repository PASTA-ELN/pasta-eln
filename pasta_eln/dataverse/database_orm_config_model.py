#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_orm_config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_orm_config_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_config_model_orm.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any, Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseSqlAlchemyBase


class DatabaseOrmConfigModel(DatabaseSqlAlchemyBase):
  __tablename__ = "dataverse_config"
  id = mapped_column(primary_key=True)
  project_upload_items: Mapped[Optional[dict[str, Any]]]
  parallel_uploads_count: Mapped[Optional[int]]
  dataverse_login_info: Mapped[Optional[dict[str, Any]]]
  metadata_info: Mapped[Optional[dict[str, Any]]]
