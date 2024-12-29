#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_config_error.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.config_error import ConfigError


class TestConfigError:
  # Test cases for ConfigError initialization with various realistic values
  @pytest.mark.parametrize('message, detailed_errors, test_id', [
    ('Error reading configuration', None, 'happy_path_no_details'),
    ('Error writing configuration', {'line': '10', 'error': 'invalid syntax'}, 'happy_path_with_details'),
    ('Permission denied', {'file': '/etc/config', 'error': 'permission denied'}, 'happy_path_with_permission_error'),
  ])
  def test_config_error_initialization(self, message, detailed_errors, test_id):
    # Act
    exception = ConfigError(message, detailed_errors)

    # Assert
    assert exception.message == message, f"Test failed for {test_id}: message attribute mismatch"
    assert exception.detailed_errors == detailed_errors, f"Test failed for {test_id}: detailed_errors attribute mismatch"

  # Test cases for ConfigError initialization with edge cases
  @pytest.mark.parametrize('message, detailed_errors, test_id', [
    ('', None, 'edge_case_empty_message'),
    ('Error', {}, 'edge_case_empty_details'),
    ('Error', {'key': ''}, 'edge_case_empty_detail_value'),
  ])
  def test_config_error_edge_cases(self, message, detailed_errors, test_id):
    # Act
    exception = ConfigError(message, detailed_errors)

    # Assert
    assert exception.message == message, f"Test failed for {test_id}: message attribute mismatch"
    assert exception.detailed_errors == detailed_errors, f"Test failed for {test_id}: detailed_errors attribute mismatch"
