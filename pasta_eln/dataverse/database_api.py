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

from cloudant.document import Document

from pasta_eln.dataverse.base_database_api import BaseDatabaseAPI
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel


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
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.db_api = BaseDatabaseAPI()
    self.design_doc_name = '_design/viewDataverse'
    self.config_doc_id = '-dataverseConfig-'
    self.data_hierarchy_doc_id = '-dataHierarchy-'
    self.upload_model_view_name = "dvUploadView"
    self.project_model_view_name = "dvProjectsView"

  def create_dataverse_design_document(self) -> Document:
    """
    Creates a design document for the dataverse in the database.

    Explanation:
        This method creates a design document for the dataverse in the database
        using the provided design document name.

    Args:
        self: The DatabaseAPI instance.

    Returns:
        Document: The created design document.

    """
    self.logger.info("Creating design document: %s", self.design_doc_name)
    return self.db_api.create_document({"_id": self.design_doc_name})

  def create_upload_model_view(self) -> None:
    """
    Creates the dvUploadView as part of the design document.

    Explanation:
        This method creates the dvUploadView as part of the design document, using the provided design document name.

    Args:
        self: The DatabaseAPI instance.

    """
    self.logger.info("Creating dvUploadView as part of design document: %s", self.design_doc_name)
    self.db_api.add_view(self.design_doc_name,
                         self.upload_model_view_name,
                         "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }",
                         None
                         )

  def create_projects_view(self) -> None:
    """
    Creates the dvProjectsView as part of the design document.

    Explanation:
        This method creates the dvProjectsView as part of the design document, using the provided design document name.

    Args:
        self: The DatabaseAPI instance.

    """
    self.logger.info("Creating dvProjectsView as part of design document: %s", self.design_doc_name)
    self.db_api.add_view(self.design_doc_name,
                         self.project_model_view_name,
                         "function (doc) { "
                         "if (doc['-type']=='x0') {"
                         "emit(doc._id, {"
                         "'name': doc['-name'], "
                         "'_id': doc._id, "
                         "'_rev': doc._rev, "
                         "'objective': doc.objective, "
                         "'status': doc.status, "
                         "'comment': doc.comment, "
                         "'user': doc['-user'], "
                         "'date': doc['-date']});"
                         "}}",
                         None
                         )

  def create_model_document(self,
                            data: UploadModel | ConfigModel | ProjectModel) -> Union[
    UploadModel, ConfigModel, ProjectModel]:

    """
    Creates a model document in the database.

    Explanation:
        This method creates a model document in the database using the provided data.
        It removes the '_id' and '_rev' fields from the data dictionary before creating the document.

    Args:
        self: The DatabaseAPI instance.
        data (UploadModel | ConfigModel | ProjectModel): The data to be stored in the model document.

    Raises:
        ValueError: If the data parameter is None.

    Returns:
        Union[UploadModel, ConfigModel, ProjectModel]: The created model document.

    """
    self.logger.info("Creating model document: %s", data)
    if data is None:
      self.log_and_raise_error(ValueError, "Data cannot be None!")
    if not isinstance(data, (UploadModel, ConfigModel, ProjectModel)):
      self.log_and_raise_error(TypeError, "Data must be an UploadModel, ConfigModel, or ProjectModel!")
    data_dict = dict(data)
    if data_dict['_id'] is None:
      del data_dict['_id']
    del data_dict['_rev']
    return type(data)(**self.db_api.create_document(data_dict))

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
      self.log_and_raise_error(ValueError, "Data cannot be None!")
    if not isinstance(data, (UploadModel, ConfigModel, ProjectModel)):
      self.log_and_raise_error(TypeError, "Data must be an UploadModel, ConfigModel, or ProjectModel!")
    self.db_api.update_document(dict(data))

  def log_and_raise_error(self, exception_type: Type[Exception], error_message: str) -> None:
    """
    Logs an error message and raises an exception of the specified type.

    Explanation:
        This method logs the provided error message using the logger and raises an exception of the specified type with the same message.

    Args:
        self: The DatabaseAPI instance.
        exception_type (Type[Exception]): The type of exception to be raised.
        error_message (str): The error message to be logged and raised.

    Raises:
        Raises the exception of the specified type with the provided error message.
    """
    self.logger.error(error_message)
    match exception_type():
      case ValueError():
        raise ValueError(error_message)
      case TypeError():
        raise TypeError(error_message)

  def get_models(self, model_type: Type[Union[UploadModel, ConfigModel, ProjectModel]]) -> list[Union
  [UploadModel, ConfigModel, ProjectModel]]:
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
                self.db_api.get_view_results(self.design_doc_name, "dvUploadView")]
      case ProjectModel():
        return [ProjectModel(**result) for result in
                self.db_api.get_view_results(self.design_doc_name, "dvProjectsView")]
      case _:
        raise self.log_and_raise_error(TypeError,
                                       f"Unsupported model type {model_type}")  # type: ignore[func-returns-value]

  def get_model(self, model_id: str,
                model_type: Type[UploadModel | ConfigModel | ProjectModel]) -> Union[
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
      raise self.log_and_raise_error(TypeError,
                                     f"Unsupported model type {model_type}")  # type: ignore[func-returns-value]
    elif model_id is None:
      raise self.log_and_raise_error(ValueError, "model_id cannot be None")
    else:
      return model_type(**self.db_api.get_document(model_id))

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
    document = self.db_api.get_document(self.data_hierarchy_doc_id)
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
    if self.db_api.get_document(self.design_doc_name) is None:
      self.create_dataverse_design_document()
    if self.db_api.get_view(self.design_doc_name, self.upload_model_view_name) is None:
      self.create_upload_model_view()
    if self.db_api.get_view(self.design_doc_name, self.project_model_view_name) is None:
      self.create_projects_view()
    if self.db_api.get_document(self.design_doc_name) is None:
      self.initialize_config_document()

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
    model = ConfigModel(_id=self.config_doc_id,
                        parallel_uploads_count=3,
                        dataverse_login_info={},
                        project_upload_items={})
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, "dataset-create-new-all-default-fields.json"),
              encoding="utf-8") as config_file:
      model.metadata = load(config_file)
    self.create_model_document(model)
