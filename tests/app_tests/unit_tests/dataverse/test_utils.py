#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest

from pasta_eln.dataverse.upload_status_values import UploadStatusValues
from pasta_eln.dataverse.utils import update_status


class TestUtils:

  # Parametrized test cases for happy path, edge cases, and error cases
  @pytest.mark.parametrize(
    "status, expected_icon_name, test_id",
    [
      (UploadStatusValues.Queued.name, 'ph.queue-bold', 'happy_path_queued'),
      (UploadStatusValues.Uploading.name, 'mdi6.progress-upload', 'happy_path_uploading'),
      (UploadStatusValues.Cancelled.name, 'mdi.cancel', 'happy_path_cancelled'),
      (UploadStatusValues.Finished.name, 'fa.check-circle-o', 'happy_path_finished'),
      (UploadStatusValues.Error.name, 'msc.error-small', 'happy_path_error'),
      (UploadStatusValues.Warning.name, 'fa.warning', 'happy_path_warning'),
      # Add edge cases here
      # Add error cases here
    ]
  )
  def test_update_status(self, mocker, status, expected_icon_name, test_id):
    # Arrange
    status_icon_label = mocker.MagicMock()
    status_label = mocker.MagicMock()
    mock_icon = mocker.MagicMock()
    mock_icon.constructor = mocker.patch('pasta_eln.dataverse.utils.icon', return_value=mock_icon)

    # Act
    update_status(status, status_icon_label, status_label)

    # Assert
    status_label.setText.assert_called_once_with(status)
    # Check if the correct icon is set for the given status
    mock_icon.constructor.assert_called_once_with(expected_icon_name)
    status_icon_label.size.assert_called_once()
    status_icon_label.setPixmap.assert_called_once_with(mock_icon.pixmap.return_value)
    mock_icon.pixmap.assert_called_once_with(status_icon_label.size())
