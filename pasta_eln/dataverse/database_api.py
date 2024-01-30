#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from json import load
from os import getcwd
from os.path import dirname, join, realpath
from typing import Any, Type

from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.base_database_api import BaseDatabaseAPI
from pasta_eln.dataverse.project_model import ProjectModel
from pasta_eln.dataverse.upload_model import UploadModel


class DatabaseAPI(object):

  def __init__(self):
    super().__init__()
    self.db_api = BaseDatabaseAPI()
    self.design_doc_name = '_design/viewDataverse'

  def create_dataverse_design_document(self):
    data = {"_id": self.design_doc_name}
    return self.db_api.create_document(data)

  def create_upload_documents_view(self):
    self.db_api.add_view(self.design_doc_name,
                         "dvUploadView",
                         "function (doc) { if (doc.data_type === 'dataverse_upload') { emit(doc._id, doc); } }",
                         None
                         )

  def create_projects_view(self):
    self.db_api.add_view(self.design_doc_name,
                         "dvProjectsView",
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

  def create_model_document(self, data: UploadModel | ConfigModel | ProjectModel):
    data_dict = dict(data)
    if data_dict['_id'] is None:
      del data_dict['_id']
    del data_dict['_rev']
    return type(data)(**self.db_api.create_document(data_dict))

  def update_model_document(self, data: UploadModel | ConfigModel | ProjectModel):
    self.db_api.update_document(dict(data))

  def get_models(self, model_type: Type[UploadModel | ConfigModel | ProjectModel]):
    match model_type():
      case UploadModel():
        return [UploadModel(**result) for result in
                self.db_api.get_view_results(self.design_doc_name, "dvUploadView")]
      case ProjectModel():
        return [ProjectModel(**result) for result in
                self.db_api.get_view_results(self.design_doc_name, "dvProjectsView")]
      case _:
        raise ValueError(f"Unsupported model type {model_type}")

  def get_model(self, model_id: str,
                model_type: Type[UploadModel | ConfigModel | ProjectModel]) -> UploadModel | ProjectModel | ConfigModel:
    if model_type not in (UploadModel, ProjectModel, ConfigModel):
      raise ValueError(f"Unsupported model type {model_type}")
    elif model_id is None:
      raise ValueError("model_id cannot be None")
    else:
      return model_type(**self.db_api.get_document(model_id))

  def get_data_hierarchy(self) -> dict[str, Any]:
    data = dict(self.db_api.get_document("-dataHierarchy-"))
    del data['_id']
    del data['_rev']
    del data['-version']
    return data

  def initialize(self):
    self.create_dataverse_design_document()
    self.create_upload_documents_view()
    self.create_projects_view()
    model = ConfigModel()
    model.id = "-dataverseConfig-"
    model.parallel_uploads_count = 3
    model.dataverse_login_info = {}
    model.project_upload_items = {}
    current_path = realpath(join(getcwd(), dirname(__file__)))
    with open(join(current_path, "dataset-create-new-all-default-fields.json"),
              encoding="utf-8") as config_file:
      model.metadata = load(config_file)
    self.create_model_document(model)
