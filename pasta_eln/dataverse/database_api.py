""" Provides an interface to interact with the database for dataverse specific operations. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import logging
import math
from json import load
from os import getcwd
from os.path import dirname, join, realpath
from pathlib import Path
from typing import Union

from pasta_eln.database.error import Error
from pasta_eln.database.models.config_model import ConfigModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.database.models.project_model import ProjectModel
from pasta_eln.database.models.upload_model import UploadModel
from pasta_eln.dataverse.base_database_api import BaseDatabaseApi
from pasta_eln.dataverse.utils import (decrypt_data,
                                       encrypt_data,
                                       get_data_hierarchy_types,
                                       get_db_info, get_encrypt_key,
                                       log_and_create_error,
                                       set_authors,
                                       set_template_values)


class DatabaseAPI:
  """Handles database operations for various model types.

  This class provides methods to interact with the database, including creating,
  updating, retrieving, and counting models. It supports multiple model types and
  manages the conversion between base models and ORM models.
  """

  def __init__(self) -> None:
    """Initializes the DatabaseAPI instance.

    This constructor sets up the necessary attributes for the DatabaseAPI, including
    the configuration model ID, logger, database names, and database connections.
    It retrieves database information and initializes the database API.

    Raises:
        IncorrectParameterError: If the database path is None.
    """
    super().__init__()
    self.config_model_id: int = 1
    self.logger: logging.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.dataverse_db_name: str = '.pastaELN_dataverse'
    self.pasta_db_name: str = 'pastaELN'
    db_info: dict[str, str] = get_db_info(self.logger)
    db_path: str | None = db_info.get('database_path')
    if db_path is None:
      raise log_and_create_error(self.logger, Error, 'Database path is None!')
    self.db_api: BaseDatabaseApi = BaseDatabaseApi(
      f"{Path.home()}/{self.dataverse_db_name}.db",
      f"{db_path}/{self.pasta_db_name}.db"
    )
    _, self.encrypt_key = get_encrypt_key(self.logger)

  def create_model(self, data: Union[UploadModel, ConfigModel]) -> Union[
    UploadModel, ConfigModel]:
    """Creates a new model in the database.

            This function takes a data model, validates it, and inserts it into the database.
            It logs the creation process and raises an error if the data is invalid.

            Args:
                data (Union[UploadModel, ConfigModel]): The data model to be created.

            Returns:
                Union[UploadModel, ConfigModel]: The created model.

            Raises:
                ValueError: If the data is None.
                TypeError: If the data is not an instance of UploadModel or ConfigModel.
    """
    self.logger.info('Creating model: %s', data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, 'Data cannot be None!')
    if not isinstance(data, (UploadModel, ConfigModel)):
      raise log_and_create_error(self.logger, TypeError, 'Data must be an UploadModel or ConfigModel!')
    return self.db_api.insert_model(data)

  def update_model(self, data: UploadModel | ConfigModel) -> None:
    """Updates an existing model in the database.

            This function takes a data model, verifies its ID, and updates the corresponding
            record in the database. It logs the update process and raises an error if the
            model ID is not provided or if the model does not exist in the database.

            Args:
                data (Union[UploadModel, ConfigModel]): The data model to be updated.

            Raises:
                ValueError: If the data is None.
                TypeError: If the data is not an instance of UploadModel or ConfigModel.
    """
    self.logger.info('Updating model document: %s', data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, 'Data cannot be None!')
    if not isinstance(data, (UploadModel, ConfigModel)):
      raise log_and_create_error(self.logger, TypeError, 'Data must be an UploadModel, ConfigModel, or ProjectModel!')
    self.db_api.update_model(data)

  def get_models(self, model_type: type[UploadModel | ConfigModel | DataHierarchyModel | ProjectModel]) -> list[
    Union[UploadModel, ConfigModel, DataHierarchyModel, ProjectModel]]:
    """Retrieves a list of models from the database based on the specified type.

            This function queries the database for models of the given type and returns them
            in a list. It logs the retrieval process and raises an error if the model type is
            not provided.

            Args:
                model_type (Type[Union[UploadModel, ConfigModel, DataHierarchyModel, ProjectModel]]):
                    The type of models to retrieve.

            Returns:
                list[Union[UploadModel, ConfigModel, DataHierarchyModel, ProjectModel]]:
                    A list of models of the specified type retrieved from the database.

            Raises:
                TypeError: If the model type is not provided or unsupported.
    """
    self.logger.info('Retrieving models of type: %s', model_type)
    match model_type():
      case UploadModel() | ConfigModel() | DataHierarchyModel():
        return self.db_api.get_models(model_type)  # type: ignore
      case ProjectModel():
        return self.db_api.get_project_models()  # type: ignore
      case _:
        raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")

  def get_paginated_models(self,
                           model_type: type[Union[UploadModel, ConfigModel, DataHierarchyModel]],
                           filter_term: str | None = None,
                           filter_fields: list[str] | None = None,
                           order_by_column: str | None = None,
                           page_number: int = 1,
                           limit: int = 10) -> list[type[UploadModel | ConfigModel | DataHierarchyModel]]:
    """Retrieves a paginated list of models from the database.

            This function fetches a specified number of models of a given type from the
            database, applying optional filters and sorting. It supports pagination to
            manage large datasets effectively.

            Args:
                model_type (Type[Union[UploadModel, ConfigModel, DataHierarchyModel]]):
                    The type of models to retrieve.
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

    self.logger.info('Retrieving paginated models of type: %s, filter_term: %s, bookmark: %s, limit: %s',
                     model_type,
                     filter_term,
                     page_number,
                     limit)
    match model_type():
      case UploadModel() | ConfigModel() | DataHierarchyModel():
        return self.db_api.get_paginated_models(model_type,
                                                filter_term,
                                                filter_fields,
                                                order_by_column,
                                                page_number,
                                                limit)
      case _:
        raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")

  def get_last_page_number(self,
                           model_type: type[Union[UploadModel, ConfigModel, DataHierarchyModel]],
                           limit: int = 10) -> int:
    """Retrieves the last page number for a specified model type.

    This function calculates the last page number based on the total count of models
    of the specified type and the defined limit of models per page. It logs the
    retrieval process and raises an error if the model type is unsupported.

    Args:
        model_type (Type[Union[UploadModel, ConfigModel, DataHierarchyModel]]):
            The type of models for which to retrieve the last page number.
        limit (int): The maximum number of models per page (default is 10).

    Returns:
        int: The last page number for the specified model type.

    Raises:
        TypeError: If the model type is unsupported.
    """

    self.logger.info('Retrieving last page number of type: %s, limit: %s', model_type, limit)
    match model_type():
      case UploadModel() | ConfigModel() | DataHierarchyModel():
        row_count = self.db_api.get_models_count(model_type)
        return math.ceil(row_count / limit)
      case _:
        raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")

  def get_model(self, model_id: int | str,
                model_type: type[UploadModel | ConfigModel | DataHierarchyModel | ProjectModel]) -> Union[
    UploadModel, ConfigModel, DataHierarchyModel, ProjectModel, None]:
    """Retrieves a model from the database based on its ID and type.

    This function fetches a specified model from the database using its ID and type.
    It logs the retrieval process and raises an error if the model ID is not provided
    or if the model type is unsupported.

    Args:
        model_id (int | str): The ID of the model to retrieve, which can be an integer or a string.
        model_type (Type[UploadModel | ConfigModel | DataHierarchyModel | ProjectModel]):
            The type of the model to retrieve, which can be one of UploadModel,
            ConfigModel, DataHierarchyModel, or ProjectModel.

    Returns:
        Union[UploadModel, ConfigModel, DataHierarchyModel, ProjectModel, None]:
            The retrieved model in its base form, or None if the model does not exist.

    Raises:
        TypeError: If the model type is unsupported.
        ValueError: If the model ID is None.
    """
    self.logger.info('Retrieving model with id: %s, type: %s', model_id, model_type)
    if model_type not in (UploadModel, ProjectModel, ConfigModel):
      raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")
    if model_id is None:
      raise log_and_create_error(self.logger, ValueError, 'model_id cannot be None')
    return self.db_api.get_model(model_id,
                                 model_type)

  def get_config_model(self) -> ConfigModel | None:
    """Retrieves the configuration model from the database.

    This function fetches the configuration model using its ID and checks its validity.
    It logs the retrieval process and handles the decryption of sensitive information
    if an encryption key is available.

    Returns:
        ConfigModel | None: The configuration model retrieved from the database,
        or None if the model cannot be loaded or is invalid.

    Raises:
        DatabaseError: If the model ID is empty or if there is an error during
        the database retrieval process.
    """
    self.logger.info('Retrieving config model...')
    config_model = self.get_model(self.config_model_id, ConfigModel)
    if config_model is None or not isinstance(config_model, ConfigModel):
      self.logger.error('Fatal error, Failed to load config model!')
      return None
    if not isinstance(config_model.dataverse_login_info, dict):
      self.logger.error('Fatal Error, Invalid dataverse login info!')
      return None
    api_token = config_model.dataverse_login_info.get('api_token')
    if self.encrypt_key and api_token:
      config_model.dataverse_login_info['api_token'] = decrypt_data(self.logger, self.encrypt_key, api_token)
    if not self.encrypt_key and api_token:
      self.logger.warning(
        'No encryption key found. Hence if any API key exists, it will be removed and the user needs to re-enter it.')
      config_model.dataverse_login_info['api_token'] = None
      config_model.dataverse_login_info['dataverse_id'] = None
      self.update_model(config_model)
    return config_model

  def save_config_model(self, config_model: ConfigModel) -> None:
    """Saves the configuration model to the database.

    This function validates the provided configuration model and encrypts sensitive
    information before saving it to the database. It logs the saving process and
    raises an error if the model is invalid or if there is no encryption key.

    Args:
        config_model (ConfigModel): The configuration model to save.

    Raises:
        ValueError: If the config model is invalid.
        DatabaseError: If there is no encryption key found.
    """
    self.logger.info('Saving config model...')
    if (not config_model
        or not isinstance(config_model, ConfigModel)
        or not isinstance(config_model.dataverse_login_info, dict)):
      self.logger.error('Invalid config model!')
      return
    if not self.encrypt_key:
      raise log_and_create_error(self.logger, ValueError,
                                 'Fatal Error, No encryption key found! Make sure to initialize the database!')
    if api_token := config_model.dataverse_login_info['api_token']:
      config_model.dataverse_login_info['api_token'] = encrypt_data(self.logger, self.encrypt_key, api_token)
    if server_url := config_model.dataverse_login_info['server_url']:
      config_model.dataverse_login_info['server_url'] = server_url.strip('/').strip('\\')
    self.update_model(config_model)

  def get_data_hierarchy_models(self) -> list[DataHierarchyModel] | None:
    """Retrieves a list of data hierarchy models from the database.

    This function queries the database for all data hierarchy models and returns them
    as a list. It logs the retrieval process and warns if no data hierarchy items are found.

    Returns:
        list[DataHierarchyModel] | None: A list of data hierarchy models retrieved from the database,
        or None if no models are found.

    Raises:
        SQLAlchemyError: If there is an error during the database retrieval process.
    """
    self.logger.info('Retrieving data hierarchy...')
    results = self.db_api.get_models(DataHierarchyModel)
    if not results:
      self.logger.warning('Data hierarchy items not found!')
      return results  # type: ignore[return-value]
    return results  # type: ignore[return-value]

  def initialize_database(self) -> None:
    """Initializes the database for the dataverse module.

    This function sets up the database by creating necessary tables and ensuring
    that the configuration model is initialized. It logs the initialization process
    and checks if the configuration model exists, creating it if it does not.

    Raises:
        SQLAlchemyError: If there is an error during the database initialization process.
    """
    self.logger.info('Initializing database for dataverse module...')
    self.db_api.create_and_init_database()
    if self.db_api.get_model(self.config_model_id, ConfigModel) is None:
      self.initialize_config_document()

  def initialize_config_document(self) -> None:
    """Initializes the configuration document for the application.

    This function creates a new configuration model with default values and loads
    metadata from a JSON file. It sets template values and authors before saving
    the model to the database.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        JSONDecodeError: If there is an error decoding the JSON file.
    """
    self.logger.info('Initializing and saving the config model...')
    data_hierarchy_types: list[str] = get_data_hierarchy_types(self.get_data_hierarchy_models())
    model = ConfigModel(_id=self.config_model_id, parallel_uploads_count=3,
                        dataverse_login_info={'server_url': '', 'api_token': '', 'dataverse_id': ''},
                        project_upload_items={data_type: True for data_type in data_hierarchy_types})
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, 'dataset-create-new-all-default-fields.json'), encoding='utf-8') as config_file:
      model.metadata = load(config_file)
    set_template_values(self.logger, model.metadata or {})
    set_authors(self.logger, model.metadata or {})
    self.create_model(model)
