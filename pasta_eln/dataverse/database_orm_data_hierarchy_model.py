from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase


class DatabaseOrmDataHierarchyModel(DatabaseModelBase):
  __tablename__ = "dataHierarchy"
  docType: Mapped[str] = mapped_column(primary_key=True)
  IRI: Mapped[Optional[str]]
  title: Mapped[Optional[str]]
  icon: Mapped[Optional[str]]
  shortcut: Mapped[Optional[str]]
  view: Mapped[Optional[str]]

  @classmethod
  def get_table_columns(cls) -> list[str]:
    return ["docType", "IRI", "title", "icon", "shortcut", "view"]
