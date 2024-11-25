#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_upload_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox

from pasta_eln.GUI.dataverse.upload_config_dialog import UploadConfigDialog
from pasta_eln.database.models.config_model import ConfigModel
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel


@pytest.fixture
def mock_database_api(mocker):
  mock = mocker.patch('pasta_eln.dataverse.database_api.DatabaseAPI')
  mock_instance = mock.return_value
  config_model = ConfigModel(_id=123456789,
                             dataverse_login_info={
                               "server_url": "http://valid.url",
                               "api_token": "encrypted_api_token",
                               "dataverse_id": "test_dataverse_id"
                             },
                             parallel_uploads_count=2,
                             project_upload_items={
                               'Measurement': False,
                               'Sample': False,
                               'Procedure': False,
                               'Instrument': False,
                               'Unidentified': False
                             },
                             metadata=mocker.MagicMock(spec=dict))
  mock_instance.get_config_model.return_value = config_model
  mock_instance.get_data_hierarchy.return_value = {
    "x0": {},
    "x1": {},
    "measurement": {},
    "sample": {},
    "procedure": {},
    "instrument": {}
  }
  mock_instance.get_data_hierarchy_models.return_value = [
    DataHierarchyModel(docType="x0"),
    DataHierarchyModel(docType="x1"),
    DataHierarchyModel(docType="measurement"),
    DataHierarchyModel(docType="sample"),
    DataHierarchyModel(docType="procedure"),
    DataHierarchyModel(docType="instrument")
  ]
  return mock_instance


@pytest.fixture
def upload_config_dialog(qtbot, mocker, mock_database_api):
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.DatabaseAPI', return_value=mock_database_api)
  mocker.patch('pasta_eln.GUI.dataverse.upload_config_dialog.logging')
  dialog = UploadConfigDialog()
  mocker.resetall()
  qtbot.addWidget(dialog.instance)
  return dialog


