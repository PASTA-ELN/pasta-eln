#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_incorrect_parameter_error.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.incorrect_parameter_error import IncorrectParameterError


class TestIncorrectParameterError:
  # Success path tests with various realistic test values
  @pytest.mark.parametrize("message, detailed_errors, test_id", [
    ("Error occurred", None, "happy_none_detailed_errors"),
    ("Error occurred", {"param1": "invalid value"}, "happy_with_detailed_errors_single"),
    ("Error occurred", {"param1": "invalid value", "param2": "missing field"}, "happy_with_detailed_errors_multiple")
  ])
  def test_incorrect_parameter_error_success_path(self, message, detailed_errors, test_id):
    # Act
    error = IncorrectParameterError(message, detailed_errors)

    # Assert
    assert error.message == message, f"Test failed for {test_id}: message attribute does not match."
    assert error.detailed_errors == detailed_errors, f"Test failed for {test_id}: detailed_errors attribute does not match."

  # Edge cases
  @pytest.mark.parametrize("message, detailed_errors, test_id", [
    ("", None, "edge_empty_message"),
    ("Error occurred", {}, "edge_empty_detailed_errors")
  ])
  def test_incorrect_parameter_error_edge_cases(self, message, detailed_errors, test_id):
    # Act
    error = IncorrectParameterError(message, detailed_errors)

    # Assert
    assert error.message == message, f"Test failed for {test_id}: message attribute does not match."
    assert error.detailed_errors == detailed_errors, f"Test failed for {test_id}: detailed_errors attribute does not match."
