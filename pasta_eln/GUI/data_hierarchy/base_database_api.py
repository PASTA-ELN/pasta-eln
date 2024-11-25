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
from typing import Union

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from pasta_eln.database.database_orm_adapter import DatabaseOrmAdapter
from pasta_eln.database.error import Error
from pasta_eln.database.models.data_hierarchy_definition_orm_model import DataHierarchyDefinitionOrmModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.database.models.data_hierarchy_orm_model import DataHierarchyOrmModel
from pasta_eln.database.models.orm_model_base import OrmModelBase
from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.dataverse.utils import log_and_create_error


class BaseDatabaseApi:

  def __init__(self,
               pasta_project_group_db_path: str) -> None:
    self.logger = logging.getLogger('sqlalchemy.engine')
    self.logger.setLevel(logging.INFO)
    if isinstance(pasta_project_group_db_path, str):
      self.db_url = f"sqlite:///{pasta_project_group_db_path}"
    else:
      raise IncorrectParameterError(f"Database path must be a string: {pasta_project_group_db_path}")

  def create_and_bind_db_tables(self) -> None:
    self.logger.info("Creating and binding table for db : %s",
                     self.db_url)
    engine = create_engine(self.db_url)
    (OrmModelBase.metadata.tables[DataHierarchyOrmModel.__tablename__]
     .create(bind=engine, checkfirst=True))
    (OrmModelBase.metadata.tables[DataHierarchyDefinitionOrmModel.__tablename__]
     .create(bind=engine, checkfirst=True))

  def insert_data_hierarchy_model(self, data_model: Union[DataHierarchyModel]) -> Union[DataHierarchyModel]:
    self.logger.info("Populating document with data: %s in database: %s",
                     data_model,
                     self.db_url)
    engine = create_engine(self.db_url)
    model = DatabaseOrmAdapter.get_orm_data_hierarchy_model(data_model)
    with Session(engine) as session:
      session.add(model)
      session.commit()
      session.flush()
      return DatabaseOrmAdapter.get_data_hierarchy_model(model)

  def get_data_hierarchy_model(self, model_doc_type: int | str) -> Union[DataHierarchyModel, None]:
    self.logger.info("Retrieving data_hierarchy_model with doctype: %s", model_doc_type)
    if not model_doc_type:
      raise log_and_create_error(self.logger, Error, "Model Doc Type cannot be empty!")
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      db_model = session.get(DataHierarchyOrmModel, model_doc_type)
      if db_model and isinstance(db_model,
                                 DataHierarchyOrmModel):
        return DatabaseOrmAdapter.get_data_hierarchy_model(db_model)
      else:
        return None

  def check_if_data_hierarchy_model_exists(self, model_doc_type: str) -> bool:
    self.logger.info("Retrieving data_hierarchy_model with doctype: %s", model_doc_type)
    if not model_doc_type:
      raise log_and_create_error(self.logger, Error, "Model Doc Type cannot be empty!")
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      return isinstance(session.get(DataHierarchyOrmModel, model_doc_type), DataHierarchyOrmModel)

  def get_data_hierarchy_models(self) -> list[DataHierarchyModel]:
    self.logger.info("Retrieving data_hierarchy_models from database")
    stmt = select(DataHierarchyOrmModel)
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      models = session.scalars(stmt).all()
      return [DatabaseOrmAdapter.get_data_hierarchy_model(model) for model in models]

  def update_data_hierarchy_model(self, data_model: DataHierarchyModel) -> None:
    self.logger.info("Updating data model with doc_type: %s", data_model.doc_type)
    if not data_model.doc_type:
      raise log_and_create_error(self.logger, Error, "Model doc_type cannot be empty!")
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      db_model = DatabaseOrmAdapter.get_orm_data_hierarchy_model(data_model)
      if not (session.get(DataHierarchyOrmModel,
                          db_model.doc_type)):
        raise log_and_create_error(self.logger, Error, "Model does not exist in database!")
      session.merge(db_model)
      session.commit()
