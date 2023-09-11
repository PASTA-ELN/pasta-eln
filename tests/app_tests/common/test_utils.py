#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#
#  Author: Jithu Murugan
#  Filename: test_utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import json
import os

from cloudant.document import Document


def save_couchdb_document_in_file(couch_db_doc: Document,
                                  save_file_name: str) -> None:
  """
  Dumps the json object into the file given within test_data folder in cd
  Args:
      couch_db_doc (Document): Document to be saved.
      save_file_name (str): File name where the document to be dumped.
  Returns:
      None
  """
  test_data_path = get_test_data_path(os.getcwd(), save_file_name)
  json.dump(couch_db_doc, open(test_data_path, 'w'))


def get_ontology_document(document_json_file: str) -> dict | None:
  """
  Returns the dict representation of ontology document from the file
  Args:
      document_json_file (str): File name representing document data in test_data folder

  Returns:
      Json representation of ontology document
  """
  test_data_path = get_test_data_path(os.getcwd(), document_json_file)
  if not os.path.exists(test_data_path):
    return None
  with open(test_data_path) as f:
    return json.loads(f.read())


def get_test_data_path(executing_path: str,
                       document_json_file: str):
  """
  Resolve the test data path
  Args:
    document_json_file (str):
    executing_path (str):

  Returns:

  """
  if os.path.exists(os.path.join(executing_path, "tests", "app_tests", "test_data")):
    test_data_path = os.path.join(executing_path, "tests", "app_tests", "test_data", document_json_file)
  else:
    test_data_path = os.path.join(executing_path, "..//test_data", document_json_file)
  import pathlib
  if not os.path.exists(pathlib.Path(test_data_path).parent):
    os.makedirs(pathlib.Path(test_data_path).parent)
  return test_data_path