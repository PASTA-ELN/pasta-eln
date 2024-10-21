#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_sqlalchemy_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: database_sqlalchemy_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: sqlalchemy_base.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.ext.declarative import declarative_base

class DatabaseSqlAlchemyBase(declarative_base):
  type_annotation_map = {
    dict[str, Any]: JSON
  }

