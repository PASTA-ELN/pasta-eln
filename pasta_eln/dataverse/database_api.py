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
from typing import Type, Union

from pasta_eln.dataverse.base_database_api import BaseDatabaseApi
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.data_hierarchy_model import DataHierarchyModel
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.utils import (decrypt_data,
                                       encrypt_data,
                                       get_data_hierarchy_types,
                                       get_db_info, get_encrypt_key,
                                       log_and_create_error,
                                       set_authors,
                                       set_template_values)


class DatabaseAPI:
  """
  Provides an interface to interact with the database for dataverse specific operations.

  Explanation:
      This class represents the DatabaseAPI and provides methods to interact with the database.
      It includes methods for initializing the database, retrieving models and data, and performing other database operations.
  """

  def __init__(self) -> None:
    super().__init__()
    self.config_model_id: int = 1
    self.logger: logging.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.dataverse_db_name: str = ".pastaELN_dataverse"
    self.pasta_db_name: str = "pastaELN"
    db_info: dict[str, str] = get_db_info(self.logger)
    self.db_api: BaseDatabaseApi = BaseDatabaseApi(
      f"{Path.home()}/{self.dataverse_db_name}.db",
      f"{db_info.get('database_path')}/{self.pasta_db_name}.db"
    )
    _, self.encrypt_key = get_encrypt_key(self.logger)

  def create_model(self, data: Union[UploadModel, ConfigModel]) -> Union[
    UploadModel, ConfigModel]:
    self.logger.info("Creating model: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, (UploadModel, ConfigModel)):
      raise log_and_create_error(self.logger, TypeError, "Data must be an UploadModel or ConfigModel!")
    return self.db_api.insert_model(data)

  def update_model(self, data: UploadModel | ConfigModel) -> None:
    self.logger.info("Updating model document: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, (UploadModel, ConfigModel)):
      raise log_and_create_error(self.logger, TypeError, "Data must be an UploadModel, ConfigModel, or ProjectModel!")
    self.db_api.update_model(data)

  def get_models(self, model_type: Type[UploadModel | ConfigModel | DataHierarchyModel | ProjectModel]) -> list[
    Union[UploadModel, ConfigModel, DataHierarchyModel, ProjectModel]]:
    self.logger.info("Getting models of type: %s", model_type)
    match model_type():
      case UploadModel() | ConfigModel() | DataHierarchyModel():
        return self.db_api.get_models(model_type)  # type: ignore
      case ProjectModel():
        return self.db_api.get_project_models()  # type: ignore
      case _:
        raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")

  def get_paginated_models(self,
                           model_type: Type[Union[UploadModel, ConfigModel, DataHierarchyModel]],
                           filter_term: str | None = None,
                           filter_fields: list[str] | None = None,
                           order_by_column: str | None = None,
                           page_number: int = 1,
                           limit: int = 10) -> list[Type[UploadModel | ConfigModel | DataHierarchyModel]]:

    self.logger.info("Getting paginated models of type: %s, filter_term: %s, bookmark: %s, limit: %s",
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
                           model_type: Type[Union[UploadModel, ConfigModel, DataHierarchyModel]],
                           limit: int = 10) -> int:

    self.logger.info("Retrieving last page number of type: %s, limit: %s", model_type, limit)
    match model_type():
      case UploadModel() | ConfigModel() | DataHierarchyModel():
        row_count = self.db_api.get_models_count(model_type)
        return math.ceil(row_count / limit)
      case _:
        raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")

  def get_model(self, model_id: int | str,
                model_type: Type[UploadModel | ConfigModel | DataHierarchyModel | ProjectModel]) -> Union[
    UploadModel, ConfigModel, DataHierarchyModel, ProjectModel, None]:
    self.logger.info("Getting model with id: %s, type: %s", model_id, model_type)
    if model_type not in (UploadModel, ProjectModel, ConfigModel):
      raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")
    if model_id is None:
      raise log_and_create_error(self.logger, ValueError, "model_id cannot be None")
    return self.db_api.get_model(model_id,
                                 model_type)

  def get_config_model(self) -> ConfigModel | None:
    """
    Retrieves the config model from the database.

    Explanation:
        This method retrieves the config model from the database using the appropriate document ID.
        It performs the necessary validations and returns the retrieved config model.

    Args:
        self: The DatabaseAPI instance.

    Returns:
        ConfigModel: The retrieved config model.dataverse_login_info = {dict: 2} {'api_token': 'encrypted_token', 'dataverse_id': 'some_id'}
    """
    self.logger.info("Retrieving config model...")
    config_model = self.get_model(self.config_model_id, ConfigModel)
    if config_model is None or not isinstance(config_model, ConfigModel):
      self.logger.error("Fatal error, Failed to load config model!")
      return None
    if not isinstance(config_model.dataverse_login_info, dict):
      self.logger.error("Fatal Error, Invalid dataverse login info!")
      return None
    api_token = config_model.dataverse_login_info.get("api_token")
    if self.encrypt_key and api_token:
      config_model.dataverse_login_info["api_token"] = decrypt_data(self.logger, self.encrypt_key, api_token)
    if not self.encrypt_key and api_token:
      self.logger.warning(
        "No encryption key found. Hence if any API key exists, it will be removed and the user needs to re-enter it.")
      config_model.dataverse_login_info["api_token"] = None
      config_model.dataverse_login_info["dataverse_id"] = None
      self.update_model(config_model)
    return config_model

  def save_config_model(self, config_model: ConfigModel) -> None:
    """
    Saves the config model to the database.

    Explanation:
        This method saves the config model to the database using the appropriate document ID.

    Args:
        self: The DatabaseAPI instance.
        config_model (ConfigModel): The config model to save.
    """
    self.logger.info("Saving config model...")
    if (not config_model
        or not isinstance(config_model, ConfigModel)
        or not isinstance(config_model.dataverse_login_info, dict)):
      self.logger.error("Invalid config model!")
      return
    if not self.encrypt_key:
      raise log_and_create_error(self.logger, ValueError,
                                 "Fatal Error, No encryption key found! Make sure to initialize the database!")
    if api_token := config_model.dataverse_login_info["api_token"]:
      config_model.dataverse_login_info["api_token"] = encrypt_data(self.logger, self.encrypt_key, api_token)
    if server_url := config_model.dataverse_login_info["server_url"]:
      config_model.dataverse_login_info["server_url"] = server_url.strip("/").strip("\\")
    self.update_model(config_model)

  def get_data_hierarchy_models(self) -> list[DataHierarchyModel] | None:
    self.logger.info("Getting data hierarchy...")
    results = self.db_api.get_models(DataHierarchyModel)
    if not results:
      self.logger.warning("Data hierarchy items not found!")
      return results  # type: ignore[return-value]
    return results  # type: ignore[return-value]

  def initialize_database(self) -> None:
    self.logger.info("Initializing database for dataverse module...")
    self.db_api.create_and_init_database()
    if self.db_api.get_model(self.config_model_id, ConfigModel) is None:
      self.initialize_config_document()

  def initialize_config_document(self) -> None:
    self.logger.info("Initializing config document...")
    data_hierarchy_types: list[str] = get_data_hierarchy_types(self.get_data_hierarchy_models())
    model = ConfigModel(_id=self.config_model_id, parallel_uploads_count=3,
                        dataverse_login_info={"server_url": "", "api_token": "", "dataverse_id": ""},
                        project_upload_items={data_type: True for data_type in data_hierarchy_types})
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, "dataset-create-new-all-default-fields.json"), encoding="utf-8") as config_file:
      model.metadata = load(config_file)
    set_template_values(self.logger, model.metadata or {})
    set_authors(self.logger, model.metadata or {})
    self.create_model(model)
