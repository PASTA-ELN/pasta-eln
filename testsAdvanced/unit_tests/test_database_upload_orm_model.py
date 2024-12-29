#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_database_upload_orm_model.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.database.models.upload_orm_model import UploadOrmModel


class TestDatabaseOrmUploadModel:
  @pytest.mark.parametrize(
    'data_type, project_name, project_doc_id, status, created_date_time, finished_date_time, log, dataverse_url, expected_columns',
    [
      # Happy path test cases
      ('type1', 'project1', 'doc1', 'status1', '2023-01-01T00:00:00', '2023-01-02T00:00:00', 'log1',
       'http://example.com',
       ['id', 'data_type', 'project_name', 'project_doc_id', 'status', 'created_date_time', 'finished_date_time', 'log',
        'dataverse_url']),
      ('type2', 'project2', 'doc2', 'status2', '2023-02-01T00:00:00', '2023-02-02T00:00:00', 'log2',
       'http://example.org',
       ['id', 'data_type', 'project_name', 'project_doc_id', 'status', 'created_date_time', 'finished_date_time', 'log',
        'dataverse_url']),

      # Edge case test cases
      (None, None, None, None, None, None, None, None,
       ['id', 'data_type', 'project_name', 'project_doc_id', 'status', 'created_date_time', 'finished_date_time', 'log',
        'dataverse_url']),
      ('', '', '', '', '', '', '', '',
       ['id', 'data_type', 'project_name', 'project_doc_id', 'status', 'created_date_time', 'finished_date_time', 'log',
        'dataverse_url']),

      # Error case test cases
      # Assuming that the class should handle None and empty strings gracefully, no explicit error cases are defined here.
    ],
    ids=[
      'happy_path_case1',
      'happy_path_case2',
      'edge_case_none_values',
      'edge_case_empty_strings',
    ]
  )
  def test_get_table_columns(self, data_type, project_name, project_doc_id, status, created_date_time,
                             finished_date_time,
                             log, dataverse_url, expected_columns):
    # Act
    columns = UploadOrmModel.get_table_columns()

    # Assert
    assert columns == expected_columns
