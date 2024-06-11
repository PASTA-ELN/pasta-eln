#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_completed_uploads.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from PySide6 import QtCore

from pasta_eln.GUI.dataverse.completed_uploads import CompletedUploads
from pasta_eln.dataverse.upload_model import UploadModel
from pasta_eln.dataverse.upload_status_values import UploadStatusValues


@pytest.fixture
def mock_completed_upload(mocker):
  mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.logging.getLogger")
  mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.QDialog")
  mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.DatabaseAPI")
  mocker.patch("pasta_eln.GUI.dataverse.completed_uploads_base.Ui_CompletedUploadsForm.setupUi")
  mocker.patch.object(CompletedUploads, 'completedUploadsScrollArea', create=True)
  mocker.patch.object(CompletedUploads, 'completedUploadsVerticalLayout', create=True)
  mocker.patch.object(CompletedUploads, 'filterTermLineEdit', create=True)
  instance = CompletedUploads()
  return instance


class TestDataverseCompletedUploads:
  @pytest.mark.parametrize("test_id", [
    ("test_happy_path")
  ])
  def test_completed_uploads_initialization(self, mocker, test_id):
    # Arrange
    mock_get_logger = mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.logging.getLogger")
    mock_dialog = mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.QDialog")
    mock_database_api = mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.DatabaseAPI")
    mock_setup_ui = mocker.patch("pasta_eln.GUI.dataverse.completed_uploads_base.Ui_CompletedUploadsForm.setupUi")
    mocker.patch.object(CompletedUploads, 'completedUploadsScrollArea', create=True)
    mocker.patch.object(CompletedUploads, 'filterTermLineEdit', create=True)

    # Act
    completed_upload_instance = CompletedUploads()

    # Assert
    mock_get_logger.assert_any_call('pasta_eln.GUI.dataverse.completed_uploads.CompletedUploads')
    mock_dialog.assert_called_once()
    mock_setup_ui.assert_called_once_with(completed_upload_instance.instance)
    mock_database_api.assert_called_once()
    assert completed_upload_instance.load_complete is False
    assert completed_upload_instance.next_bookmark is None
    assert completed_upload_instance.logger is mock_get_logger.return_value, "Logger should be initialized"
    assert completed_upload_instance.db_api is mock_database_api.return_value, "DatabaseAPI should be initialized"
    assert completed_upload_instance.instance is mock_dialog.return_value, "completed_upload_instance should be initialized"
    completed_upload_instance.instance.setWindowModality.assert_called_once_with(QtCore.Qt.ApplicationModal)
    completed_upload_instance.completedUploadsScrollArea.verticalScrollBar().valueChanged.connect.assert_called_once_with(
      completed_upload_instance.scrolled)
    completed_upload_instance.filterTermLineEdit.textChanged.connect.assert_called_once_with(
      completed_upload_instance.load_ui)

  @pytest.mark.parametrize("result, filter_text, expected_widget_count, expected_exception, test_id", [
    # Test ID: 1 - Success path with multiple uploads
    ({"models": [UploadModel(), UploadModel()], "bookmark": "bookmark123"}, "text123", 2, None,
     "success_with_multiple_uploads"),
    # Test ID: 2 - Success path with no uploads
    ({"models": [], "bookmark": None}, "text456", 0, None, "success_with_no_uploads"),
    # Test ID: 3 - Edge case with None result
    (None, "text789", 0, TypeError, "edge_case_with_none_result"),
    # Test ID: 4 - Error case with incorrect type in models
    ({"models": ["not_an_upload_model"], "bookmark": "bookmarkABC"}, "text000", 0, None,
     "error_with_incorrect_type_in_models"),
    # Test ID: 4 - Error case with incorrect type in models
    ({"models": ["not_an_upload_model"], "bookmark": None}, "text000", 0, None,
     "error_with_incorrect_bookmark_in_models"),
  ])
  def test_load_ui(self, mocker, mock_completed_upload, result, filter_text,
                   expected_widget_count, expected_exception, test_id):
    # Arrange
    mock_completed_upload.db_api.get_paginated_models.return_value = result
    mock_completed_upload.filterTermLineEdit.text.return_value = filter_text
    mock_completed_upload.get_completed_upload_task_widget = mocker.MagicMock()
    mock_completed_upload.clear_ui = mocker.MagicMock()
    mock_completed_upload.get_completed_upload_task_widget = mocker.MagicMock()

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        mock_completed_upload.load_ui()
    else:
      mock_completed_upload.load_ui()

    # Assert
    mock_completed_upload.clear_ui.assert_called_once()
    mock_completed_upload.filterTermLineEdit.text.assert_called_once()
    mock_completed_upload.logger.info.assert_called_once_with("Loading completed uploads..")
    if result is not None and isinstance(result, dict):
      assert mock_completed_upload.completedUploadsVerticalLayout.addWidget.call_count == expected_widget_count
      if "bookmark" in result and isinstance(result["bookmark"], str):
        assert mock_completed_upload.next_bookmark == result["bookmark"]
      else:
        assert mock_completed_upload.next_bookmark is None
    if test_id == "error_with_incorrect_type_in_models":
      mock_completed_upload.logger.error.assert_called_once_with("Incorrect type in queried models!")
    if test_id == "error_with_incorrect_bookmark_in_models":
      mock_completed_upload.logger.error.assert_called_once_with(
        "Unable to retrieve models, invalid bookmark returned!")

  @pytest.mark.parametrize("num_widgets, test_id", [
    (0, "success_no_widgets"),  # No widgets to remove
    (1, "success_single_widget"),  # Single widget
    (5, "success_multiple_widgets"),  # Multiple widgets
  ])
  def test_clear_ui(self, mocker, mock_completed_upload, num_widgets, test_id):
    # Arrange
    widgets = [mocker.MagicMock() for _ in range(num_widgets)]
    mock_completed_upload.completedUploadsVerticalLayout.count.return_value = num_widgets
    mock_completed_upload.completedUploadsVerticalLayout.itemAt.side_effect = lambda x: mocker.MagicMock(
      widget=lambda: widgets[x])

    # Act
    mock_completed_upload.clear_ui()

    # Assert
    assert mock_completed_upload.completedUploadsVerticalLayout.count.call_count == 1
    assert mock_completed_upload.completedUploadsVerticalLayout.itemAt.call_count == num_widgets
    for widget in widgets:
      widget.setParent.assert_called_once_with(None)

  @pytest.mark.parametrize(
    "upload, expected_project_name, expected_status, expected_url, expected_tooltip, expected_created_date, expected_finished_date",
    [
      pytest.param(
        UploadModel(project_name="Project A", status=UploadStatusValues.Uploading.name, dataverse_url="",
                    created_date_time="",
                    finished_date_time=""),
        "Project A", "Waiting..", "Waiting..", "", "Waiting..", "Waiting..",
        id="in_progress"
      ),
      pytest.param(
        UploadModel(project_name="Project B", status=UploadStatusValues.Queued.name, dataverse_url="",
                    created_date_time="",
                    finished_date_time=""),
        "Project B", "Waiting..", "Waiting..", "", "Waiting..", "Waiting..",
        id="queued"
      ),
      pytest.param(
        UploadModel(project_name="Project C", status=UploadStatusValues.Finished.name,
                    dataverse_url="http://example.com",
                    created_date_time="2023-01-01", finished_date_time="2023-01-02"),
        "Project C", "Finished", "http://formatted_url/example.com", "Dataverse URL\nhttp://example.com", "2023-01-01",
        "2023-01-02",
        id="finished"
      ),
      pytest.param(
        UploadModel(project_name="Project D", status=UploadStatusValues.Error.name, dataverse_url="",
                    created_date_time="",
                    finished_date_time=""),
        "Project D", "Error state..", "Error state..", "", "Error state..", "Error state..",
        id="failed"
      ),
      pytest.param(
        UploadModel(project_name="Project E", status=UploadStatusValues.Cancelled.name, dataverse_url="",
                    created_date_time="",
                    finished_date_time=""),
        "Project E", "NA", "NA", "", "NA", "NA",
        id="cancelled"
      ),
      pytest.param(
        UploadModel(project_name="Project F", status="Unknown", dataverse_url="", created_date_time="",
                    finished_date_time=""),
        "Project F", "Error state..", "Error state..", "", "Error state..", "Error state..",
        id="unknown_status"
      ),
    ]
  )
  def test_get_completed_upload_task_widget(self, mocker, mock_completed_upload, upload, expected_project_name,
                                            expected_status, expected_url, expected_tooltip, expected_created_date,
                                            expected_finished_date):
    # Arrange
    mock_frame = mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.QFrame")
    mock_completed_upload_frame = mocker.patch("pasta_eln.GUI.dataverse.completed_uploads.Ui_CompletedUploadTaskFrame")
    mock_get_formatted_dataverse_url = mocker.patch(
      "pasta_eln.GUI.dataverse.completed_uploads.get_formatted_dataverse_url", return_value=expected_url)
    mock_completed_upload_frame.return_value.dataverseUrlLabel.toolTip.return_value = "Dataverse URL"
    mock_completed_upload.set_completed_task_properties = mocker.MagicMock()

    # Act
    result = mock_completed_upload.get_completed_upload_task_widget(upload)

    # Assert
    mock_frame.assert_called_once()
    mock_completed_upload_frame.assert_called_once()
    mock_completed_upload_frame.return_value.setupUi.assert_called_once_with(result)
    mock_completed_upload_frame.return_value.projectNameLabel.setText(upload.project_name)
    mock_completed_upload_frame.return_value.statusLabel.setText(upload.status)
    assert result is mock_frame.return_value, "Expected return value to be a QFrame"
    if expected_status == "Finished":
      mock_get_formatted_dataverse_url.assert_called_once_with("http://example.com")
      mock_completed_upload_frame.return_value.dataverseUrlLabel.toolTip.assert_called_once()
    mock_completed_upload.set_completed_task_properties.assert_called_once_with(
      mock_completed_upload_frame.return_value,
      expected_url,
      expected_tooltip,
      expected_created_date,
      expected_finished_date
    )

  @pytest.mark.parametrize(
    "dataverse_url, dataverse_url_tooltip, started_date_time, finished_date_time, expected_url, expected_tooltip, expected_started, expected_finished",
    [
      # Happy path tests
      ("http://example.com", "Example Tooltip", "2023-01-01 10:00:00", "2023-01-01 12:00:00", "http://example.com",
       "Example Tooltip", "2023-01-01 10:00:00", "2023-01-01 12:00:00"),
      ("http://another.com", "Another Tooltip", "2023-02-01 11:00:00", "2023-02-01 13:00:00", "http://another.com",
       "Another Tooltip", "2023-02-01 11:00:00", "2023-02-01 13:00:00"),

      # Edge cases
      ("", "", "", "", "default_url", "default_tooltip", "default_started", "default_finished"),
      (None, None, None, None, "default_url", "default_tooltip", "default_started", "default_finished"),

      # Error cases
      ("invalid_url", "Invalid Tooltip", "invalid_date", "invalid_date", "invalid_url", "Invalid Tooltip",
       "invalid_date", "invalid_date"),
    ],
    ids=[
      "success_path_1",
      "success_path_2",
      "edge_case_empty_strings",
      "edge_case_none_values",
      "error_case_invalid_values",
    ]
  )
  def test_set_completed_task_properties(self, mocker, mock_completed_upload, dataverse_url, dataverse_url_tooltip,
                                         started_date_time, finished_date_time,
                                         expected_url, expected_tooltip, expected_started, expected_finished):

    # Arrange
    completed_task_ui = mocker.MagicMock()
    completed_task_ui.dataverseUrlLabel.toolTip.return_value = "default_tooltip"
    completed_task_ui.dataverseUrlLabel.text.return_value = "default_url"
    completed_task_ui.startedDateTimeLabel.text.return_value = "default_started"
    completed_task_ui.finishedDateTimeLabel.text.return_value = "default_finished"

    # Act
    mock_completed_upload.set_completed_task_properties(completed_task_ui, dataverse_url, dataverse_url_tooltip,
                                                        started_date_time,
                                                        finished_date_time)

    # Assert
    completed_task_ui.dataverseUrlLabel.setToolTip.assert_called_once_with(expected_tooltip)
    completed_task_ui.dataverseUrlLabel.setText.assert_called_once_with(expected_url)
    completed_task_ui.startedDateTimeLabel.setText.assert_called_once_with(expected_started)
    completed_task_ui.finishedDateTimeLabel.setText.assert_called_once_with(expected_finished)

  @pytest.mark.parametrize(
    "load_ui_side_effect, instance_show_side_effect, expected_exception",
    [
      pytest.param(None, None, None, id="success_path"),
      pytest.param(Exception("load_ui error"), None, Exception, id="load_ui_error"),
      pytest.param(None, Exception("show error"), Exception, id="instance_show_error"),
    ],
    ids=lambda param: param[-1]
  )
  def test_show(self, mocker, mock_completed_upload, load_ui_side_effect, instance_show_side_effect,
                expected_exception):

    # Arrange
    mock_completed_upload.load_ui = mocker.MagicMock()
    mock_completed_upload.load_ui.side_effect = load_ui_side_effect
    mock_completed_upload.instance.show.side_effect = instance_show_side_effect

    # Act
    if expected_exception:
      with pytest.raises(expected_exception):
        mock_completed_upload.show()
    else:
      mock_completed_upload.show()

    # Assert
    if not expected_exception:
      mock_completed_upload.logger.info.assert_called_once_with("Showing completed uploads..")
      mock_completed_upload.load_ui.assert_called_once()
      mock_completed_upload.instance.show.assert_called_once()

  @pytest.mark.parametrize(
    "scroll_value, load_complete, next_bookmark, db_return_value, expected_log_call, expected_load_complete",
    [
      pytest.param(100, False, "bookmark", {"bookmark": "new_bookmark", "models": [UploadModel()]}, False, False,
                   id="success_path"),
      pytest.param(50, False, "bookmark", {"bookmark": "new_bookmark", "models": [UploadModel()]}, False, False,
                   id="scroll_not_at_max"),
      pytest.param(100, True, "bookmark", {"bookmark": "new_bookmark", "models": [UploadModel()]}, True, True,
                   id="load_complete_true"),
      pytest.param(100, False, None, {"bookmark": "new_bookmark", "models": [UploadModel()]}, False, False,
                   id="no_next_bookmark"),
      pytest.param(100, False, "bookmark", {"bookmark": "bookmark", "models": [UploadModel()]}, False, True,
                   id="same_bookmark"),
      pytest.param(100, False, "bookmark", {"bookmark": "new_bookmark", "models": []}, False, False,
                   id="no_models_returned"),
    ],
    ids=lambda val: val[-1]
  )
  def test_scrolled(self, mock_completed_upload, mocker, scroll_value, load_complete, next_bookmark, db_return_value,
                    expected_log_call,
                    expected_load_complete
                    ):
    mock_completed_upload.load_complete = load_complete
    mock_completed_upload.next_bookmark = next_bookmark
    mock_completed_upload.db_api.get_paginated_models.return_value = db_return_value
    mock_completed_upload.completedUploadsScrollArea.verticalScrollBar.return_value.maximum.return_value = 100
    mock_completed_upload.get_completed_upload_task_widget = mocker.MagicMock()
    mock_completed_upload.filterTermLineEdit.text.return_value = "filter_term"

    # Act
    mock_completed_upload.scrolled(scroll_value)

    # Assert
    if expected_log_call:
      mock_completed_upload.logger.info.assert_called_once_with("Data load completed, hence skipping..")
    else:
      mock_completed_upload.logger.info.assert_not_called()
    assert mock_completed_upload.load_complete == expected_load_complete
    if scroll_value == 100 and not load_complete and next_bookmark:
      mock_completed_upload.db_api.get_paginated_models.assert_called_once_with(
        UploadModel, filter_term="filter_term", bookmark=next_bookmark
      )
      if not expected_load_complete:
        if db_return_value["models"]:
          mock_completed_upload.get_completed_upload_task_widget.assert_called()
          mock_completed_upload.completedUploadsVerticalLayout.addWidget.assert_called()
        else:
          mock_completed_upload.get_completed_upload_task_widget.assert_not_called()
          mock_completed_upload.completedUploadsVerticalLayout.addWidget.assert_not_called()
    else:
      mock_completed_upload.db_api.get_paginated_models.assert_not_called()
