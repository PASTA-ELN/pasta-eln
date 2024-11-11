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
from json import load
from os import getcwd
from os.path import dirname, join, realpath
from typing import Any, Type, Union

from pasta_eln.dataverse.base_database_api import BaseDatabaseApi
from pasta_eln.dataverse.config_model import ConfigModel
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
    """
    Initializes the DatabaseAPI instance.

    Explanation:
        This method initializes the DatabaseAPI instance
        by setting up the necessary attributes and creating an instance of BaseDatabaseAPI.

    Args:
        None

    Returns:
        None
    """
    super().__init__()
    self.logger: logging.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.dataverse_db_name: str = "dataverse"
    db_info: dict[str, str] = get_db_info(self.logger)
    self.db_api: BaseDatabaseApi = BaseDatabaseApi(
      f"{db_info.get('database_path')}/{self.dataverse_db_name}.db",
      #f"{db_info.get('database_path')}/{db_info.get('database_name')}.db",
      f"{db_info.get('database_path')}/pastaELN.db"
    )
    # self.design_doc_name: str = '_design/viewDataverse'
    # self.config_doc_id: str = '-dataverseConfig-'
    # self.data_hierarchy_doc_id: str = '-dataHierarchy-'
    # self.upload_model_view_name: str = 'dvUploadView'
    # self.project_model_view_name: str = 'dvProjectsView'
    # self.upload_models_query_index_name: str = "uploadModelsQuery"
    # self.upload_models_query_index_fields: list[str] = ["finished_date_time"]
    _, self.encrypt_key = get_encrypt_key(self.logger)

  # def create_dataverse_design_document(self, db_name: str) -> Document:
  #   """
  #   Creates a design document for the dataverse in the database.
  #
  #   Explanation:
  #       This method creates a design document for the dataverse in the database
  #       using the provided design document name.
  #
  #   Args:
  #       db_name (str): The name of the database.
  #       self: The DatabaseAPI instance.
  #
  #   Returns:
  #       Document: The created design document.
  #
  #   """
  #   self.logger.info("Creating design document: %s", self.design_doc_name)
  #   return self.db_api.create_document({"_id": self.design_doc_name}, db_name)

  # def create_upload_model_view(self) -> None:
  #   """
  #   Creates the dvUploadView as part of the design document.
  #
  #   Explanation:
  #       This method creates the dvUploadView as part of the design document, using the provided design document name.
  #
  #   Args:
  #       self: The DatabaseAPI instance.
  #
  #   """
  #   self.logger.info("Creating dvUploadView as part of design document: %s", self.design_doc_name)
  #   self.db_api.add_view(self.dataverse_db_name,
  #                        self.design_doc_name,
  #                        self.upload_model_view_name,
  #                        "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }", None)

  # def create_projects_view(self) -> None:
  #   """
  #   Creates the dvProjectsView as part of the design document.
  #
  #   Explanation:
  #       This method creates the dvProjectsView as part of the design document, using the provided design document name.
  #
  #   Args:
  #       self: The DatabaseAPI instance.
  #
  #   """
  #   self.logger.info("Creating dvProjectsView as part of design document: %s", self.design_doc_name)
  #   self.db_api.add_view(self.default_project_group_db_name,
  #                        self.design_doc_name,
  #                        self.project_model_view_name,
  #                        "function (doc) { "
  #                        "if (doc['-type'].includes('x0')) {"
  #                        "emit(doc._id, {"
  #                        "'name': doc['-name'], "
  #                        "'_id': doc._id, "
  #                        "'_rev': doc._rev, "
  #                        "'objective': doc.objective, "
  #                        "'status': doc.status, "
  #                        "'comment': doc.comment, "
  #                        "'user': doc['-user'], "
  #                        "'date': doc['-date']});"
  #                        "}}",
  #                        None
  #                        )

  def create_model(self, data: Union[UploadModel, ConfigModel]) -> Union[
    UploadModel, ConfigModel]:
    self.logger.info("Creating model: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, (UploadModel, ConfigModel)):
      raise log_and_create_error(self.logger, TypeError, "Data must be an UploadModel or ConfigModel!")
    return self.db_api.insert_model(data)

  def update_model_document(self, data: UploadModel | ConfigModel | ProjectModel) -> None:
    """
    Updates the model document with the provided data.

    Explanation:
        This method updates the model document with the provided data. It logs the update operation and performs necessary validations.

    Args:
        self: The DatabaseAPI instance.
        data (UploadModel | ConfigModel | ProjectModel): The data to update the model document with.

    Raises:
        ValueError: If the data parameter is None.
        TypeError: If the data parameter is not an instance of UploadModel, ConfigModel, or ProjectModel.

    """
    self.logger.info("Updating model document: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, (UploadModel, ConfigModel, ProjectModel)):
      raise log_and_create_error(self.logger, TypeError, "Data must be an UploadModel, ConfigModel, or ProjectModel!")
    self.db_api.update_document(dict(data), self.dataverse_db_name)

  def get_models(self, model_type: Type[Union[UploadModel, ConfigModel, ProjectModel]]) -> list[
    Union[UploadModel, ConfigModel, ProjectModel]]:
    """
    Retrieves models of the specified type from the database.

    Explanation:
        This method retrieves models of the specified type from the database using the appropriate view.

    Args:
        self: The DatabaseAPI instance.
        model_type (Type[Union[UploadModel, ConfigModel, ProjectModel]]): The type of models to retrieve.

    Raises:
        ValueError: If the model_type is not supported.

    Returns:
        list[Union[UploadModel, ConfigModel, ProjectModel]]: The retrieved models.
    """
    self.logger.info("Getting models of type: %s", model_type)
    match model_type():
      case UploadModel():
        return [UploadModel(**result) for result in
                self.db_api.get_view_results(self.dataverse_db_name,
                                             self.design_doc_name,
                                             "dvUploadView")]
      case ProjectModel():
        return [ProjectModel(**result) for result in
                self.db_api.get_view_results(self.default_project_group_db_name,
                                             self.design_doc_name,
                                             "dvProjectsView")]
      case _:
        raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")

  def get_paginated_models(self,
                           model_type: Type[Union[UploadModel, ProjectModel]],
                           filter_term: str | None = None,
                           bookmark: str | None = None,
                           limit: int = 10) -> dict[str, str | list[UploadModel]] | dict[str, str | list[ProjectModel]]:
    """
    Gets paginated models of the specified type based on the provided filter criteria.

    Args:
        model_type (Type[Union[UploadModel, ProjectModel]]): The type of model to retrieve.
        filter_term (str | None, optional): The filter term to search for. Defaults to None.
        Filter term is applied on following filter fields:  ["project_name", "dataverse_url", "finished_date_time", "status"]
        bookmark (str | None, optional): The bookmark for pagination. Defaults to None.
        limit (int, optional): The maximum number of results to retrieve. Defaults to 10.

    Returns:
        dict[str, str | list[UploadModel]] | dict[str, str | list[ProjectModel]]: A dictionary containing the paginated models or an error message.

    Raises:
        TypeError: If an unsupported model type is provided.
    """

    self.logger.info("Getting paginated models of type: %s, filter_term: %s, bookmark: %s, limit: %s",
                     model_type,
                     filter_term,
                     bookmark,
                     limit)
    match model_type():
      case UploadModel():
        result = self.db_api.get_paginated_upload_model_query_results(self.dataverse_db_name,
                                                                      filter_term,
                                                                      ["project_name",
                                                                       "dataverse_url",
                                                                       "finished_date_time",
                                                                       "status"],
                                                                      bookmark,
                                                                      limit)
        return {
          "bookmark": result["bookmark"],
          "models": [UploadModel(**doc) for doc in result["docs"]]
        }
      case _:
        raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")

  def get_model(self, model_id: str, model_type: Type[UploadModel | ConfigModel | ProjectModel]) -> Union[
    UploadModel, ProjectModel, ConfigModel]:
    """
    Retrieves a model from the database.

    Explanation:
        This method retrieves a model from the database based on the given model_id and model_type.
        It performs the necessary validation and returns the corresponding model instance.

    Args:
        model_id (str): The ID of the model to retrieve.
        model_type (Type[UploadModel | ConfigModel | ProjectModel]): The type of the model to retrieve.

    Returns:
        Union[UploadModel, ProjectModel, ConfigModel, None]: The retrieved model instance.

    Raises:
        TypeError: If the model_type is not one of the supported types.
        ValueError: If the model_id is None.
    """
    self.logger.info("Getting model with id: %s, type: %s", model_id, model_type)
    if model_type not in (UploadModel, ProjectModel, ConfigModel):
      raise log_and_create_error(self.logger, TypeError, f"Unsupported model type {model_type}")
    if model_id is None:
      raise log_and_create_error(self.logger, ValueError, "model_id cannot be None")
    return model_type(**self.db_api.get_document(model_id,
                                                 self.default_project_group_db_name
                                                 if model_type is ProjectModel
                                                 else self.dataverse_db_name))

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
    self.logger.info("Getting config model...")
    config_model = self.get_model(self.config_doc_id, ConfigModel)
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
      self.update_model_document(config_model)
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
    self.update_model_document(config_model)

  def get_data_hierarchy(self) -> dict[str, Any] | None:
    """
    Retrieves the data hierarchy from the database.

    Explanation:
        This method retrieves the data hierarchy from the database using the appropriate document ID.
        It performs the necessary validations and returns the retrieved data hierarchy.

    Args:
        self: The DatabaseAPI instance.

    Returns:
        dict[str, Any] | None: The retrieved data hierarchy, or None if the document is not found.
    """
    self.logger.info("Getting data hierarchy...")
    document = self.db_api.get_document(self.data_hierarchy_doc_id, self.default_project_group_db_name)
    if document is None:
      self.logger.warning("Data hierarchy document not found!")
      return document
    data = dict(document)
    del data['_id']
    del data['_rev']
    del data['-version']
    return data

  def initialize_database(self) -> None:
    """
    Initializes the database for the dataverse module.

    Explanation:
        This method initializes the database for the dataverse module by creating necessary documents and views if they do not exist.

    Args:
        self: The DatabaseAPI instance.

    """
    self.logger.info("Initializing database for dataverse module...")
    self.db_api.create_database(self.dataverse_db_name)
    if self.db_api.get_document(self.design_doc_name, self.default_project_group_db_name) is None:
      self.create_dataverse_design_document(self.default_project_group_db_name)
    if self.db_api.get_document(self.design_doc_name, self.dataverse_db_name) is None:
      self.create_dataverse_design_document(self.dataverse_db_name)
    if self.db_api.get_view(self.dataverse_db_name, self.design_doc_name, self.upload_model_view_name) is None:
      self.create_upload_model_view()
    if self.db_api.get_view(self.default_project_group_db_name, self.design_doc_name,
                            self.project_model_view_name) is None:
      self.create_projects_view()
    if self.db_api.get_document(self.config_doc_id, self.dataverse_db_name) is None:
      self.initialize_config_document()
    self.db_api.create_query_index(self.dataverse_db_name,
                                   self.upload_models_query_index_name,
                                   "json",
                                   self.upload_models_query_index_fields)

  def initialize_config_document(self) -> None:
    """
    Initializes the config document.

    Explanation:
        This method initializes the config document by creating a ConfigModel instance with the provided attributes.
        It loads the metadata from a JSON file and calls the create_model_document method to create the document.

    Args:
        self: The DatabaseAPI instance.

    """
    self.logger.info("Initializing config document...")
    data_hierarchy_types: list[str] = get_data_hierarchy_types(self.get_data_hierarchy())
    model = ConfigModel(_id=self.config_doc_id, parallel_uploads_count=3,
                        dataverse_login_info={"server_url": "", "api_token": "", "dataverse_id": ""},
                        project_upload_items={data_type: True for data_type in data_hierarchy_types})
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, "dataset-create-new-all-default-fields.json"), encoding="utf-8") as config_file:
      model.metadata = load(config_file)
    set_template_values(self.logger, model.metadata or {})
    set_authors(self.logger, model.metadata or {})
    self.create_model_document(model)
