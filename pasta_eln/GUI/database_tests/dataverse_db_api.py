#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_db_api.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from pasta_eln.GUI.database_tests.database_api import DatabaseAPI
from pasta_eln.GUI.database_tests.project_model import ProjectModel
from pasta_eln.GUI.database_tests.upload_model import UploadModel


class DataverseDBAPI(object):

  def __init__(self):
    super().__init__()
    self.db_api = DatabaseAPI()
    self.design_doc_name = '_design/viewDataverse'

  def create_upload_model_document(self, data: UploadModel):
    data_dict = dict(data)
    del data_dict['_id']
    del data_dict['_rev']
    return UploadModel(**self.db_api.create_document(data_dict))

  def update_upload_model_document(self, data: UploadModel):
    self.db_api.update_document(dict(data))

  def create_dataverse_design_document(self):
    data = {"_id": self.design_doc_name}
    return self.db_api.create_document(data)

  def create_upload_documents_view(self):
    self.db_api.add_view(self.design_doc_name,
                         "dvUploadView",
                         "function (doc) { if (doc._data_type === 'dataverse_upload') { emit(doc._id, doc); } }",
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

  def get_all_upload_models(self):
    results = self.db_api.get_view_results(self.design_doc_name, "dvUploadView")
    return [UploadModel(**result) for result in results]

  def get_all_project_models(self):
    results = self.db_api.get_view_results(self.design_doc_name, "dvProjectsView")
    return [ProjectModel(**result) for result in results]

  def get_upload_model(self, model_id: str) -> UploadModel:
    return UploadModel(**self.db_api.get_view_results_by_id(self.design_doc_name, "dvUploadView", model_id))
