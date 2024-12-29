#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_edit_metadata_summary_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from unittest.mock import MagicMock

import pytest
from PySide6 import QtCore

from pasta_eln.GUI.dataverse.edit_metadata_summary_dialog import EditMetadataSummaryDialog


@pytest.fixture
def dialog_instance(mocker):
  mocker.patch(
    'pasta_eln.GUI.dataverse.edit_metadata_summary_dialog_base.Ui_EditMetadataSummaryDialog.setupUi')
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.logging')
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.QDialog')
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.EditMetadataSummaryDialog.summaryTextEdit',
               create=True)
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.EditMetadataSummaryDialog.buttonBox',
               create=True)
  mock_call_back = mocker.MagicMock()
  dialog = EditMetadataSummaryDialog(mock_call_back)
  return dialog


class TestDataverseEditMetadataSummaryDialog:
  @pytest.mark.parametrize('test_id, save_config_callback, expected_behavior', [
    ('valid_callback', MagicMock(), 'should_connect'),
    ('null_callback', None, 'should_raise'),
    ('invalid_callback', 'not_a_function', 'should_raise'),
  ])
  def test_EditMetadataSummaryDialog_initialization(self, mocker, test_id, save_config_callback, expected_behavior):
    # Arrange
    mock_setup_ui = mocker.patch(
      'pasta_eln.GUI.dataverse.edit_metadata_summary_dialog_base.Ui_EditMetadataSummaryDialog.setupUi')
    mock_log = mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.logging')
    mock_qdialog = mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.QDialog')
    mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.EditMetadataSummaryDialog.summaryTextEdit',
                 create=True)
    mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.EditMetadataSummaryDialog.buttonBox',
                 create=True)
    if expected_behavior == 'should_raise':
      if save_config_callback is None or not callable(save_config_callback):
        with pytest.raises(TypeError):
          EditMetadataSummaryDialog(save_config_callback)
        return
    elif expected_behavior == 'should_connect':
      # Mocking QDialog and other Qt components would be necessary here, but since we're focusing on pytest
      # and avoiding additional dependencies, we'll simplify the test to assume these components work as expected.
      pass

    # Act
    dialog = EditMetadataSummaryDialog(save_config_callback)

    # Assert
    if expected_behavior == 'should_connect':
      mock_log.getLogger.assert_called_once_with(
        'pasta_eln.GUI.dataverse.edit_metadata_summary_dialog.EditMetadataSummaryDialog')
      mock_qdialog.assert_called_once()
      mock_setup_ui.assert_called_once_with(mock_qdialog.return_value)
      dialog.instance.setWindowModality.assert_called_once_with(QtCore.Qt.ApplicationModal)
      dialog.summaryTextEdit.setReadOnly.assert_called_once_with(True)
      dialog.buttonBox.accepted.connect.assert_called_once_with(save_config_callback)

  def test_show_calls_instance_show(self, dialog_instance):
    # Act
    dialog_instance.show()

    # Assert
    dialog_instance.instance.show.assert_called_once()
