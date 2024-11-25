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
  def __init__(self) -> None:
    super().__init__()
    self.config_model_id: int = 1
    self.logger: logging.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.pasta_db_name: str = "pastaELN"
    db_info: dict[str, str] = get_db_info(self.logger)
    db_path: str | None = db_info.get('database_path')
    if db_path is None:
      raise log_and_create_error(self.logger, Error, "Database path is None!")
    self.db_api: BaseDatabaseApi = BaseDatabaseApi(f"{db_path}/{self.pasta_db_name}.db")

  def create_data_hierarchy_model(self, data: Union[DataHierarchyModel]) -> DataHierarchyModel:
    self.logger.info("Creating data_hierarchy_model: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, DataHierarchyModel):
      raise log_and_create_error(self.logger, TypeError, "Data must be DataHierarchyModel!")
    return self.db_api.insert_data_hierarchy_model(data)

  def update_data_hierarchy_models(self, data_models: list[DataHierarchyModel]) -> None:
    self.logger.info("Updating data models")
    for data_model in data_models:
      self.update_data_hierarchy_model(data_model)

  def update_data_hierarchy_model(self, data: DataHierarchyModel) -> None:
    self.logger.info("Updating data_hierarchy_model: %s", data)
    if data is None:
      raise log_and_create_error(self.logger, ValueError, "Data cannot be None!")
    if not isinstance(data, DataHierarchyModel):
      raise log_and_create_error(self.logger, TypeError, "Data must be an DataHierarchyModel!")
    self.db_api.update_data_hierarchy_model(data)

  def get_data_hierarchy_models(self) -> list[DataHierarchyModel]:
    self.logger.info("Retrieving data_hierarchy_models")
    return self.db_api.get_data_hierarchy_models()

  def get_model(self, model_doc_type: str) -> DataHierarchyModel:
    self.logger.info("Retrieving data_hierarchy_model with id: %s", model_doc_type)
    if model_doc_type is None:
      raise log_and_create_error(self.logger, ValueError, "model_id cannot be None")
    return self.db_api.get_data_hierarchy_model(model_doc_type)

  def initialize_database(self) -> None:
    self.logger.info("Initializing database for data-hierarchy module...")
    self.db_api.create_and_bind_db_tables()

  def get_data_hierarchy_document(self) -> dict[str, Any]:
    self.logger.info("Retrieving data hierarchy document...")
    data_hierarchy_models = self.get_data_hierarchy_models()
    dh_document = {}
    for model in data_hierarchy_models:
      dh_document.update(DataHierarchyDocumentAdapter.to_data_hierarchy_document(model))
    return dh_document

  def save_data_hierarchy_document(self, data_hierarchy_document: dict[str, Any]) -> None:
    models = DataHierarchyDocumentAdapter.to_data_hierarchy_model_list(data_hierarchy_document)
    for model in models:
      if self.db_api.check_if_data_hierarchy_model_exists(model.doc_type):
        self.update_data_hierarchy_model(model)
      else:
        self.create_data_hierarchy_model(model)
