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
from threading import Lock
from typing import Any

from cloudant import couchdb
from cloudant.design_document import DesignDocument
from cloudant.document import Document
from cloudant.error import CloudantDatabaseException
from cloudant.query import Query
from cloudant.result import Result
from cloudant.view import View

from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.utils import log_and_create_error, read_pasta_config_file


class BaseDatabaseAPI:
  """
  Provides an interface to interact with a database.

  Explanation:
      This class encapsulates the functionality to interact with a database, including creating, retrieving, and updating documents,
      adding views to design documents, and getting view results.

  """

  def __init__(self) -> None:
    """
    Initializes the BaseDatabaseAPI instance.

    Explanation:
        This method initializes the BaseDatabaseAPI instance by setting up the necessary attributes and loading the configuration file.

    Args:
        None

    Raises:
        DatabaseError: If the config file or required fields are not found.

    Returns:
        None
    """
    super().__init__()
    self.password = None
    self.username = None
    self.host = 'localhost'
    self.port = 5984
    self.url = f'http://{self.host}:{self.port}'
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    config = read_pasta_config_file(self.logger)
    if 'defaultProjectGroup' in config:
      self.db_name = config['defaultProjectGroup']
    else:
      raise log_and_create_error(self.logger, ConfigError, "Incorrect config file, defaultProjectGroup not found!")
    self.set_username_password(config)
    self.update_lock = Lock()

  def set_username_password(self, config: dict[str, Any]) -> None:
    """
    Sets the username and password based on the provided config.

    Args:
        config (dict[str, Any]): The configuration dictionary.

    Raises:
        DatabaseError: If the config file or required fields are not found.

    """
    project_groups = config.get('projectGroups')
    if not project_groups:
      raise log_and_create_error(self.logger, ConfigError,
                                 "Incorrect config file, projectGroups not found!")
    main_group = project_groups.get(self.db_name)
    if not main_group:
      raise log_and_create_error(self.logger, ConfigError,
                                 "Incorrect config file, defaultProjectGroup not found!")
    local_info = main_group.get('local')
    if not local_info:
      raise log_and_create_error(self.logger, ConfigError,
                                 "Incorrect config file, user or password not found!")
    self.username = local_info.get('user')
    self.password = local_info.get('password')

  def create_document(self, data: dict[str, Any]) -> Document:
    """
    Creates a document in the database with the provided data.

    Args:
        data (dict[str, Any]): The data to be stored in the document.

    Returns:
        Document: The created document.

    """
    self.logger.info("Creating document with data: %s", data)
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      document = None
      try:
        document = pasta_db.create_document(data, throw_on_exists=True)
      except CloudantDatabaseException as e:
        self.logger.error("Error creating document: %s", e)
      return document

  def get_document(self, document_id: str) -> Document:
    """
    Retrieves a document from the database based on the provided document ID.

    Args:
        document_id (str): The ID of the document to retrieve.

    Returns:
        Document: The retrieved document.

    Raises:
        DatabaseError: If the document ID is empty or if an error occurs during retrieval.

    """
    self.logger.info("Retrieving document with id: %s", document_id)
    if not document_id:
      raise log_and_create_error(self.logger, DatabaseError, "Document ID cannot be empty!")
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      document = None
      try:
        document = pasta_db[document_id]
      except KeyError as e:
        self.logger.error("Error retrieving document: %s", e)
      return document

  def update_document(self, data: dict[str, Any]) -> None:
    """
    Updates a document in the database with the provided data.
    Make sure to use the `_id` and `_rev` keys in the data to identify the document to update otherwise a new document will be created.

    Args:
        data (dict[str, Any]): The data to update the document with.

    """
    self.logger.info("Updating document with data: %s", data)
    with self.update_lock:
      with couchdb(self.username,
                   self.password,
                   url=self.url,
                   connect=True) as client:
        pasta_db = client[self.db_name]
        with Document(pasta_db, data['_id']) as document:
          for key, value in data.items():
            if key not in ['_id', '_rev']:
              document[key] = value

  def add_view(self,
               design_document_name: str,
               view_name: str,
               map_func: str,
               reduce_func: str | None = None) -> None:
    """
    Adds a view to the specified design document in the database.

    Args:
        design_document_name (str): The name of the design document.
        view_name (str): The name of the view.
        map_func (str): The map function for the view.
        reduce_func (str, optional): The reduce function for the view. Defaults to None.

    Raises:
        ValueError: If design_document_name, view_name, or map_func is None.

    Examples:
        # Add a view with a map function
        add_view("my_design_doc", "my_view", "function(doc) { emit(doc._id, 1); }")

        # Add a view with a map and reduce function
        add_view("my_design_doc", "my_view", "function(doc) { emit(doc.name, doc.age); }", "_count")
    """
    self.logger.info("Adding view: %s to design document: %s, map_func: %s, reduce_func: %s",
                     view_name,
                     design_document_name,
                     map_func,
                     reduce_func)
    if design_document_name is None or view_name is None or map_func is None:
      raise log_and_create_error(self.logger, DatabaseError,
                                 "Design document name, view name, and map function cannot be empty!")
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        design_doc.add_view(view_name, map_func, reduce_func)

  def get_view(self,
               design_document_name: str,
               view_name: str) -> View:
    """
    Retrieves a view from the design document.

    Explanation:
        This method retrieves a view from the specified design document.
        It connects to the CouchDB instance, selects the appropriate database,
        and retrieves the view from the design document.

    Args:
        self: The DatabaseAPI instance.
        design_document_name (str): The name of the design document.
        view_name (str): The name of the view.

    Raises:
        ValueError: If the design document name or view name is empty.

    Returns:
        View: The retrieved view.
    """
    self.logger.info("Retrieving view: %s from design document: %s",
                     view_name,
                     design_document_name)
    if design_document_name is None or view_name is None:
      raise log_and_create_error(self.logger, DatabaseError, "Design document name, view name cannot be empty!")
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        return design_doc.get_view(view_name)

  def get_view_results(self,
                       design_document_name: str,
                       view_name: str,
                       map_func: str | None = None,
                       reduce_func: str | None = None) -> list[dict[str, Any]]:
    """
    Gets the results of a view from the specified design document in the database.

    Args:
        design_document_name (str): The name of the design document.
        view_name (str): The name of the view.
        map_func (str, optional): The map function for the view. Defaults to None.
        reduce_func (str, optional): The reduce function for the view. Defaults to None.

    Raises:
        ValueError: If design_document_name or view_name is None.

    Returns:
        list[dict[str, Any]]: The results of the view as a list of dictionaries.

    Examples:
        # Get results from a view without map and reduce functions
        results = get_view_results("my_design_doc", "my_view")

        # Get results from a view with map and reduce functions
        results = get_view_results("my_design_doc", "my_view", "function(doc) { emit(doc._id, 1); }", "_count")
    """
    self.logger.info("Getting view results: %s from design document: %s, map_func: %s, reduce_func: %s",
                     view_name,
                     design_document_name,
                     map_func,
                     reduce_func)
    if design_document_name is None or view_name is None:
      raise log_and_create_error(self.logger, DatabaseError, "Design document name and view name cannot be empty!")
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      results: list[dict[str, Any]] = []
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        view = View(design_doc, view_name, map_func, reduce_func)
        results.extend(result['value'] for result in view.result)
        return results

  def get_paginated_view_results(self,
                                 design_document_name: str,
                                 view_name: str,
                                 limit: int = 10,
                                 start_key: int | None = None,
                                 start_key_doc_id: str | None = None) -> list[dict[str, Any]]:
    """
    Retrieves paginated view results.

    Args:
        self: The instance of the class.
        design_document_name (str): The name of the design document.
        view_name (str): The name of the view.
        limit (int, optional): The maximum number of results to retrieve. Defaults to 10.
        start_key (int | None, optional): The starting key for pagination. Defaults to None.
        start_key_doc_id (str | None, optional): The starting key document ID for pagination. Defaults to None.

    Raises:
        DatabaseError: If design_document_name or view_name is None.

    Returns:
        list[dict[str, Any]]: The paginated view results.
    """
    self.logger.info(
      "Retrieving paginated view results, View: %s from design document: %s, limit: %s, start_key_doc_id: %s, start_key: %s",
      view_name,
      design_document_name,
      limit,
      start_key_doc_id,
      start_key)
    params: dict[str, Any] = {
      "limit": limit,
      "descending": True,
    }
    if start_key_doc_id:
      params["startkey_docid"] = start_key_doc_id
    if start_key:
      params["startkey"] = start_key
    if design_document_name is None or view_name is None:
      raise log_and_create_error(self.logger, DatabaseError, "Design document name and view name cannot be empty!")
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        result = Result(
          design_doc.get_view(view_name),
          **params
        )
        return result[:limit]

  def create_query_index(self,
                         index_name: str,
                         index_type: str = "json",
                         fields: list[dict[str, str]] | list[str] | None = None) -> None:
    """
    Creates a query index in database with the specified name, type, and fields.

    Args:
        index_name (str): The name of the index to be created.
        index_type (str, optional): The type of the index. Defaults to "json".
        fields (list[dict[str, str]] | list[str] | None, optional): The fields to be included in the index. Defaults to None.

    Raises:
        DatabaseError: If index_name or fields are None.

    Examples:
        create_query_index("index1", "json", [{"name": "field1", "type": "asc"}])
    """

    self.logger.info("Creating query index, name: %s, index_type: %s, fields: %s",
                     index_name,
                     index_type,
                     fields)
    if index_name is None or fields is None:
      raise log_and_create_error(self.logger, DatabaseError,
                                 "Index name and fields cannot be empty!")
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      if index_name in [index.name for index in pasta_db.get_query_indexes()]:
        self.logger.warning("Index already exists: %s", index_name)
        return
      pasta_db.create_query_index(index_name=index_name,
                                  index_type=index_type,
                                  fields=fields)

  def get_paginated_upload_model_query_results(self,
                                               filter_term: str | None = None,
                                               filter_fields: list[str] | None = None,
                                               bookmark: str | None = None,
                                               limit: int = 10) -> dict[str, Any]:
    """
    Gets paginated upload model query results based on the provided filter criteria.

    Args:
        filter_term (str | None, optional): The filter term to search for. Defaults to None.
        filter_fields (list[str] | None, optional): The list of fields to apply the filter on. Defaults to None.
        bookmark (str | None, optional): The bookmark for pagination. Defaults to None.
        limit (int, optional): The maximum number of results to retrieve. Defaults to 10.

    Returns:
        dict[str, Any]: A dictionary containing the paginated query results. Contains the following keys: bookmark, docs. docs is a list of dictionaries representing the retrieved documents.

    Raises:
        DatabaseError: If filter_term or filter_fields is None.

    Examples:
        get_paginated_upload_model_query_results(filter_term="test", filter_fields=["project_name", "dataverse_url"])

    Raises:
        No specific exceptions are raised by this function.
    """

    self.logger.info(
      "Getting paginated upload model query results: filter_term: %s, filter_fields: %s, bookmark: %s, limit: %s",
      filter_term,
      ",".join(filter_fields) if filter_fields else None,
      bookmark,
      limit)
    selector: dict[str, Any] = {"data_type": "dataverse_upload"}
    if filter_term and filter_fields:
      filter_criteria = {"$or": [{field: {"$regex": f"(?i).*{filter_term}.*"}} for field in filter_fields]}
      selector = {
        "$and": [selector, filter_criteria]
      }
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      query = Query(pasta_db,
                    selector=selector,
                    sort=[{
                      "finished_date_time": "desc"
                    }],
                    limit=limit)
      return query(bookmark=bookmark) if bookmark else query()

  def get_view_results_by_id(self,
                             design_document_name: str,
                             view_name: str,
                             document_id: str,
                             map_func: str | None = None,
                             reduce_func: str | None = None) -> Document | None:
    """
    Gets the result of a view for a specific document ID from the specified design document in the database.

    Args:
        design_document_name (str): The name of the design document.
        view_name (str): The name of the view.
        document_id (str): The ID of the document.
        map_func (str | None, optional): The map function for the view. Defaults to None.
        reduce_func (str | None, optional): The reduce function for the view. Defaults to None.

    Raises:
        ValueError: If design_document_name, view_name, or document_id is None.

    Returns:
        Document | None: The result of the view for the specified document ID, or None if not found.

    Examples:
        # Get the result of a view for a specific document ID
        result = get_view_results_by_id("my_design_doc", "my_view", "my_document_id")

        # Get the result of a view for a specific document ID with map and reduce functions
        result = get_view_results_by_id("my_design_doc", "my_view", "my_document_id", "function(doc) { emit(doc._id, 1); }", "_count")
    """
    self.logger.info("Getting view result: %s for id: %s from design document: %s, map_func: %s, reduce_func: %s",
                     view_name,
                     document_id,
                     design_document_name,
                     map_func,
                     reduce_func)
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      if design_document_name is None or view_name is None or document_id is None:
        raise log_and_create_error(self.logger, DatabaseError,
                                   "Design document name, view name and document id cannot be empty!")
      pasta_db = client[self.db_name]
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        view = View(design_doc, view_name, map_func, reduce_func)
        return view.result[document_id][0]['value']
