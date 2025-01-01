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
from pasta_eln.database.error import Error
from pasta_eln.database.incorrect_parameter_error import IncorrectParameterError
from pasta_eln.database.models.data_hierarchy_definition_orm_model import DataHierarchyDefinitionOrmModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.database.models.data_hierarchy_orm_model import DataHierarchyOrmModel
from pasta_eln.database.models.orm_model_base import OrmModelBase
from pasta_eln.database.orm_model_adapter import OrmModelAdapter
from pasta_eln.dataverse.utils import log_and_create_error


class BaseDatabaseApi:
  """A class for managing database operations related to data hierarchy models.

  This class provides methods to create, retrieve, update, and check the existence of
  data hierarchy models in a database. It utilizes SQLAlchemy for database interactions
  and includes logging for tracking operations.

  Args:
      pasta_project_group_db_path (str): The path to the database file.

  Raises:
      IncorrectParameterError: If the provided database path is not a string.
  """

  def __init__(self,
               pasta_project_group_db_path: str) -> None:
    """Initializes the database API with the specified database path.

    This constructor sets up a logger for SQLAlchemy and constructs the database URL
    based on the provided path. If the path is not a string, an error is raised.

    Args:
        pasta_project_group_db_path (str): The path to the database file.

    Raises:
        IncorrectParameterError: If the provided database path is not a string.
    """
    self.logger = logging.getLogger('sqlalchemy.engine')
    self.logger.setLevel(logging.INFO)
    if isinstance(pasta_project_group_db_path, str):
      self.db_url = f"sqlite:///{pasta_project_group_db_path}"
    else:
      raise IncorrectParameterError(f"Database path must be a string: {pasta_project_group_db_path}")

  def create_and_bind_db_tables(self) -> None:
    """Creates and binds the necessary database tables.

    This method initializes the database tables for the data hierarchy models
    by creating them in the database specified by the instance's db_url. It logs
    the action and ensures that the tables are created only if they do not already exist.

    Raises:
        SQLAlchemyError: If there is an issue with creating the tables in the database.
    """
    self.logger.info('Creating and binding table for db : %s',
                     self.db_url)
    engine = create_engine(self.db_url)
    (OrmModelBase.metadata.tables[DataHierarchyOrmModel.__tablename__]
     .create(bind=engine, checkfirst=True))
    (OrmModelBase.metadata.tables[DataHierarchyDefinitionOrmModel.__tablename__]
     .create(bind=engine, checkfirst=True))

  def get_data_hierarchy_model(self, model_doc_type: int | str) -> Union[DataHierarchyModel, None]:
    """Retrieves a DataHierarchyModel based on the provided document type.

    This method logs the retrieval process and checks if the document type is valid.
    If the document type is empty, an error is raised. It then queries the database
    for the corresponding DataHierarchyOrmModel and returns the adapted DataHierarchyModel.

    Args:
        model_doc_type (int | str): The document type used to retrieve the model.

    Returns:
        Union[DataHierarchyModel, None]: The corresponding DataHierarchyModel if found,
        otherwise None.

    Raises:
        Error: If the model_doc_type is empty.
    """
    self.logger.info('Retrieving DataHierarchyModel with doctype: %s', model_doc_type)
    if not model_doc_type:
      raise log_and_create_error(self.logger, Error, 'Model Doc Type cannot be empty!')
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      db_model = session.get(DataHierarchyOrmModel, model_doc_type)
      if db_model and isinstance(db_model,
                                 DataHierarchyOrmModel):
        return OrmModelAdapter.get_data_hierarchy_model(db_model)
      else:
        return None

  def get_data_hierarchy_models(self) -> list[DataHierarchyModel]:
    """Retrieves all DataHierarchyModel instances from the database.

    This method logs the retrieval process and queries the database for all
    DataHierarchyOrmModel entries. It then adapts these ORM models into
    DataHierarchyModel instances for further use.

    Returns:
        list[DataHierarchyModel]: A list of DataHierarchyModel instances retrieved from the database.
    """
    self.logger.info('Retrieving data_hierarchy_models from database')
    stmt = select(DataHierarchyOrmModel)
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      models = session.scalars(stmt).all()
      return [OrmModelAdapter.get_data_hierarchy_model(model) for model in models]

  def insert_data_hierarchy_model(self, data_model: Union[DataHierarchyModel]) -> Union[DataHierarchyModel]:
    """Inserts a DataHierarchyModel into the database.

    This method logs the insertion process and converts the provided DataHierarchyModel
    into an ORM model before adding it to the database. After committing the transaction,
    it returns the adapted DataHierarchyModel.

    Args:
        data_model (Union[DataHierarchyModel]): The DataHierarchyModel instance to be inserted.

    Returns:
        Union[DataHierarchyModel]: The inserted DataHierarchyModel instance after adaptation.

    Raises:
        Exception: If there is an error during the database operation.
    """
    self.logger.info('Populating DataHierarchyModel with data: %s in database: %s',
                     data_model,
                     self.db_url)
    engine = create_engine(self.db_url)
    model = OrmModelAdapter.get_orm_data_hierarchy_model(data_model)
    with Session(engine) as session:
      session.add(model)
      session.commit()
      session.flush()
      return OrmModelAdapter.get_data_hierarchy_model(model)

  def update_data_hierarchy_model(self, data_model: DataHierarchyModel) -> None:
    """Updates an existing DataHierarchyModel in the database.

    This method logs the update process and checks if the provided data model's
    document type is valid. If the document type is empty or the model does not
    exist in the database, an error is raised. If valid, the model is merged into
    the session and the changes are committed to the database.

    Args:
        data_model (DataHierarchyModel): The DataHierarchyModel instance to be updated.

    Raises:
        Error: If the model's document type is empty or if the model does not exist in the database.
    """
    self.logger.info('Updating data model with doc_type: %s', data_model.doc_type)
    if not data_model.doc_type:
      raise log_and_create_error(self.logger, Error, 'Model doc_type cannot be empty!')
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      db_model = OrmModelAdapter.get_orm_data_hierarchy_model(data_model)
      if not (session.get(DataHierarchyOrmModel,
                          db_model.doc_type)):
        raise log_and_create_error(self.logger, Error, 'Model does not exist in database!')
      session.merge(db_model)
      session.commit()

  def check_if_data_hierarchy_model_exists(self, model_doc_type: str) -> bool:
    """Checks if a DataHierarchyModel exists in the database.

    This method logs the retrieval process and verifies if the provided document type
    is valid. If the document type is empty, an error is raised. It then queries the
    database to determine if a model with the specified document type exists.

    Args:
        model_doc_type (str): The document type of the DataHierarchyModel to check.

    Returns:
        bool: True if the model exists in the database, False otherwise.

    Raises:
        Error: If the model_doc_type is empty.
    """
    self.logger.info('Retrieving data_hierarchy_model with doctype: %s', model_doc_type)
    if not model_doc_type:
      raise log_and_create_error(self.logger, Error, 'Model Doc Type cannot be empty!')
    engine = create_engine(self.db_url)
    with Session(engine) as session:
      return isinstance(session.get(DataHierarchyOrmModel, model_doc_type), DataHierarchyOrmModel)
