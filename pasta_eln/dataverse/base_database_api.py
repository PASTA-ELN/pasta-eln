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
    self.host = 'localhost'
    self.port = 5984
    self.url = f'http://{self.host}:{self.port}'
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    config_file_name = Path.home() / '.pastaELN.json'
    if not config_file_name.exists():
      self.logger.error("Config file not found!")
      raise DatabaseError("Config file not found!")
    with open(config_file_name, 'r', encoding='utf-8') as confFile:
      config = load(confFile)
      if 'defaultProjectGroup' in config:
        self.db_name = config['defaultProjectGroup']
      else:
        self.logger.error("Incorrect config file, defaultProjectGroup not found!")
        raise DatabaseError("Incorrect config file, defaultProjectGroup not found!")
      self.username = config['projectGroups'][config['defaultProjectGroup']]['local']['user']
      self.password = config['projectGroups'][config['defaultProjectGroup']]['local']['password']

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
