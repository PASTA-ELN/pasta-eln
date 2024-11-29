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
from typing import Any, Union

from pasta_eln.GUI.data_hierarchy.base_database_api import BaseDatabaseApi
from pasta_eln.GUI.data_hierarchy.data_hierarchy_document_adapter import DataHierarchyDocumentAdapter
from pasta_eln.database.error import Error
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.dataverse.utils import (get_db_info, log_and_create_error)


class DatabaseAPI:
  """A class for managing database operations related to data hierarchy models.

  This class provides methods to create, retrieve, update, and save data hierarchy
  models in a database. It utilizes logging for tracking operations and ensures
  that the database is correctly initialized and managed.

  Raises:
      Error: If there are issues with database operations or invalid data.
  """

  def __init__(self) -> None:
    """Initializes the database API with configuration settings.

    This constructor sets up the initial configuration for the database API,
    including a logger, a default model ID, and the database path. If the
    database path is not provided, an error is raised to ensure that the
    database API is initialized correctly.

    Raises:
        Error: If the database path is None.
    """
    self.config_model_id: int = 1
    self.logger: logging.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.pasta_db_name: str = "pastaELN"
    db_info: dict[str, str] = get_db_info(self.logger)
    db_path: str | None = db_info.get('database_path')
    if db_path is None:
      raise log_and_create_error(self.logger, Error, "Database path is None!")
    self.db_api: BaseDatabaseApi = BaseDatabaseApi(f"{db_path}/{self.pasta_db_name}.db")

  def create_data_hierarchy_model(self, data: Union[DataHierarchyModel]) -> DataHierarchyModel:
    """Creates a new DataHierarchyModel in the database.

    This method logs the creation process and validates the provided data.
    If the data is None or not an instance of DataHierarchyModel, an error is raised.
    If valid, the data model is inserted into the database using the database API.

    Args:
        data (Union[DataHierarchyModel]): The DataHierarchyModel instance to be created.

    Returns:
        DataHierarchyModel: The created DataHierarchyModel instance.

    Raises:
        ValueError: If the provided data is None.
        TypeError: If the provided data is not an instance of DataHierarchyModel.
    """
    self.logger.info("Creating data_hierarchy_model: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, DataHierarchyModel):
      raise log_and_create_error(self.logger, TypeError, "Data must be DataHierarchyModel!")
    return self.db_api.insert_data_hierarchy_model(data)

  def update_data_hierarchy_models(self, data_models: list[DataHierarchyModel]) -> None:
    """Updates a list of DataHierarchyModel instances.

    This method logs the update process and iterates through each DataHierarchyModel
    in the provided list, calling the update method for each model. It ensures that
    all specified models are processed for updates.

    Args:
        data_models (list[DataHierarchyModel]): A list of DataHierarchyModel instances to be updated.
    """
    self.logger.info("Updating data hierarchy models...")
    for data_model in data_models:
      self.update_data_hierarchy_model(data_model)

  def update_data_hierarchy_model(self, data: DataHierarchyModel) -> None:
    """Updates an existing DataHierarchyModel instance.

    This method logs the update process and validates the provided data model.
    If the data is None or not an instance of DataHierarchyModel, an error is raised.
    If valid, the data model is passed to the database API for updating.

    Args:
        data (DataHierarchyModel): The DataHierarchyModel instance to be updated.

    Raises:
        ValueError: If the provided data is None.
        TypeError: If the provided data is not an instance of DataHierarchyModel.
    """
    self.logger.info("Updating data_hierarchy_model: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, DataHierarchyModel):
      raise log_and_create_error(self.logger, TypeError, "Data must be an DataHierarchyModel!")
    self.db_api.update_data_hierarchy_model(data)

  def get_data_hierarchy_models(self) -> list[DataHierarchyModel]:
    """Retrieves all DataHierarchyModel instances from the database.

    This method logs the retrieval process and queries the database for all
    DataHierarchyModel entries. It returns a list of the retrieved models for further use.

    Returns:
        list[DataHierarchyModel]: A list of DataHierarchyModel instances retrieved from the database.
    """
    self.logger.info("Retrieving data_hierarchy_models")
    return self.db_api.get_data_hierarchy_models()

  def get_data_hierarchy_model(self, model_doc_type: str) -> DataHierarchyModel | None:
    """Retrieves a DataHierarchyModel based on the provided document type.

    This method logs the retrieval process and checks if the provided document type
    is valid. If the document type is None, an error is raised. It then queries the
    database to retrieve the corresponding DataHierarchyModel.

    Args:
        model_doc_type (str): The document type of the DataHierarchyModel to retrieve.

    Returns:
        DataHierarchyModel | None: The corresponding DataHierarchyModel instance if found.

    Raises:
        ValueError: If the model_doc_type is None.
    """
    self.logger.info("Retrieving data_hierarchy_model with id: %s", model_doc_type)
    if model_doc_type is None:
      raise log_and_create_error(self.logger, ValueError, "model_id cannot be None")
    return self.db_api.get_data_hierarchy_model(model_doc_type)

  def initialize_database(self) -> None:
    """Initializes the database for the data-hierarchy module.

    This method logs the initialization process and calls the database API to create
    and bind the necessary database tables. It ensures that the database is set up
    correctly for further operations within the data-hierarchy module.
    """
    self.logger.info("Initializing database for data-hierarchy module...")
    self.db_api.create_and_bind_db_tables()

  def get_data_hierarchy_document(self) -> dict[str, Any]:
    """Retrieves the data hierarchy document as a dictionary.

    This method logs the retrieval process and collects data hierarchy models from
    the database. It then converts each model into a dictionary format using the
    DataHierarchyDocumentAdapter and combines them into a single document.

    Returns:
        dict[str, Any]: A dictionary representation of the data hierarchy document.

    Raises:
        Error: If there is an issue retrieving the data hierarchy models or converting them.
    """
    self.logger.info("Retrieving data hierarchy document...")
    data_hierarchy_models = self.get_data_hierarchy_models()
    dh_document: dict[str, Any] = {}
    for model in data_hierarchy_models:
      dh_document |= DataHierarchyDocumentAdapter.to_data_hierarchy_document(model)
    return dh_document

  def save_data_hierarchy_document(self, data_hierarchy_document: dict[str, Any]) -> None:
    """Saves a data hierarchy document by updating or creating models.

    This method converts the provided data hierarchy document into a list of
    DataHierarchyModel instances. It checks if each model already exists in the
    database; if it does, the model is updated, otherwise, a new model is created.

    Args:
        data_hierarchy_document (dict[str, Any]): A dictionary representation of the data hierarchy document.
    """
    models = DataHierarchyDocumentAdapter.to_data_hierarchy_model_list(data_hierarchy_document)
    for model in models:
      if self.db_api.check_if_data_hierarchy_model_exists(model.doc_type or ""):
        self.update_data_hierarchy_model(model)
      else:
        self.create_data_hierarchy_model(model)
