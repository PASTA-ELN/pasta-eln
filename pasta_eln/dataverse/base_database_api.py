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
from threading import Lock
from typing import Sequence, Type, Union

from sqlalchemy import and_, create_engine, or_, select
from sqlalchemy.orm import Session, aliased

from pasta_eln.dataverse.base_model import BaseModel
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.database_orm_adapter import DatabaseOrmAdapter
from pasta_eln.dataverse.database_orm_config_model import DatabaseOrmConfigModel
from pasta_eln.dataverse.database_orm_main_model import DatabaseOrmMainModel
from pasta_eln.dataverse.database_orm_properties_model import DatabaseOrmPropertiesModel
from pasta_eln.dataverse.database_orm_upload_model import DatabaseOrmUploadModel
from pasta_eln.dataverse.database_sqlalchemy_base import DatabaseModelBase
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.utils import log_and_create_error


class DatabaseNames(Enum):
  DataverseDatabase = 1
  PastaProjectGroupDatabase = 2


class BaseDatabaseApi:
  def __init__(self,
               dataverse_db_path: str,
               pasta_project_group_db_path: str) -> None:
    super().__init__()
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.db_url_map: dict[DatabaseNames, str] = {}

    base_model_type = Type[UploadModel | ConfigModel | ProjectModel]
    orm_model_type = Type[DatabaseOrmUploadModel | DatabaseOrmConfigModel]
    self.model_mapping: dict[base_model_type, orm_model_type] = {
      UploadModel: DatabaseOrmUploadModel,
      ConfigModel: DatabaseOrmConfigModel,
    }
    self.to_orm_converter_map: dict[base_model_type, Callable[Type[UploadModel | ConfigModel | ProjectModel], Type[
      DatabaseOrmUploadModel | DatabaseOrmConfigModel]]] = {
      UploadModel: DatabaseOrmAdapter.get_orm_upload_model,
      ConfigModel: DatabaseOrmAdapter.get_orm_config_model,
      ProjectModel: DatabaseOrmAdapter.get_orm_project_model
    }

    self.to_base_model_converter_map: dict[orm_model_type, Callable[
      Type[DatabaseOrmUploadModel | DatabaseOrmConfigModel], Type[
        UploadModel | ConfigModel | ProjectModel]]] = {
      DatabaseOrmUploadModel: DatabaseOrmAdapter.get_upload_model,
      DatabaseOrmConfigModel: DatabaseOrmAdapter.get_config_model
    }

    if isinstance(dataverse_db_path, str):
      self.db_url_map[DatabaseNames.DataverseDatabase] = f"sqlite:///{dataverse_db_path}"
    else:
      raise IncorrectParameterError(f"Database path must be a string: {dataverse_db_path}")
    if isinstance(pasta_project_group_db_path, str):
      self.db_url_map[DatabaseNames.PastaProjectGroupDatabase] = f"sqlite:///{pasta_project_group_db_path}"
    else:
      raise IncorrectParameterError(f"Database path must be a string: {pasta_project_group_db_path}")
    self.update_lock = Lock()

  def create_and_init_database(self) -> None:
    self.logger.info("Creating database at the location : %s", self.db_url_map[DatabaseNames.DataverseDatabase])
    engine = create_engine(self.db_url_map[DatabaseNames.DataverseDatabase], echo=True)
    DatabaseModelBase.metadata.create_all(engine)

  def insert_model(self, data_model: Union[UploadModel, ConfigModel]) -> Union[UploadModel, ConfigModel]:
    self.logger.info("Populating document with data: %s in database: %s",
                     data_model,
                     "config")
    engine = create_engine(self.db_url_map[DatabaseNames.DataverseDatabase], echo=True)
    model = self.to_orm_converter_map[type(data_model)](data_model)
    with Session(engine) as session:
      session.add(model)
      session.commit()
      session.flush()
      return self.to_base_model_converter_map[type(model)](model)

  def get_model(self, model_id: int, db_name: DatabaseNames,
                model_type: Type[Union[UploadModel, ConfigModel, ProjectModel]]) -> BaseModel:
    self.logger.info("Retrieving data model with id: %s from database: %s, type: %s", model_id, db_name, model_type)
    if not model_id:
      raise log_and_create_error(self.logger, DatabaseError, "Model ID cannot be empty!")
    engine = create_engine(self.db_url_map[db_name], echo=True)
    with Session(engine) as session:
      if db_model := session.get(self.model_mapping[model_type], model_id):
        return self.to_base_model_converter_map[type(db_model)](db_model)
      else:
        raise log_and_create_error(self.logger, DatabaseError, "Model not found!")

  def get_projects(self, db_name: DatabaseNames) -> Sequence[ProjectModel]:
    self.logger.info("Retrieving projects from database: %s", db_name)
    engine = create_engine(self.db_url_map[db_name], echo=True)
    properties_objective_aliased = aliased(DatabaseOrmPropertiesModel)
    properties_status_aliased = aliased(DatabaseOrmPropertiesModel)
    statement = (select(DatabaseOrmMainModel, properties_status_aliased.value,
                        properties_objective_aliased.value)
                 .where(DatabaseOrmMainModel.type == "x0")
                 .join_from(DatabaseOrmMainModel, properties_objective_aliased,
                            and_(DatabaseOrmMainModel.id == properties_objective_aliased.id,
                                 properties_objective_aliased.key == ".objective"), isouter=True)
                 .join_from(DatabaseOrmMainModel, properties_status_aliased,
                            and_(DatabaseOrmMainModel.id == properties_status_aliased.id,
                                 properties_status_aliased.key == ".status"), isouter=True))

    with Session(engine) as session:
      return [DatabaseOrmAdapter.get_project_model(r.tuple()) for r in session.execute(statement).fetchall()]

  def update_model(self, db_name: DatabaseNames,
                   data_model: Union[UploadModel, ConfigModel, ProjectModel]) -> None:
    self.logger.info("Updating data model with id: %s in database: %s, type: %s", data_model.id, db_name,
                     type(data_model))
    if not data_model.id:
      raise log_and_create_error(self.logger, DatabaseError, "Model ID cannot be empty!")
    engine = create_engine(self.db_url_map[db_name], echo=True)
    with Session(engine) as session:
      db_model = self.to_orm_converter_map[type(data_model)](data_model)
      if not (session.get(type(db_model),
                          db_model.id)):
        raise log_and_create_error(self.logger, DatabaseError, "Model does not exist in database!")
      session.merge(db_model)
      session.commit()

  def get_paginated_results(self, db_name: DatabaseNames,
                            model_type: Type[Union[UploadModel, ConfigModel]],
                            filter_term: str | None = None,
                            filter_fields: list[str] | None = None,
                            page_number: int = 1,
                            limit: int = 10) -> list[Type[Union[UploadModel, ConfigModel]]]:
    if page_number < 1:
      raise log_and_create_error(self.logger, DatabaseError, "Page number cannot be less than 1!")
    if limit < 1:
      raise log_and_create_error(self.logger, DatabaseError, "Limit cannot be less than 1!")
    engine = create_engine(self.db_url_map[db_name], echo=True)
    query = select(self.model_mapping[model_type]).limit(limit).offset((page_number - 1) * limit)
    with Session(engine) as session:
      if filter_term:
        query = query.filter(
          or_(*[getattr(self.model_mapping[model_type], field).like(f"%{filter_term}%") for field in filter_fields]))
      docs = session.execute(query).scalars().all()
      return [self.to_base_model_converter_map[type(doc)](doc) for doc in docs]
