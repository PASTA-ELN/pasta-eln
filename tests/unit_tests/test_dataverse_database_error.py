#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_database_error.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest

from pasta_eln.dataverse.database_error import DatabaseError


class TestDataverseDatabaseError:

  @pytest.mark.parametrize("test_id, message, detailed_errors, expected_message, expected_detailed_errors",
                           [# Happy path tests with various realistic test values
                             ("success", "Connection failed", {"code": "CONN_ERR"}, "Connection failed",
                              {"code": "CONN_ERR"}), (
                           "success", "Query execution aborted", {"query": "SELECT *"}, "Query execution aborted",
                           {"query": "SELECT *"}),

                             # Edge cases
                             ("edge_empty_message", "", {}, "", {}),
                             ("edge_empty_detailed_errors", "Missing data", {}, "Missing data", {}), ])
  def test_database_error_initialization(self, test_id, message, detailed_errors, expected_message,
                                         expected_detailed_errors):
    # Act
    exception = DatabaseError(message, detailed_errors)

    # Assert
    assert exception.message == expected_message, f"Test ID: {test_id} - The message attribute does not match the expected value."
    assert exception.detailed_errors == expected_detailed_errors, f"Test ID: {test_id} - The detailed_errors attribute does not match the expected value."
