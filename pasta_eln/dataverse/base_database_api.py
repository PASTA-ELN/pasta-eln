#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: base_database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from json import load
from os.path import exists, join
from pathlib import Path
from typing import Any

from cloudant import couchdb
from cloudant.design_document import DesignDocument
from cloudant.document import Document
from cloudant.view import View

from pasta_eln.dataverse.database_error import DatabaseError


class BaseDatabaseAPI:
  def __init__(self):
    super().__init__()
    self.password = None
    self.username = None
    self.host = 'localhost'
    self.port = 5984
    self.url = f'http://{self.host}:{self.port}'
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    config_file_name = join(Path.home(), '.pastaELN.json')
    if not exists(config_file_name):
      self.log_and_raise_error("Config file not found, Corrupt installation!")
    with open(config_file_name, 'r', encoding='utf-8') as confFile:
      config = load(confFile)
      if 'defaultProjectGroup' in config:
        self.db_name = config['defaultProjectGroup']
      else:
        self.log_and_raise_error("Incorrect config file, defaultProjectGroup not found!")
      self.set_username_password(config)

  def set_username_password(self, config: dict[str, Any]):
    """
    Sets the username and password based on the provided config.

    Args:
        config (dict[str, Any]): The configuration dictionary.

    Raises:
        DatabaseError: If the config file or required fields are not found.

    Returns:
        None

    """
    project_groups = config.get('projectGroups')
    if not project_groups:
      self.log_and_raise_error(
        "Incorrect config file, projectGroups not found!")
    main_group = project_groups.get(self.db_name)
    if not main_group:
      self.log_and_raise_error(
        "Incorrect config file, defaultProjectGroup not found!")
    local_info = main_group.get('local')
    if not local_info:
      self.log_and_raise_error(
        "Incorrect config file, user or password not found!")
    self.username = local_info.get('user')
    self.password = local_info.get('password')

  def log_and_raise_error(self, error_message: str):
    """
    Logs an error message and raises a DatabaseError.

    Args:
        error_message (str): The error message to log and raise.

    Raises:
        DatabaseError: Always raised with the provided error message.

    Returns:
        None

    """
    self.logger.error(error_message)
    raise DatabaseError(error_message)

  def create_document(self, data: dict[str, Any]) -> Document:
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      return pasta_db.create_document(data, throw_on_exists=True)

  def get_document(self, document_id: str) -> Document:
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      return pasta_db[document_id]

  def update_document(self, data: dict[str, Any]) -> None:
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
               design_document_name,
               view_name,
               map_func,
               reduce_func=None):
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        design_doc.add_view(view_name, map_func, reduce_func)

  def get_view_results(self,
                       design_document_name,
                       view_name,
                       map_func=None,
                       reduce_func=None):
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      results = []
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        view = View(design_doc, view_name, map_func, reduce_func)
        results.extend(result['value'] for result in view.result)
        return results

  def get_view_results_by_id(self,
                             design_document_name,
                             view_name,
                             id,
                             map_func=None,
                             reduce_func=None):
    with couchdb(self.username,
                 self.password,
                 url=self.url,
                 connect=True) as client:
      pasta_db = client[self.db_name]
      with DesignDocument(pasta_db, design_document_name) as design_doc:
        view = View(design_doc, view_name, map_func, reduce_func)
        return view.result[id][0]['value']