class TestDataverseUploadConfigDialog:
  def test_component_launch_should_display_all_ui_elements(self, qtbot, upload_config_dialog):
    upload_config_dialog.show()
    with qtbot.waitExposed(upload_config_dialog.instance, timeout=500):
      assert upload_config_dialog.instance.isVisible() is True, "UploadConfigDialog should be shown!"
      assert upload_config_dialog.buttonBox.isVisible() is True, "UploadConfigDialog dialog button box not shown!"
      assert upload_config_dialog.numParallelComboBox.isVisible(), "UploadConfigDialog numParallelComboBox should be shown!"
      assert upload_config_dialog.numParallelLabel.isVisible(), "UploadConfigDialog numParallelComboBox should be shown!"
      assert upload_config_dialog.buttonBox.button(
        QDialogButtonBox.Save).isVisible(), "UploadConfigDialog Save button should be shown!"
      assert upload_config_dialog.buttonBox.button(
        QDialogButtonBox.Cancel).isVisible(), "UploadConfigDialog Save button should be shown!"
      assert upload_config_dialog.data_hierarchy_types == ['Measurement', 'Sample', 'Procedure', 'Instrument',
                                                           'Unidentified'], "UploadConfigDialog data_hierarchy_types should be populated with default values!"

      assert upload_config_dialog.instance.windowTitle() == "Configure project upload", "UploadConfigDialog instance windowTitle should be populated with default value!"
      assert upload_config_dialog.instance.toolTip() == "Select the configuration parameters used for dataverse upload.", "UploadConfigDialog instance tooltip should be populated with default values!"
      assert upload_config_dialog.projectContentsScrollArea.toolTip() == "Select the sub-items in a project to be uploaded to dataverse.", "UploadConfigDialog projectContentsScrollArea tooltip should be populated with default values!"
      assert upload_config_dialog.numParallelLabel.text() == "No of parallel uploads", "UploadConfigDialog numParallelLabel should be populated with default values!"
      assert upload_config_dialog.numParallelComboBox.currentText() == "2", "UploadConfigDialog numParallelComboBox should be set with default value!"
      assert [upload_config_dialog.numParallelComboBox.itemText(i) for i in
              range(upload_config_dialog.numParallelComboBox.count())] == ['2', '3', '4',
                                                                           '5'], "UploadConfigDialog numParallelComboBox should be populated with default values!"
      assert upload_config_dialog.numParallelComboBox.toolTip() == "Choose the number of parallel dataverse uploads.", "UploadConfigDialog numParallelComboBox tooltip should be populated with default values!"
      assert upload_config_dialog.projectItemsVerticalLayout.count() == 5, "UploadConfigDialog projectItemsVerticalLayout should not be empty!"
      for pos in range(upload_config_dialog.projectItemsVerticalLayout.count()):
        widget = upload_config_dialog.projectItemsVerticalLayout.itemAt(pos).widget()
        assert widget.isVisible(), "UploadConfigDialog projectItemsVerticalLayout widget should be shown!"
        assert widget.text() == upload_config_dialog.data_hierarchy_types[
          pos], "UploadConfigDialog projectItemsVerticalLayout widget should be populated with default values!"
        assert not widget.isChecked(), f"UploadConfigDialog projectItemsVerticalLayout widget: {widget.text()} should not be checked!"

  @pytest.mark.parametrize("test_id, num_parallel, expected_num_parallel", [
    ("success_case_with_max_num_parallel", "5", 5),
    ("success_case_with_min_num_parallel", "2", 2),
    ("success_case_with_in_range_num_parallel_1", "3", 3),
    ("success_case_with_in_range_num_parallel_2", "4", 4),
    ("edge_case_with_min_below_num_parallel", "1", 2),
    ("edge_case_with_min_below_num_parallel", "10", 2),
  ])
  def test_select_num_of_parallel_uploads_and_save_click_should_set_right_values(self, qtbot, upload_config_dialog,
                                                                                 mock_database_api,
                                                                                 test_id, num_parallel,
                                                                                 expected_num_parallel):
    upload_config_dialog.show()
    with qtbot.waitExposed(upload_config_dialog.instance, timeout=500):
      assert upload_config_dialog.instance.isVisible() is True, "UploadConfigDialog should be shown!"
      assert upload_config_dialog.buttonBox.isVisible() is True, "UploadConfigDialog dialog button box not shown!"
      assert upload_config_dialog.numParallelComboBox.isVisible(), "UploadConfigDialog numParallelComboBox should be shown!"

      qtbot.keyClicks(upload_config_dialog.numParallelComboBox, num_parallel, delay=1)

      assert upload_config_dialog.numParallelComboBox.currentText() == str(
        expected_num_parallel), f"UploadConfigDialog numParallelComboBox should be set with {expected_num_parallel}!"

    qtbot.mouseClick(upload_config_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not upload_config_dialog.instance.isVisible(), "UploadConfigDialog instance should be closed!"
    assert upload_config_dialog.config_model.parallel_uploads_count == expected_num_parallel, f"UploadConfigDialog model should be updated with {expected_num_parallel}!"
    mock_database_api.save_config_model.assert_called_once_with(upload_config_dialog.config_model)

  @pytest.mark.parametrize("test_id, num_parallel, expected_num_parallel", [
    ("success_case_with_in_range_num_parallel_1", "3", 3),
    ("success_case_with_in_range_num_parallel_2", "4", 4),

  ])
  def test_select_num_of_parallel_uploads_and_save_cancel_should_not_set_right_values(self, qtbot, upload_config_dialog,
                                                                                      mock_database_api,
                                                                                      test_id, num_parallel,
                                                                                      expected_num_parallel):
    upload_config_dialog.show()
    with qtbot.waitExposed(upload_config_dialog.instance, timeout=500):
      assert upload_config_dialog.instance.isVisible() is True, "UploadConfigDialog should be shown!"
      assert upload_config_dialog.buttonBox.isVisible() is True, "UploadConfigDialog dialog button box not shown!"
      assert upload_config_dialog.numParallelComboBox.isVisible(), "UploadConfigDialog numParallelComboBox should be shown!"

      qtbot.keyClicks(upload_config_dialog.numParallelComboBox, num_parallel, delay=1)

      assert upload_config_dialog.numParallelComboBox.currentText() == str(
        expected_num_parallel), f"UploadConfigDialog numParallelComboBox should be set with {expected_num_parallel}!"

    qtbot.mouseClick(upload_config_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert not upload_config_dialog.instance.isVisible(), "UploadConfigDialog instance should be closed!"
    assert upload_config_dialog.config_model.parallel_uploads_count == expected_num_parallel, f"UploadConfigDialog model should be updated with {expected_num_parallel}!"
    mock_database_api.update_model.assert_not_called()

  @pytest.mark.parametrize("test_id, set_items", [
    ("success_case_set_all", {
      'Measurement': True,
      'Sample': True,
      'Procedure': True,
      'Instrument': True,
      'Unidentified': True
    }),
    ("success_case_set_1", {
      'Measurement': True,
      'Sample': False,
      'Procedure': True,
      'Instrument': True,
      'Unidentified': True
    }),
    ("success_case_set_2", {
      'Measurement': True,
      'Sample': False,
      'Procedure': False,
      'Instrument': True,
      'Unidentified': False
    }),
    ("success_case_un_set_all", {
      'Measurement': False,
      'Sample': False,
      'Procedure': False,
      'Instrument': False,
      'Unidentified': False
    }),

  ])
  def test_set_upload_items_and_save_should_set_right_values(self,
                                                             qtbot,
                                                             upload_config_dialog,
                                                             mock_database_api,
                                                             test_id,
                                                             set_items):
    upload_config_dialog.show()
    with qtbot.waitExposed(upload_config_dialog.instance, timeout=500):
      assert upload_config_dialog.instance.isVisible() is True, "UploadConfigDialog should be shown!"
      assert upload_config_dialog.buttonBox.isVisible() is True, "UploadConfigDialog dialog button box not shown!"
      assert upload_config_dialog.numParallelComboBox.isVisible(), "UploadConfigDialog numParallelComboBox should be shown!"

      for pos in range(upload_config_dialog.projectItemsVerticalLayout.count()):
        widget = upload_config_dialog.projectItemsVerticalLayout.itemAt(pos).widget()
        widget.setChecked(set_items[widget.text()])

    qtbot.mouseClick(upload_config_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not upload_config_dialog.instance.isVisible(), "UploadConfigDialog instance should be closed!"
    assert upload_config_dialog.config_model.project_upload_items == set_items, f"UploadConfigDialog model project_upload_items should be updated with {set_items}!"
    mock_database_api.save_config_model.assert_called_once_with(upload_config_dialog.config_model)

  def test_set_upload_items_and_cancel_should_not_set_right_values(self, qtbot, upload_config_dialog,
                                                                   mock_database_api):
    set_items = {
      'Measurement': False,
      'Sample': False,
      'Procedure': False,
      'Instrument': False,
      'Unidentified': False
    }
    upload_config_dialog.show()
    with qtbot.waitExposed(upload_config_dialog.instance, timeout=500):
      assert upload_config_dialog.instance.isVisible() is True, "UploadConfigDialog should be shown!"
      assert upload_config_dialog.buttonBox.isVisible() is True, "UploadConfigDialog dialog button box not shown!"
      assert upload_config_dialog.numParallelComboBox.isVisible(), "UploadConfigDialog numParallelComboBox should be shown!"

      for pos in range(upload_config_dialog.projectItemsVerticalLayout.count()):
        widget = upload_config_dialog.projectItemsVerticalLayout.itemAt(pos).widget()
        widget.setChecked(set_items[widget.text()])

    qtbot.mouseClick(upload_config_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert not upload_config_dialog.instance.isVisible(), "UploadConfigDialog instance should be closed!"
    assert upload_config_dialog.config_model.project_upload_items == set_items, f"UploadConfigDialog model project_upload_items should be updated with {set_items}!"
    mock_database_api.update_model.assert_not_called()
