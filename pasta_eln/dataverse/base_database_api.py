""" Provides an interface to interact with a database. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: base_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from collections.abc import Callable
from enum import Enum
from typing import Type, Union

from sqlalchemy import create_engine, or_, select
from sqlalchemy.orm import Session

from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.data_hierarchy_model import DataHierarchyModel
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.database_orm_adapter import DatabaseOrmAdapter
from pasta_eln.dataverse.database_orm_config_model import DatabaseOrmConfigModel
from pasta_eln.dataverse.database_orm_data_hierarchy_model import DatabaseOrmDataHierarchyModel
from pasta_eln.dataverse.database_orm_main_model import DatabaseOrmMainModel
from pasta_eln.dataverse.database_orm_properties_model import DatabaseOrmPropertiesModel
from pasta_eln.dataverse.database_orm_upload_model import DatabaseOrmUploadModel
from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.utils import generate_project_join_statement, log_and_create_error


class DatabaseNames(Enum):
  DataverseDatabase = 1
  PastaProjectGroupDatabase = 2


class BaseDatabaseApi:
  def __init__(self,
               dataverse_db_path: str,
               pasta_project_group_db_path: str) -> None:
    self.logger = logging.getLogger('sqlalchemy.engine')
    self.logger.setLevel(logging.INFO)
    self.db_url_map: dict[DatabaseNames, str] = {}
    base_model_type = Type[UploadModel | ConfigModel | ProjectModel | DataHierarchyModel]
    orm_model_type = Type[DatabaseOrmUploadModel | DatabaseOrmConfigModel | DatabaseOrmDataHierarchyModel]
    self.model_mapping: dict[base_model_type, orm_model_type] = {
      UploadModel: DatabaseOrmUploadModel,
      ConfigModel: DatabaseOrmConfigModel,
      DataHierarchyModel: DatabaseOrmDataHierarchyModel
    }
    self.to_orm_converter_map: dict[base_model_type,
    Callable[Type[UploadModel | ConfigModel | ProjectModel | DataHierarchyModel], Type[
      DatabaseOrmUploadModel | DatabaseOrmConfigModel | DatabaseOrmDataHierarchyModel]]] = {
      UploadModel: DatabaseOrmAdapter.get_orm_upload_model,
      ConfigModel: DatabaseOrmAdapter.get_orm_config_model,
      ProjectModel: DatabaseOrmAdapter.get_orm_project_model,
      DataHierarchyModel: DatabaseOrmAdapter.get_orm_data_hierarchy_model
    }

    self.to_base_model_converter_map: dict[orm_model_type, Callable[
      Type[DatabaseOrmUploadModel | DatabaseOrmConfigModel | DatabaseOrmDataHierarchyModel], Type[
        UploadModel | ConfigModel | DataHierarchyModel]]] = {
      DatabaseOrmUploadModel: DatabaseOrmAdapter.get_upload_model,
      DatabaseOrmConfigModel: DatabaseOrmAdapter.get_config_model,
      DatabaseOrmDataHierarchyModel: DatabaseOrmAdapter.get_data_hierarchy_model
    }

    if isinstance(dataverse_db_path, str):
      self.db_url_map[DatabaseNames.DataverseDatabase] = f"sqlite:///{dataverse_db_path}"
    else:
      raise IncorrectParameterError(f"Database path must be a string: {dataverse_db_path}")
    if isinstance(pasta_project_group_db_path, str):
      self.db_url_map[DatabaseNames.PastaProjectGroupDatabase] = f"sqlite:///{pasta_project_group_db_path}"
    else:
      raise IncorrectParameterError(f"Database path must be a string: {pasta_project_group_db_path}")
    self.model_db_url_map: dict[Type[UploadModel | ConfigModel | ProjectModel | DataHierarchyModel], str] = {
      UploadModel: self.db_url_map[DatabaseNames.DataverseDatabase],
      ConfigModel: self.db_url_map[DatabaseNames.DataverseDatabase],
      DataHierarchyModel: self.db_url_map[DatabaseNames.PastaProjectGroupDatabase],
      ProjectModel: self.db_url_map[DatabaseNames.PastaProjectGroupDatabase],
    }

  def create_and_init_database(self) -> None:
    self.logger.info("Creating database at the location : %s", self.db_url_map[DatabaseNames.DataverseDatabase])
    engine = create_engine(self.db_url_map[DatabaseNames.DataverseDatabase])
    DatabaseModelBase.metadata.tables[DatabaseOrmConfigModel.__tablename__].create(bind=engine, checkfirst=True)
    DatabaseModelBase.metadata.tables[DatabaseOrmUploadModel.__tablename__].create(bind=engine, checkfirst=True)
    engine = create_engine(self.db_url_map[DatabaseNames.PastaProjectGroupDatabase])
    DatabaseModelBase.metadata.tables[DatabaseOrmMainModel.__tablename__].create(bind=engine, checkfirst=True)
    DatabaseModelBase.metadata.tables[DatabaseOrmPropertiesModel.__tablename__].create(bind=engine, checkfirst=True)
    DatabaseModelBase.metadata.tables[DatabaseOrmDataHierarchyModel.__tablename__].create(bind=engine, checkfirst=True)

  def insert_model(self, data_model: Union[UploadModel, ConfigModel]) -> Union[UploadModel, ConfigModel]:
    self.logger.info("Populating document with data: %s in database: %s",
                     data_model,
                     "config")
    engine = create_engine(self.db_url_map[DatabaseNames.DataverseDatabase])
    model = self.to_orm_converter_map[type(data_model)](data_model)
    with Session(engine) as session:
      session.add(model)
      session.commit()
      session.flush()
      return self.to_base_model_converter_map[type(model)](model)

  def get_model(self, model_id: int | str,
                model_type: Type[Union[UploadModel, ConfigModel, DataHierarchyModel, ProjectModel]]) -> Union[
    UploadModel, ProjectModel, ConfigModel, DataHierarchyModel, None]:
    self.logger.info("Retrieving data model with id: %s, type: %s", model_id, model_type)
    if not model_id:
      raise log_and_create_error(self.logger, DatabaseError, "Model ID cannot be empty!")

    match model_type():
      case UploadModel() | ConfigModel() | DataHierarchyModel():
        engine = create_engine(self.model_db_url_map[model_type])
        with Session(engine) as session:
          db_model = session.get(self.model_mapping[model_type], model_id)
          return self.to_base_model_converter_map[type(db_model)](db_model) if db_model else None
      case ProjectModel():
        return self.get_project_model(model_id)
      case _:
        raise log_and_create_error(self.logger, DatabaseError, "Model type not found!")

  def get_models(self, model_type: Type[Union[UploadModel, ConfigModel, DataHierarchyModel]]) -> list[
    Union[UploadModel, ConfigModel, DataHierarchyModel]]:
    self.logger.info("Retrieving models from database, type: %s", model_type)
    if not model_type:
      raise log_and_create_error(self.logger, DatabaseError, "Model Type cannot be empty!")
    stmt = select(self.model_mapping[model_type])
    engine = create_engine(self.model_db_url_map[model_type])
    with Session(engine) as session:
      models = session.scalars(stmt).all()
      return [self.to_base_model_converter_map[type(model)](model) for model in models]

  def get_project_models(self) -> list[ProjectModel]:
    self.logger.info("Retrieving projects from database: %s", DatabaseNames.PastaProjectGroupDatabase)
    engine = create_engine(self.db_url_map[DatabaseNames.PastaProjectGroupDatabase])
    statement = generate_project_join_statement(None)
    with Session(engine) as session:
      return [DatabaseOrmAdapter.get_project_model(r.tuple()) for r in session.execute(statement).fetchall()]

  def get_project_model(self, model_id: str) -> ProjectModel:
    self.logger.info("Retrieving project from database: %s, model id: %s",
                     DatabaseNames.PastaProjectGroupDatabase,
                     model_id)
    if not model_id:
      raise log_and_create_error(self.logger, DatabaseError, "Model ID cannot be empty!")
    engine = create_engine(self.db_url_map[DatabaseNames.PastaProjectGroupDatabase])
    statement = generate_project_join_statement(model_id)
    with Session(engine) as session:
      return DatabaseOrmAdapter.get_project_model(session.execute(statement).fetchone().tuple())

  def update_model(self, data_model: Union[UploadModel, ConfigModel]) -> None:
    model_type = type(data_model)
    self.logger.info("Updating data model with id: %s, type: %s", data_model.id,
                     model_type)
    if not data_model.id:
      raise log_and_create_error(self.logger, DatabaseError, "Model ID cannot be empty!")
    engine = create_engine(self.model_db_url_map[model_type])
    with Session(engine) as session:
      db_model = self.to_orm_converter_map[model_type](data_model)
      if not (session.get(type(db_model),
                          db_model.id)):
        raise log_and_create_error(self.logger, DatabaseError, "Model does not exist in database!")
      session.merge(db_model)
      session.commit()

  def get_paginated_models(self,
                           model_type: Type[Union[UploadModel, ConfigModel, DataHierarchyModel]],
                           filter_term: str | None = None,
                           filter_fields: list[str] | None = None,
                           order_by_column: str | None = None,
                           page_number: int = 1,
                           limit: int = 10) -> list[[Union[UploadModel, ConfigModel, DataHierarchyModel]]]:
    if page_number < 1:
      raise log_and_create_error(self.logger, DatabaseError, "Page number cannot be less than 1!")
    if limit < 1:
      raise log_and_create_error(self.logger, DatabaseError, "Limit cannot be less than 1!")
    engine = create_engine(self.model_db_url_map[model_type])
    query = select(self.model_mapping[model_type]).limit(limit).offset((page_number - 1) * limit)
    with Session(engine) as session:
      if filter_fields is None:
        filter_fields = self.model_mapping[model_type].get_table_columns()
      if filter_term:
        query = query.filter(
          or_(*[getattr(self.model_mapping[model_type], field).like(f"%{filter_term}%") for field in filter_fields]))
      query = query.order_by(getattr(self.model_mapping[model_type], order_by_column).desc())
      docs = session.execute(query).scalars().all()
      return [self.to_base_model_converter_map[type(doc)](doc) for doc in docs]

  def get_models_count(self,
                       model_type: Type[Union[UploadModel, ConfigModel, DataHierarchyModel]]
                       ) -> int:
    engine = create_engine(self.model_db_url_map[model_type])
    with Session(engine) as session:
      return session.query(self.model_mapping[model_type]).count()
