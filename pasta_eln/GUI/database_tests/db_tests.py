#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: db_tests.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from cloudant import CouchDB

from pasta_eln.GUI.database_tests.config_model import ConfigModel
from pasta_eln.GUI.database_tests.dataverse_db_api import DataverseDBAPI


class DBTests(object):

  def __init__(self):
    super().__init__()
    db = self.get_db("admin", "ceca7ae93325450a848a0a431add5c0d", "research", "localhost", 5984)
    print(db["-dataHierarchy-"])
    data = {
      # '_id': 'test',  # Setting _id is optional
      'name': 'test',
      'age': 30,
      'pets': ['cat', 'dog', 'frog']
    }
    my_document = db.create_document(data)
    print(my_document)
    if my_document.exists():
      print('SUCCESS!!')
    print("DB Tests")

  def get_db(self, user, password, databaseName, host, port):
    try:
      client = CouchDB(user, password, url=f'http://{host}:{port}', connect=True)
    except Exception:
      print('**ERROR dit01: Could not connect with username+password to local server')
      raise  # there is no possibility to recover
    return (
      client[databaseName]
      if databaseName in client.all_dbs()
      else client.create_database(databaseName)
    )


if __name__ == "__main__":
  from faker import Faker

  fake = Faker()
  api = DataverseDBAPI()
  # api.create_dataverse_design_document()
  # api.create_upload_documents_view()
  # api.create_projects_view()

  # config_model = ConfigModel("-dataverseConfig-")
  # config_model.project_upload_items = {}
  # config_model.dataverse_login_info = {"username": fake.name(), "password": fake.name()}
  # config_model.metadata = {}
  # config_model.parallel_uploads_count = 5
  # config_model = api.create_model_document(config_model)
  config_model = api.get_model("-dataverseConfig-", ConfigModel)
  print(config_model.__dict__)
  data_hierarchy = api.get_data_hierarchy()
  print(data_hierarchy)

  # for _ in range(500):
  #   dv_upload_model = UploadModel(fake.name(), "Finished", fake.iso8601(), fake.text(), fake.url())
  #   new_doc = api.create_upload_model_document(dv_upload_model)
  # dv_upload_model = UploadModel(fake.name(), "uploading", fake.iso8601(), fake.text(), fake.url())
  # print(dv_upload_model.__dict__)
  # print("######################")
  # new_doc = api.create_upload_model_document(dv_upload_model)
  # results = api.get_all_upload_models()
  # print(f"###################### count: {len(results)}")
  # for result in results:
  #   print(result.__dict__)
  # print("######################")
  # result = api.get_upload_model(new_doc['_id'])
  # print(result.__dict__)
  # result.project_name = fake.name() + fake.name()
  # result.upload_status = "finished"
  # result = api.update_upload_model_document(result)
  # print(result.__dict__)
  # print("######################")
  # projects = api.get_all_project_models()
  # for project in projects:
  #   print(project.__dict__)

# tests = DBTests()
