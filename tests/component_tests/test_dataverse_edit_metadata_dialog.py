#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_edit_metadata_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import json
from os import getcwd
from os.path import dirname, join, realpath

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from pasta_eln.GUI.dataverse.edit_metadata_dialog import EditMetadataDialog
from pasta_eln.dataverse.config_model import ConfigModel
from pasta_eln.dataverse.utils import set_template_values


@pytest.fixture
def mock_database_api(mocker):
  mock = mocker.patch('pasta_eln.dataverse.database_api.DatabaseAPI')
  mock_instance = mock.return_value
  current_path = realpath(join(getcwd(), dirname(__file__)))
  with open(join(current_path, "..//..//pasta_eln//dataverse", "dataset-create-new-all-default-fields.json"),
            encoding="utf-8") as config_file:
    file_data = config_file.read()
    config_model = ConfigModel(_id="test_id",
                               _rev="test_rev",
                               dataverse_login_info={"server_url": "http://valid.url",
                                                     "api_token": "encrypted_api_token",
                                                     "dataverse_id": "test_dataverse_id"},
                               parallel_uploads_count=1,
                               project_upload_items={},
                               metadata=json.loads(file_data))
    set_template_values(mocker.MagicMock(), config_model.metadata or {})
  mock_instance.get_model.return_value = config_model
  return mock_instance


@pytest.fixture
def edit_metadata_dialog(qtbot, mocker, mock_database_api):
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_dialog.DatabaseAPI', return_value=mock_database_api)
  mocker.patch('pasta_eln.GUI.dataverse.edit_metadata_dialog.logging')
  dialog = EditMetadataDialog()
  mocker.resetall()
  qtbot.addWidget(dialog.instance)
  return dialog


