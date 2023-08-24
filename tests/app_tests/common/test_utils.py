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


def dump_object_as_json(json_object: object,
                        dump_file: str) -> None:
  """
  Dumps the json object into the file given within test_data folder in cd
  Args:
      json_object (object): Object to be printed.
      dump_file (str): File name where the object to be dumped.
  Returns:
      None
  """
  dump = json.dumps(json_object, sort_keys=True, indent='\t', separators=(',', ': '))
  test_data_folder = os.path.join(os.getcwd(), "..//test_data")
  if not os.path.exists(test_data_folder):
    os.makedirs(test_data_folder)
  test_data_path = os.path.join(test_data_folder, dump_file)
  json.dump(dump, open(test_data_path, 'w'))
