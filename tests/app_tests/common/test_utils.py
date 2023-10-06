#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: test_utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import json
import os


def save_json(json_object: object,
              save_file_name: str) -> None:
  """
  Dumps the json object into the file given within test_data folder in cd
  Args:
      json_object (object): Json to be saved.
      save_file_name (str): File name where the object to be dumped.
  Returns:
      None
  """
  test_data_path = get_test_data_path(os.getcwd(), save_file_name)
  json.dump(json_object, open(test_data_path, 'w'))


def read_json(json_file: str) -> dict | None:
  """
  Returns the dict representation of the json file
  Args:
      json_file (str): File name representing data in test_data folder or relative path from test data folder

  Returns:
      Json representation of the file
  """
  test_data_path = get_test_data_path(os.getcwd(), json_file)
  if not os.path.exists(test_data_path):
    return None
  with open(test_data_path, encoding='utf-8') as f:
    return json.loads(f.read())


def are_json_equal(json1: dict,
                   json2: dict) -> bool:
  """
  Compare two json objects
  Args:
    json1 (dict):
    json2 (dict):

  Returns: True if the two json objects are equal

  """
  return json.dumps(json1, sort_keys=True) == json.dumps(json2, sort_keys=True)


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