class TestDataverseEditMetadataDialog:
  def test_component_launch_should_display_all_ui_elements(self, qtbot, edit_metadata_dialog):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.instance.isVisible() is True, "EditMetadataDialog should be shown!"
      assert edit_metadata_dialog.buttonBox.isVisible() is True, "EditMetadataDialog dialog button box not shown!"
      assert edit_metadata_dialog.minimalFullComboBox.isVisible(), "EditMetadataDialog minimalFullComboBox should be shown!"
      assert edit_metadata_dialog.metadataBlockComboBox.isVisible(), "EditMetadataDialog metadataBlockComboBox should be shown!"
      assert edit_metadata_dialog.typesComboBox.isVisible(), "EditMetadataDialog typesComboBox should be shown!"
      assert edit_metadata_dialog.licenseURLLineEdit.isVisible(), "EditMetadataDialog licenseURLLineEdit should be shown!"
      assert edit_metadata_dialog.licenseNameLineEdit.isVisible(), "EditMetadataDialog licenseNameLineEdit should be shown!"
      assert edit_metadata_dialog.buttonBox.button(
        edit_metadata_dialog.buttonBox.Save).isVisible(), "EditMetadataDialog Save button should be shown!"
      assert edit_metadata_dialog.buttonBox.button(
        edit_metadata_dialog.buttonBox.Cancel).isVisible(), "EditMetadataDialog Cancel button should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      primitive_vertical_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QVBoxLayout,
        "primitiveVerticalLayout")
      assert primitive_vertical_layout, "EditMetadataDialog primitive_compound_frame should be present!"
      delete_button = primitive_vertical_layout.itemAt(0).itemAt(1).widget()
      assert delete_button.isVisible(), "EditMetadataDialog primitive_compound_frame delete button should be shown!"
      assert not delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete button should be disabled!"
      assert not edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be disabled!"

      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Citation Metadata", "metadataBlockComboBox must be initialized with default 'Citation Metadata' option"
      assert edit_metadata_dialog.typesComboBox.currentText() == "Title", "typesComboBox must be initialized with default 'Title' option"
      assert edit_metadata_dialog.licenseNameLineEdit.text() == "CC0 1.0", "licenseNameLineEdit must be initialized with default 'CC0 1.0' option"
      assert edit_metadata_dialog.licenseURLLineEdit.text() == "http://creativecommons.org/publicdomain/zero/1.0", "licenseURLLineEdit must be initialized with default 'http://creativecommons.org/publicdomain/zero/1.0' option"
      metadata_block_comboBox_items = [edit_metadata_dialog.metadataBlockComboBox.itemText(i) for i in
                                       range(edit_metadata_dialog.metadataBlockComboBox.count())]
      assert metadata_block_comboBox_items == ['Citation Metadata', 'Geospatial Metadata',
                                               'Social Science and Humanities Metadata',
                                               'Astronomy and Astrophysics Metadata', 'Life Sciences Metadata',
                                               'Journal Metadata'], "metadataBlockComboBox must be initialized with default options"
      metafield_items = [edit_metadata_dialog.typesComboBox.itemText(i) for i in
                         range(edit_metadata_dialog.typesComboBox.count())]
      default_field_items = ['Title',
                             'Subtitle',
                             'Alternative Title',
                             'Alternative URL',
                             'Other Id',
                             'Author',
                             'Dataset Contact',
                             'Ds Description',
                             'Subject',
                             'Keyword',
                             'Topic Classification',
                             'Publication',
                             'Notes Text',
                             'Language',
                             'Producer',
                             'Production Date',
                             'Production Place',
                             'Contributor',
                             'Grant Number',
                             'Distributor',
                             'Distribution Date',
                             'Depositor',
                             'Date Of Deposit',
                             'Time Period Covered',
                             'Date Of Collection',
                             'Kind Of Data',
                             'Series',
                             'Software',
                             'Related Material',
                             'Related Datasets',
                             'Other References',
                             'Data Sources',
                             'Origin Of Sources',
                             'Characteristic Of Sources',
                             'Access To Sources']
      assert metafield_items == default_field_items, "typesComboBox must be initialized with default options"
    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(edit_metadata_dialog.buttonBox.Cancel), Qt.LeftButton)

  def test_change_to_minimal_should_list_only_minimal_fields(self, qtbot, edit_metadata_dialog):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      qtbot.keyClicks(edit_metadata_dialog.minimalFullComboBox, "Minimal", delay=1)
      assert edit_metadata_dialog.instance.isVisible() is True, "EditMetadataDialog should be shown!"
      assert edit_metadata_dialog.buttonBox.isVisible() is True, "EditMetadataDialog dialog button box not shown!"
      assert edit_metadata_dialog.minimalFullComboBox.isVisible(), "EditMetadataDialog minimalFullComboBox should be shown!"
      assert not edit_metadata_dialog.metadataBlockComboBox.isVisible(), "EditMetadataDialog metadataBlockComboBox should not be shown!"
      assert edit_metadata_dialog.typesComboBox.isVisible(), "EditMetadataDialog typesComboBox should be shown!"
      assert edit_metadata_dialog.licenseURLLineEdit.isVisible(), "EditMetadataDialog licenseURLLineEdit should be shown!"
      assert edit_metadata_dialog.licenseNameLineEdit.isVisible(), "EditMetadataDialog licenseNameLineEdit should be shown!"
      assert edit_metadata_dialog.buttonBox.button(
        edit_metadata_dialog.buttonBox.Save).isVisible(), "EditMetadataDialog Save button should be shown!"
      assert edit_metadata_dialog.buttonBox.button(
        edit_metadata_dialog.buttonBox.Cancel).isVisible(), "EditMetadataDialog Cancel button should be shown!"
      assert edit_metadata_dialog.controlled_vocab_frame.instance.isVisible(), "EditMetadataDialog controlled_vocab_frame should be shown!"
      assert edit_metadata_dialog.controlled_vocab_frame.addPushButton.isVisible(), "EditMetadataDialog controlled_vocab_frame addPushButton should be shown!"
      vocab_horizontal_layout = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.findChild(
        QHBoxLayout,
        "vocabHorizontalLayout")
      assert vocab_horizontal_layout, "EditMetadataDialog vocab_horizontal_layout should be present in mainVerticalLayout!"
      controlled_combo_box = vocab_horizontal_layout.itemAt(0).widget()
      assert controlled_combo_box.isVisible(), "EditMetadataDialog controlled_vocab_frame controlled_combo_box should be shown!"
      assert controlled_combo_box.isEnabled(), "EditMetadataDialog controlled_vocab_frame controlled_combo_box should be enabled!"
      delete_button = vocab_horizontal_layout.itemAt(1).widget()
      assert delete_button.isVisible(), "EditMetadataDialog controlled_vocab_frame delete button should be shown!"
      assert delete_button.isEnabled(), "EditMetadataDialog controlled_vocab_frame delete button should be enabled!"
      assert edit_metadata_dialog.controlled_vocab_frame.addPushButton.isEnabled(), "EditMetadataDialog controlled_vocab_frame addPushButton should be enabled!"

      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Minimal", "minimalFullComboBox must be initialized with default Minimal option"
      assert edit_metadata_dialog.typesComboBox.currentText() == "Subject", "typesComboBox must be initialized with default 'Title' option"
      assert edit_metadata_dialog.licenseNameLineEdit.text() == "CC0 1.0", "licenseNameLineEdit must be initialized with default 'CC0 1.0' option"
      assert edit_metadata_dialog.licenseURLLineEdit.text() == "http://creativecommons.org/publicdomain/zero/1.0", "licenseURLLineEdit must be initialized with default 'http://creativecommons.org/publicdomain/zero/1.0' option"
      assert delete_button.text() == "Delete", "Delete button should have right text"
      assert delete_button.toolTip() == 'Delete this particular vocabulary entry.', "Delete button should have right tooltip"
      assert controlled_combo_box.toolTip() == 'Select the controlled vocabulary.', "controlled_combo_box should have right tooltip"
      controlled_combo_box_items = [controlled_combo_box.itemText(i) for i in range(controlled_combo_box.count())]
      assert controlled_combo_box_items == ['Agricultural Sciences', 'Business and Management', 'Engineering',
                                            'Law'], "controlled_combo_box should have right contents"
      assert controlled_combo_box.toolTip() == 'Select the controlled vocabulary.', "controlled_combo_box should have right tooltip"
      assert controlled_combo_box.currentText() == "Agricultural Sciences", "controlled_combo_box must be selected to 'Agricultural Sciences'"
      meta_field_items = [edit_metadata_dialog.typesComboBox.itemText(i) for i in
                          range(edit_metadata_dialog.typesComboBox.count())]
      assert meta_field_items == ['Subject', 'Author', 'Dataset contact',
                                  'Ds Description'], "typesComboBox should have right contents"
      minimal_full_comboBox_items = [edit_metadata_dialog.minimalFullComboBox.itemText(i) for i in
                                     range(edit_metadata_dialog.minimalFullComboBox.count())]
      assert minimal_full_comboBox_items == ['Full', 'Minimal'], "minimalFullComboBox should have right contents"
    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(edit_metadata_dialog.buttonBox.Cancel), Qt.LeftButton)

  @pytest.mark.parametrize("test_id, metadata_block, expected_fields, selected_field",
                           [  # Success tests with various realistic test values
                             ("success_case_1", "Citation Metadata", ['Title',
                                                                      'Subtitle',
                                                                      'Alternative Title',
                                                                      'Alternative URL',
                                                                      'Other Id',
                                                                      'Author',
                                                                      'Dataset Contact',
                                                                      'Ds Description',
                                                                      'Subject',
                                                                      'Keyword',
                                                                      'Topic Classification',
                                                                      'Publication',
                                                                      'Notes Text',
                                                                      'Language',
                                                                      'Producer',
                                                                      'Production Date',
                                                                      'Production Place',
                                                                      'Contributor',
                                                                      'Grant Number',
                                                                      'Distributor',
                                                                      'Distribution Date',
                                                                      'Depositor',
                                                                      'Date Of Deposit',
                                                                      'Time Period Covered',
                                                                      'Date Of Collection',
                                                                      'Kind Of Data',
                                                                      'Series',
                                                                      'Software',
                                                                      'Related Material',
                                                                      'Related Datasets',
                                                                      'Other References',
                                                                      'Data Sources',
                                                                      'Origin Of Sources',
                                                                      'Characteristic Of Sources',
                                                                      'Access To Sources'], 'Title'),
                             ("success_case_2", "Geospatial Metadata",
                              ['Geographic Coverage', 'Geographic Unit', 'Geographic Bounding Box'], 'Geographic Coverage'),
                             ("success_case_3", "Social Science and Humanities Metadata", [], 'Author'),
                             ("success_case_4", "Astronomy and Astrophysics Metadata", [], 'Author'),
                             ("success_case_4", "Life Sciences Metadata", [], 'Author'),
                             ("success_case_4", "Journal Metadata", [], 'Author'),
                           ])
  def test_change_metadata_block_to_different_selection_should_update_the_ui_correctly(self, qtbot,
                                                                                       edit_metadata_dialog, test_id,
                                                                                       metadata_block, expected_fields,
                                                                                       selected_field):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      assert edit_metadata_dialog.metadataBlockComboBox.isVisible(), "EditMetadataDialog metadataBlockComboBox should be shown!"

      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, metadata_block, delay=1)
      assert edit_metadata_dialog.typesComboBox.isVisible(), "EditMetadataDialog typesComboBox should be shown!"
      assert edit_metadata_dialog.licenseURLLineEdit.isVisible(), "EditMetadataDialog licenseURLLineEdit should be shown!"
      assert edit_metadata_dialog.licenseNameLineEdit.isVisible(), "EditMetadataDialog licenseNameLineEdit should be shown!"
      assert edit_metadata_dialog.licenseNameLineEdit.text() == "CC0 1.0", "licenseNameLineEdit must be initialized with default 'CC0 1.0' option"
      assert edit_metadata_dialog.licenseURLLineEdit.text() == "http://creativecommons.org/publicdomain/zero/1.0", "licenseURLLineEdit must be initialized with default 'http://creativecommons.org/publicdomain/zero/1.0' option"
      meta_field_items = [edit_metadata_dialog.typesComboBox.itemText(i) for i in
                          range(edit_metadata_dialog.typesComboBox.count())]
      assert meta_field_items == expected_fields, "typesComboBox should have right contents"
      assert edit_metadata_dialog.typesComboBox.currentText() == selected_field, f"typesComboBox must be initialized with default '{selected_field}' option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      compound_Horizontal_Layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QHBoxLayout,
        "compoundHorizontalLayout")
      assert compound_Horizontal_Layout, "EditMetadataDialog compound_Horizontal_Layout should be present!"
      tooltips = ['Enter the Country value here. e.g. Afghanistan',
                  'Enter the State value here. e.g. GeographicCoverageStateProvince1',
                  'Enter the City value here. e.g. GeographicCoverageCity1',
                  'Enter the Other Geographic Coverage value here. e.g. GeographicCoverageOther1',
                  'Delete this particular entry.']
      for i in range(compound_Horizontal_Layout.count()):
        widget = compound_Horizontal_Layout.itemAt(i).widget()
        assert widget.isEnabled(), f"EditMetadataDialog compound_Horizontal_Layout {widget.getObjectName()} should be enabled!"
        assert widget.isVisible(), f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should be shown!"
        assert widget.toolTip() == tooltips[
          i], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right tooltip!"
      assert widget.text() == "Delete", "EditMetadataDialog compound_Horizontal_Layout widget should have right text!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog compound_Horizontal_Layout addPushButton should be disabled!"

      # Select 'Social Science and Humanities Metadata' and check if other fields are updated correctly
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Citation Metadata", delay=2)
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Astronomy and Astrophysics Metadata", delay=10)
      assert edit_metadata_dialog.typesComboBox.isVisible(), "EditMetadataDialog typesComboBox should be shown!"
      assert edit_metadata_dialog.licenseURLLineEdit.isVisible(), "EditMetadataDialog licenseURLLineEdit should be shown!"
      assert edit_metadata_dialog.licenseNameLineEdit.isVisible(), "EditMetadataDialog licenseNameLineEdit should be shown!"
      assert edit_metadata_dialog.typesComboBox.currentText() == "Geographic Coverage", "typesComboBox must be initialized with default 'Geographic Coverage' option"
      assert edit_metadata_dialog.licenseNameLineEdit.text() == "CC0 1.0", "licenseNameLineEdit must be initialized with default 'CC0 1.0' option"
      assert edit_metadata_dialog.licenseURLLineEdit.text() == "http://creativecommons.org/publicdomain/zero/1.0", "licenseURLLineEdit must be initialized with default 'http://creativecommons.org/publicdomain/zero/1.0' option"
      meta_field_items = [edit_metadata_dialog.typesComboBox.itemText(i) for i in
                          range(edit_metadata_dialog.typesComboBox.count())]
      assert meta_field_items == ['Geographic Coverage', 'Geographic Unit',
                                  'Geographic Bounding Box'], "typesComboBox should have right contents"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      compound_Horizontal_Layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QHBoxLayout,
        "compoundHorizontalLayout")
      assert compound_Horizontal_Layout, "EditMetadataDialog compound_Horizontal_Layout should be present!"
      tooltips = ['Enter the Country value here. e.g. Afghanistan',
                  'Enter the State value here. e.g. GeographicCoverageStateProvince1',
                  'Enter the City value here. e.g. GeographicCoverageCity1',
                  'Enter the Other Geographic Coverage value here. e.g. GeographicCoverageOther1',
                  'Delete this particular entry.']
      for i in range(compound_Horizontal_Layout.count()):
        widget = compound_Horizontal_Layout.itemAt(i).widget()
        assert widget.isEnabled(), f"EditMetadataDialog compound_Horizontal_Layout {widget.getObjectName()} should be enabled!"
        assert widget.isVisible(), f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should be shown!"
        assert widget.toolTip() == tooltips[
          i], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right tooltip!"
      assert widget.text() == "Delete", "EditMetadataDialog compound_Horizontal_Layout widget should have right text!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog compound_Horizontal_Layout addPushButton should be disabled!"
    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(edit_metadata_dialog.buttonBox.Cancel), Qt.LeftButton)
