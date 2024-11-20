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
from typing import Type, Union

from sqlalchemy import create_engine, or_, select
from sqlalchemy.orm import Session

from pasta_eln.dataverse.base_model import BaseModel
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.data_hierarchy_model import DataHierarchyModel
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.database_names import DatabaseNames
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


class BaseDatabaseApi:
  """Handles database operations for various model types.

  This class provides methods to interact with the database, including creating,
  updating, retrieving, and counting models. It supports multiple model types and
  manages the conversion between base models and ORM models.

  Args:
      dataverse_db_path (str): The path to the Dataverse database.
      pasta_project_group_db_path (str): The path to the Pasta Project Group database.
  """

  def __init__(self,
               dataverse_db_path: str,
               pasta_project_group_db_path: str) -> None:
    self.logger = logging.getLogger('sqlalchemy.engine')
    self.logger.setLevel(logging.INFO)
    self.db_url_map: dict[DatabaseNames, str] = {}
    base_model_type = Type[BaseModel | UploadModel | ConfigModel | ProjectModel | DataHierarchyModel]
    orm_model_type = Type[
      DatabaseModelBase | DatabaseOrmUploadModel | DatabaseOrmConfigModel | DatabaseOrmDataHierarchyModel]
    self.model_mapping: dict[base_model_type, orm_model_type] = {
      UploadModel: DatabaseOrmUploadModel,
      ConfigModel: DatabaseOrmConfigModel,
      DataHierarchyModel: DatabaseOrmDataHierarchyModel
    }
    self.to_orm_converter_map: dict[base_model_type,  # type: ignore[valid-type, misc]
    Callable[base_model_type, orm_model_type]] = {
      UploadModel: DatabaseOrmAdapter.get_orm_upload_model,
      ConfigModel: DatabaseOrmAdapter.get_orm_config_model,
      ProjectModel: DatabaseOrmAdapter.get_orm_project_model,
      DataHierarchyModel: DatabaseOrmAdapter.get_orm_data_hierarchy_model
    }

    self.to_base_model_converter_map: dict[orm_model_type,  # type: ignore[valid-type, misc]
    Callable[orm_model_type, base_model_type]] = {
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
    """Creates and initializes the database.

    This function sets up the database by creating the necessary tables for the
    application. It logs the database creation process and ensures that the tables
    are created only if they do not already exist.

    Args:
        self: The instance of the class.

    Raises:
        SQLAlchemyError: If there is an error during the database creation process.
    """
    self.logger.info("Creating database at the location : %s",
                     self.db_url_map[DatabaseNames.DataverseDatabase])
    engine = create_engine(self.db_url_map[DatabaseNames.DataverseDatabase])
    (DatabaseModelBase.metadata.tables[DatabaseOrmConfigModel.__tablename__]
     .create(bind=engine, checkfirst=True))
    (DatabaseModelBase.metadata.tables[DatabaseOrmUploadModel.__tablename__]
     .create(bind=engine, checkfirst=True))
    engine = create_engine(self.db_url_map[DatabaseNames.PastaProjectGroupDatabase])
    (DatabaseModelBase.metadata.tables[DatabaseOrmMainModel.__tablename__]
     .create(bind=engine, checkfirst=True))
    (DatabaseModelBase.metadata.tables[DatabaseOrmPropertiesModel.__tablename__]
     .create(bind=engine, checkfirst=True))
    (DatabaseModelBase.metadata.tables[DatabaseOrmDataHierarchyModel.__tablename__]
     .create(bind=engine, checkfirst=True))

  def insert_model(self, data_model: Union[UploadModel, ConfigModel]) -> Union[UploadModel, ConfigModel]:
    """Inserts a data model into the database.

    This function takes a data model, converts it to the corresponding ORM model,
    and inserts it into the database. It logs the operation and returns the inserted
    model in its base form.

    Args:
        data_model(Union[UploadModel, ConfigModel]) : The data model to be inserted, which can be either an
        UploadModel or a ConfigModel.

    Returns:
        The inserted data model in its base form.

    Raises:
        SQLAlchemyError: If there is an error during the database insertion process.
    """
    self.logger.info("Populating document with data: %s in database: %s",
                     data_model,
                     self.db_url_map[DatabaseNames.DataverseDatabase])
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
    """Retrieves a data model from the database based on its ID and type.

    This function fetches a specified model from the database using its ID and type.
    It logs the retrieval process and returns the model in its base form, or None if
    the model does not exist.

    Args:
        model_id (int | str): The ID of the model to retrieve, which can be an integer or a string.
        model_type (Type[Union[UploadModel, ConfigModel, DataHierarchyModel, ProjectModel]]):
            The type of the model to retrieve, which can be one of UploadModel, ConfigModel,
            DataHierarchyModel, or ProjectModel.

    Returns:
        Union[UploadModel, ProjectModel, ConfigModel, DataHierarchyModel, None]:
            The retrieved model in its base form, or None if the model does not exist.

    Raises:
        DatabaseError: If the model ID is empty or if the model type is not found.
    """
    self.logger.info("Retrieving data model with id: %s, type: %s", model_id, model_type)
    if not model_id:
      raise log_and_create_error(self.logger, DatabaseError, "Model ID cannot be empty!")

    match model_type():
      case UploadModel() | ConfigModel() | DataHierarchyModel():
        engine = create_engine(self.model_db_url_map[model_type])
        with Session(engine) as session:
          db_model = session.get(self.model_mapping[model_type], model_id)
          return self.to_base_model_converter_map[self.model_mapping[model_type]](db_model) if db_model else None
      case ProjectModel():
        return self.get_project_model(model_id) if isinstance(model_id, str) else None
      case _:
        raise log_and_create_error(self.logger, DatabaseError, "Model type not found!")

  def get_models(self, model_type: Type[UploadModel | ConfigModel | DataHierarchyModel]) -> list[
    Union[UploadModel, ConfigModel, DataHierarchyModel]]:
    """Retrieves a list of models from the database based on the specified type.

    This function queries the database for models of the given type and returns them
    in a list. It logs the retrieval process and raises an error if the model type is
    not provided.

    Args:
        model_type (Type[UploadModel | ConfigModel | DataHierarchyModel]):
            The type of models to retrieve, which can be UploadModel, ConfigModel,
            or DataHierarchyModel.

    Returns:
        list[Union[UploadModel, ConfigModel, DataHierarchyModel]]:
            A list of models of the specified type retrieved from the database.

    Raises:
        DatabaseError: If the model type is not provided or if there is an error
        during the database retrieval process.
    """
    self.logger.info("Retrieving models from database, type: %s", model_type)
    if not model_type:
      raise log_and_create_error(self.logger, DatabaseError, "Model Type cannot be empty!")
    stmt = select(self.model_mapping[model_type])
    engine = create_engine(self.model_db_url_map[model_type])
    with Session(engine) as session:
      models = session.scalars(stmt).all()
      return [self.to_base_model_converter_map[type(model)](model) for model in models]

  def get_project_models(self) -> list[ProjectModel]:
    """Retrieves a list of project models from the database.

    This function queries the database for all project models and returns them
    as a list. It logs the retrieval process and utilizes a session to execute
    the query and convert the results into project model instances.

    Returns:
        list[ProjectModel]: A list of project models retrieved from the database.

    Raises:
        SQLAlchemyError: If there is an error during the database retrieval process.
    """
    self.logger.info("Retrieving projects from database: %s", DatabaseNames.PastaProjectGroupDatabase)
    engine = create_engine(self.db_url_map[DatabaseNames.PastaProjectGroupDatabase])
    statement = generate_project_join_statement(None)
    with Session(engine) as session:
      return [DatabaseOrmAdapter.get_project_model(r.tuple()) for r in session.execute(statement).fetchall()]

  def get_project_model(self, model_id: str) -> ProjectModel:
    """Retrieves a project model from the database using its ID.

    This function queries the database for a project model associated with the given
    model ID. It logs the retrieval process and raises an error if the model ID is
    not provided.

    Args:
        model_id (str): The ID of the project model to retrieve.

    Returns:
        ProjectModel: The project model retrieved from the database.

    Raises:
        DatabaseError: If the model ID is empty or if there is an error during
        the database retrieval process.
    """
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
    """Updates an existing data model in the database.

    This function takes a data model, verifies its ID, and updates the corresponding
    record in the database. It logs the update process and raises an error if the
    model ID is not provided or if the model does not exist in the database.

    Args:
        data_model (Union[UploadModel, ConfigModel]): The data model to be updated,
        which can be either an UploadModel or a ConfigModel.

    Raises:
        DatabaseError: If the model ID is empty or if the model does not exist in
        the database during the update process.
    """
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
                           limit: int = 10) -> list[Type[UploadModel | ConfigModel | DataHierarchyModel]]:
    """Retrieves a paginated list of models from the database.

    This function fetches a specified number of models of a given type from the
    database, applying optional filters and sorting. It supports pagination to
    manage large datasets effectively.

    Args:
        model_type (Type[Union[UploadModel, ConfigModel, DataHierarchyModel]]):
            The type of models to retrieve, which can be UploadModel, ConfigModel,
            or DataHierarchyModel.
        filter_term (str | None): An optional term to filter the results.
        filter_fields (list[str] | None): An optional list of fields to apply the filter on.
        order_by_column (str | None): An optional column name to sort the results by.
        page_number (int): The page number to retrieve (default is 1).
        limit (int): The maximum number of results to return per page (default is 10).

    Returns:
        list[Type[UploadModel | ConfigModel | DataHierarchyModel]]:
            A list of models of the specified type retrieved from the database.

    Raises:
        DatabaseError: If the page number or limit is less than 1.
    """
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
      if order_by_column:
        query = query.order_by(getattr(self.model_mapping[model_type], order_by_column).desc())
      models = session.execute(query).scalars().all()
      return [self.to_base_model_converter_map[type(model)](model) for model in models]

  def get_models_count(self,
                       model_type: Type[Union[UploadModel, ConfigModel, DataHierarchyModel]]
                       ) -> int:
    """Retrieves the count of models of a specified type from the database.

    This function queries the database to count the number of records for the
    specified model type. It returns the total count, allowing for quick
    assessments of the number of entries in the database.

    Args:
        model_type (Type[Union[UploadModel, ConfigModel, DataHierarchyModel]]):
            The type of models for which to retrieve the count, which can be
            UploadModel, ConfigModel, or DataHierarchyModel.

    Returns:
        int: The count of models of the specified type in the database.

    Raises:
        KeyError: If the model type is not found in the model mapping.
    """
    engine = create_engine(self.model_db_url_map[model_type])
    with Session(engine) as session:
      return session.query(self.model_mapping[model_type]).count()
