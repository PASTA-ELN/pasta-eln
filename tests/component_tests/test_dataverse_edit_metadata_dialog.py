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
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import QDialogButtonBox, QHBoxLayout, QVBoxLayout

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

  @pytest.mark.parametrize("test_id, metadata_block, expected_fields, selected_field, tooltips, placeholderTexts",
                           [  # Success tests with various realistic test values
                             ("success_case_select_citation_metadata", "Citation Metadata", ['Title',
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
                                                                                             'Access To Sources'],
                              'Title',
                              ['Enter the Title value here. e.g. Replication Data for: Title',
                               'Delete this particular entry.'], [
                                'Enter the Title here.'
                              ]),
                             ("success_case_select_geospatial_metadata", "Geospatial Metadata",
                              ['Geographic Coverage', 'Geographic Unit', 'Geographic Bounding Box'],
                              'Geographic Coverage',
                              ['Enter the Country value here. e.g. Afghanistan',
                               'Enter the State value here. e.g. GeographicCoverageStateProvince1',
                               'Enter the City value here. e.g. GeographicCoverageCity1',
                               'Enter the Other Geographic Coverage value here. e.g. GeographicCoverageOther1',
                               'Delete this particular entry.'],
                              ['Enter the Country here.',
                               'Enter the State here.',
                               'Enter the City here.',
                               'Enter the Other Geographic Coverage here.',
                               'Delete this particular entry.']),
                             ("success_case_select_social_science_metadata", "Social Science and Humanities Metadata", [
                               'Unit Of Analysis',
                               'Universe',
                               'Time Method',
                               'Data Collector',
                               'Collector Training',
                               'Frequency Of Data Collection',
                               'Sampling Procedure',
                               'Target Sample Size',
                               'Deviations From Sample Design',
                               'Collection Mode',
                               'Research Instrument',
                               'Data Collection Situation',
                               'Actions To Minimize Loss',
                               'Control Operations',
                               'Weighting',
                               'Cleaning Operations',
                               'Dataset Level Error Notes',
                               'Response Rate',
                               'Sampling Error Estimates',
                               'Other Data Appraisal',
                               'Social Science Notes',
                             ], 'Unit Of Analysis', [
                                'Enter the Unit Of Analysis value here. e.g. UnitOfAnalysis1',
                                'Delete this particular entry.'
                              ], [
                                'Enter the Unit Of Analysis here.',
                                'Delete this particular entry.'
                              ]),
                             ("success_case_select_astronomy_metadata", "Astronomy and Astrophysics Metadata",
                              ['Astro Type',
                               'Astro Facility',
                               'Astro Instrument',
                               'Astro Object',
                               'Resolution Spatial',
                               'Resolution Spectral',
                               'Resolution Temporal',
                               'Coverage Spectral Bandpass',
                               'Coverage Spectral Central Wavelength',
                               'Coverage Spectral Wavelength',
                               'Coverage Temporal',
                               'Coverage Spatial',
                               'Coverage Depth',
                               'Coverage Object Density',
                               'Coverage Object Count',
                               'Coverage Sky Fraction',
                               'Coverage Polarization',
                               'Redshift Type',
                               'Resolution Redshift',
                               'Coverage Redshift Value'],
                              'Astro Type',
                              ['Select the controlled vocabulary.', 'Delete this particular vocabulary entry.'], []),
                             ("success_case_life_sciences_metadata", "Life Sciences Metadata", ['Study Design Type',
                                                                                                'Study Factor Type',
                                                                                                'Study Assay Organism',
                                                                                                'Study Assay Other Organism',
                                                                                                'Study Assay Measurement Type',
                                                                                                'Study Assay Other Measurment Type',
                                                                                                'Study Assay Technology Type',
                                                                                                'Study Assay Platform',
                                                                                                'Study Assay Cell Type'],
                              'Study Design Type',
                              ['Select the controlled vocabulary.', 'Delete this particular vocabulary entry.'], []),
                             ("success_case_journal_metadata", "Journal Metadata",
                              ['Journal Volume Issue', 'Journal Article Type'],
                              'Journal Volume Issue', ['Enter the Journal Volume value here. e.g. JournalVolume1',
                                                       'Enter the Journal Issue value here. e.g. JournalIssue1',
                                                       'Enter the Journal Pub Date value here. e.g. 1008-01-01',
                                                       'Delete this particular entry.'],
                              ['Enter the Journal Volume here.', 'Enter the Journal Issue here.',
                               'Delete this particular entry.']),
                           ])
  def test_change_metadata_block_to_different_selection_should_update_the_ui_correctly(self, qtbot,
                                                                                       edit_metadata_dialog,
                                                                                       test_id,
                                                                                       metadata_block,
                                                                                       expected_fields,
                                                                                       selected_field,
                                                                                       tooltips,
                                                                                       placeholderTexts):
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
      if test_id == "success_case_select_geospatial_metadata":
        assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
        assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
        compound_Horizontal_Layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
          QHBoxLayout,
          "compoundHorizontalLayout")
        assert compound_Horizontal_Layout, "EditMetadataDialog compound_Horizontal_Layout should be present!"
        for i in range(compound_Horizontal_Layout.count()):
          widget = compound_Horizontal_Layout.itemAt(i).widget()
          assert widget.isEnabled(), f"EditMetadataDialog compound_Horizontal_Layout {widget.objectName()} should be enabled!"
          assert widget.isVisible(), f"EditMetadataDialog primitive_compound_frame {widget.objectName()} should be shown!"
          assert widget.toolTip() == tooltips[
            i], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right tooltip!"
          if widget.objectName().lower().endswith("lineedit"):
            assert widget.placeholderText() == placeholderTexts[
              i], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right placeholderText!"
        assert widget.text() == "Delete", "EditMetadataDialog compound_Horizontal_Layout widget should have right text!"
        assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog compound_Horizontal_Layout addPushButton should be disabled!"
      elif test_id == "success_case_select_citation_metadata":
        assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
        assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
        assert not edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should not be enabled!"
        primitive_horizontal_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
          QHBoxLayout,
          "primitiveHorizontalLayout")
        for i in range(primitive_horizontal_layout.count()):
          widget = primitive_horizontal_layout.itemAt(i).widget()
          assert not widget.isEnabled() if widget.objectName().lower().endswith(
            "button") else widget.isEnabled(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should not be enabled!"
          assert widget.isVisible(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should be shown!"
          assert widget.toolTip() == tooltips[
            i], f"EditMetadataDialog primitive_compound_frame {widget.objectName()} should have right tooltip!"
          if widget.objectName().lower().endswith("lineedit"):
            assert widget.placeholderText() == placeholderTexts[
              i], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right placeholderText!"
      elif test_id == "success_case_select_social_science_metadata":
        assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
        assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
        assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be enabled!"
        primitive_horizontal_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
          QHBoxLayout,
          "primitiveHorizontalLayout")
        for i in range(primitive_horizontal_layout.count()):
          widget = primitive_horizontal_layout.itemAt(i).widget()
          assert widget.isEnabled(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should be enabled!"
          assert widget.isVisible(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should be shown!"
          assert widget.toolTip() == tooltips[
            i], f"EditMetadataDialog primitive_compound_frame {widget.objectName()} should have right tooltip!"
          if widget.objectName().lower().endswith("lineedit"):
            assert widget.placeholderText() == placeholderTexts[
              i], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right placeholderText!"
      elif test_id == "success_case_select_astronomy_metadata" or test_id == "success_case_life_sciences_metadata":
        assert edit_metadata_dialog.controlled_vocab_frame, "EditMetadataDialog controlled_vocab_frame should be present!"
        assert edit_metadata_dialog.controlled_vocab_frame.addPushButton.isVisible(), "EditMetadataDialog controlled_vocab_frame addPushButton should be shown!"
        assert edit_metadata_dialog.controlled_vocab_frame.addPushButton.isEnabled(), "EditMetadataDialog controlled_vocab_frame addPushButton should be enabled!"
        vocab_horizontal_layout = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.findChild(
          QHBoxLayout,
          "vocabHorizontalLayout")
        assert vocab_horizontal_layout, "EditMetadataDialog vocab_horizontal_layout should be present!"
        for i in range(vocab_horizontal_layout.count()):
          widget = vocab_horizontal_layout.itemAt(i).widget()
          assert widget.isEnabled(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should be enabled!"
          assert widget.isVisible(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should be shown!"
          assert widget.toolTip() == tooltips[
            i], f"EditMetadataDialog primitive_compound_frame {widget.objectName()} should have right tooltip!"
          if widget.objectName().lower().endswith("combobox"):
            assert [widget.itemText(i) for i in
                    range(widget.count())] == ['Image', 'Mosaic', 'EventList',
                                               'Cube'] if test_id == "success_case_select_astronomy_metadata" else [
              'Case Control', 'Cross Sectional', 'Cohort Study',
              'Not Specified'], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right contents!"
      elif test_id == "success_case_journal_metadata":
        assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
        assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
        assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be enabled!"
        primitive_horizontal_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
          QHBoxLayout,
          "compoundHorizontalLayout")
        assert primitive_horizontal_layout, "EditMetadataDialog primitive_horizontal_layout should be present!"
        for i in range(primitive_horizontal_layout.count()):
          widget = primitive_horizontal_layout.itemAt(i).widget()
          assert widget.isEnabled(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should be enabled!"
          assert widget.isVisible(), f"EditMetadataDialog primitive_horizontal_layout {widget.objectName()} should be shown!"
          assert widget.toolTip() == tooltips[
            i], f"EditMetadataDialog primitive_compound_frame {widget.objectName()} should have right tooltip!"
          if widget.objectName().lower().endswith("lineedit"):
            assert widget.placeholderText() == placeholderTexts[
              i], f"EditMetadataDialog primitive_compound_frame {widget.getObjectName()} should have right placeholderText!"

  def test_add_field_primitive_single_type_and_save_click_should_do_as_expected(self, qtbot, edit_metadata_dialog,
                                                                                mock_database_api):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Citation Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Citation Metadata", "metadataBlockComboBox must be initialized with  citation metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Origin Of Sources', delay=1)
      assert edit_metadata_dialog.typesComboBox.currentText() == "Origin Of Sources", "typesComboBox must be initialized with Origin Of Sources option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      assert not edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should not be enabled!"
      primitive_horizontal_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QHBoxLayout,
        "primitiveHorizontalLayout")
      assert primitive_horizontal_layout, "EditMetadataDialog primitive_horizontal_layout should be present!"
      line_edit = primitive_horizontal_layout.itemAt(0).widget()
      assert line_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
      assert line_edit.isVisible(), "EditMetadataDialog primitive_compound_frame line_edit should be shown!"
      assert line_edit.toolTip() == 'Enter the Origin Of Sources value here. e.g. OriginOfSources', "EditMetadataDialog primitive_compound_frame line_edit should have right tooltip!"
      assert line_edit.placeholderText() == 'Enter the Origin Of Sources here.', "EditMetadataDialog primitive_compound_frame line_edit should have right placeholderText!"
      delete_button = primitive_horizontal_layout.itemAt(1).widget()
      assert not delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete_button should not be enabled!"
      assert delete_button.isVisible(), "EditMetadataDialog primitive_compound_frame delete_button should be shown!"
      assert delete_button.toolTip() == 'Delete this particular entry.', "EditMetadataDialog primitive_compound_frame delete_button should have right tooltip!"

      line_edit.setText("test data...")
    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['citation']['fields'][32][
             'value'] == 'test data...'
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  @pytest.mark.parametrize("test_id, test_data, expected_data",
                           [  # Success tests with various realistic test values
                             ("success_case_multiple_data",
                              ["Kind Of Data1", "Kind Of Data2", "Kind Of Data3", "Kind Of Data4"],
                              ["Kind Of Data1", "Kind Of Data2", "Kind Of Data3", "Kind Of Data4"]),
                             ("success_case_multiple_data_with_empty_entries",
                              ["Kind Of Data1", "", None, "Kind Of Data4"], ["Kind Of Data1", "Kind Of Data4"]),
                             ("success_case_multiple_data_with_all_empty_entries", ["", "", None, ""], [])
                           ])
  def test_add_field_primitive_multiple_type_and_save_click_should_do_as_expected(self,
                                                                                  qtbot,
                                                                                  edit_metadata_dialog,
                                                                                  mock_database_api,
                                                                                  test_id,
                                                                                  test_data,
                                                                                  expected_data):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Citation Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Citation Metadata", "metadataBlockComboBox must be initialized with  citation metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Kind Of Data', delay=1)
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Kind Of Data', "typesComboBox must be initialized with 'Kind Of Data' option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be enabled!"

      primitive_vertical_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QVBoxLayout,
        "primitiveVerticalLayout")
      assert primitive_vertical_layout, "EditMetadataDialog primitive_vertical_layout should be present!"
      assert primitive_vertical_layout.count() == 1, "EditMetadataDialog primitive_vertical_layout should have 1 child!"
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      assert primitive_vertical_layout.count() == 4, "EditMetadataDialog primitive_vertical_layout should have 4 children!"
      for pos in range(primitive_vertical_layout.count()):
        line_edit = primitive_vertical_layout.itemAt(pos).itemAt(0).widget()
        assert line_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert line_edit.toolTip() == 'Enter the Kind Of Data value here. e.g. KindOfData1', "EditMetadataDialog primitive_compound_frame line_edit should have right tooltip!"
        assert line_edit.placeholderText() == 'Enter the Kind Of Data here.', "EditMetadataDialog primitive_compound_frame line_edit should have right placeholderText!"
        delete_button = primitive_vertical_layout.itemAt(pos).itemAt(1).widget()
        assert delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete_button should be enabled!"
        assert delete_button.toolTip() == 'Delete this particular entry.', "EditMetadataDialog primitive_compound_frame delete_button should have right tooltip!"
        line_edit.setText(test_data[pos])

    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['citation']['fields'][25][
             'value'] == expected_data
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  def test_delete_field_primitive_multiple_type_and_save_click_should_do_as_expected(self,
                                                                                     qtbot,
                                                                                     edit_metadata_dialog,
                                                                                     mock_database_api):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Citation Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Citation Metadata", "metadataBlockComboBox must be initialized with  citation metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Kind Of Data', delay=1)
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Kind Of Data', "typesComboBox must be initialized with 'Kind Of Data' option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be enabled!"

      primitive_vertical_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QVBoxLayout,
        "primitiveVerticalLayout")
      assert primitive_vertical_layout, "EditMetadataDialog primitive_vertical_layout should be present!"
      assert primitive_vertical_layout.count() == 1, "EditMetadataDialog primitive_vertical_layout should have 1 child!"
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      assert primitive_vertical_layout.count() == 4, "EditMetadataDialog primitive_vertical_layout should have 4 children!"
      test_data = ["KindOfData1", "KindOfData2", "KindOfData3", "KindOfData4"]
      for pos in range(primitive_vertical_layout.count()):
        line_edit = primitive_vertical_layout.itemAt(pos).itemAt(0).widget()
        assert line_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert line_edit.toolTip() == 'Enter the Kind Of Data value here. e.g. KindOfData1', "EditMetadataDialog primitive_compound_frame line_edit should have right tooltip!"
        assert line_edit.placeholderText() == 'Enter the Kind Of Data here.', "EditMetadataDialog primitive_compound_frame line_edit should have right placeholderText!"
        delete_button = primitive_vertical_layout.itemAt(pos).itemAt(1).widget()
        assert delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete_button should be enabled!"
        assert delete_button.toolTip() == 'Delete this particular entry.', "EditMetadataDialog primitive_compound_frame delete_button should have right tooltip!"
        line_edit.setText(test_data[pos])
      # Delete two populated items
      qtbot.mouseClick(primitive_vertical_layout.itemAt(1).itemAt(1).widget(), Qt.LeftButton)
      assert primitive_vertical_layout.count() == 3, "EditMetadataDialog primitive_vertical_layout should have 3 children!"
      qtbot.mouseClick(primitive_vertical_layout.itemAt(2).itemAt(1).widget(), Qt.LeftButton)
      assert primitive_vertical_layout.count() == 2, "EditMetadataDialog primitive_vertical_layout should have 2 children!"

    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['citation']['fields'][25][
             'value'] == ["KindOfData1", "KindOfData3"]
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  def test_add_field_compound_single_type_and_save_click_should_do_as_expected(self,
                                                                               qtbot,
                                                                               edit_metadata_dialog,
                                                                               mock_database_api):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Social Science and Humanities Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Social Science and Humanities Metadata", "metadataBlockComboBox must be initialized with  Social Science and Humanities Metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Target Sample Size', delay=1)
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Target Sample Size', "typesComboBox must be initialized with 'Target Sample Size' option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      assert not edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should not be enabled!"

      compound_horizontal_layout = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.findChild(
        QHBoxLayout,
        "compoundHorizontalLayout")
      assert compound_horizontal_layout, "EditMetadataDialog compound_horizontal_layout should be present!"
      line_edit1 = compound_horizontal_layout.itemAt(0).widget()
      assert line_edit1.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
      assert line_edit1.toolTip() == 'Enter the Target Sample Actual Size value here. e.g. 100', "EditMetadataDialog compound_horizontal_layout line_edit should have right tooltip!"
      assert line_edit1.placeholderText() == 'Enter the Target Sample Actual Size here.', "EditMetadataDialog compound_horizontal_layout line_edit should have right placeholderText!"
      line_edit2 = compound_horizontal_layout.itemAt(1).widget()
      assert line_edit2.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
      assert line_edit2.toolTip() == 'Enter the Target Sample Size Formula value here. e.g. TargetSampleSizeFormula', "EditMetadataDialog compound_horizontal_layout line_edit should have right tooltip!"
      assert line_edit2.placeholderText() == 'Enter the Target Sample Size Formula here.', "EditMetadataDialog compound_horizontal_layout line_edit should have right placeholderText!"
      delete_button = compound_horizontal_layout.itemAt(2).widget()
      assert not delete_button.isEnabled(), "EditMetadataDialog compound_horizontal_layout delete_button should not be enabled!"
      assert delete_button.toolTip() == 'Delete this particular entry.', "EditMetadataDialog compound_horizontal_layout delete_button should have right tooltip!"
      line_edit1.setText("targetSampleSize")
      line_edit2.setText("targetSampleSizeFormula")

    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['socialscience']['fields'][7][
             'value']['targetSampleActualSize']['value'] == "targetSampleSize"
    assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['socialscience']['fields'][7][
             'value']['targetSampleSizeFormula']['value'] == "targetSampleSizeFormula"
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  @pytest.mark.parametrize("test_id, test_data, expected_data",
                           [  # Success tests with various realistic test values
                             ("success_case_multiple_data",
                              [("Description1", "2024-01-01"), ("Description2", "2024-01-23"),
                               ("Description3", "2024-01-23"), ("Description4", "2024-01-23")],
                              [("Description1", "2024-01-01"), ("Description2", "2024-01-23"),
                               ("Description3", "2024-01-23"), ("Description4", "2024-01-23")]),
                             ("success_case_multiple_data_with_none",
                              [("Description1", None), (None, "2024-01-23"),
                               ("", "2024-01-23"), ("Description4", "2024-01-23")],
                              [("Description1", '2000-01-01'), ("", "2024-01-23"),
                               ("", "2024-01-23"), ("Description4", "2024-01-23")]),
                             ("success_case_multiple_data_with_none",
                              [("", None), (None, ""),
                               ("", ""), ("", "2024-01-23")],
                              [("", '2000-01-01'), ("", "2000-01-01"),
                               ("", "2000-01-01"), ("", "2024-01-23")]),
                           ])
  def test_add_field_compound_multiple_type_and_save_click_should_do_as_expected(self,
                                                                                 qtbot,
                                                                                 edit_metadata_dialog,
                                                                                 mock_database_api,
                                                                                 test_id,
                                                                                 test_data,
                                                                                 expected_data):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Citation Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Citation Metadata", "metadataBlockComboBox must be initialized with  citation metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Ds Description', delay=1)
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Ds Description', "typesComboBox must be initialized with 'Ds Description' option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be enabled!"

      assert edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count() == 2, "EditMetadataDialog primitive_vertical_layout should have 2 children!"
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      assert edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count() == 5, "EditMetadataDialog primitive_vertical_layout should have 5 children!"
      for pos in range(1, edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count()):
        line_edit = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(0).widget()
        assert line_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert line_edit.toolTip() == 'Enter the Ds Description Value value here. e.g. DescriptionText1', "EditMetadataDialog primitive_compound_frame line_edit should have right tooltip!"
        assert line_edit.placeholderText() == 'Enter the Ds Description Value here.', "EditMetadataDialog primitive_compound_frame line_edit should have right placeholderText!"
        date_time_edit = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(1).widget()
        assert date_time_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert date_time_edit.toolTip() == 'Enter the Ds Description Date value here. e.g. 1000-01-01', "EditMetadataDialog primitive_compound_frame date_time_edit should have right tooltip!"
        delete_button = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(2).widget()
        assert delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete_button should be enabled!"
        assert delete_button.toolTip() == 'Delete this particular entry.', "EditMetadataDialog primitive_compound_frame delete_button should have right tooltip!"
        line_edit.setText(test_data[pos - 1][0])
        date_time_edit.setDateTime(QDateTime.fromString(test_data[pos - 1][1], 'yyyy-MM-dd'))

    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    for pos in range(len(expected_data)):
      assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['citation']['fields'][7][
               'value'][pos]['dsDescriptionValue']['value'] == expected_data[pos][0]
    assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['citation']['fields'][7][
             'value'][pos]['dsDescriptionDate']['value'] == expected_data[pos][1]
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  def test_delete_fields_compound_multiple_type_and_save_click_should_do_as_expected(self,
                                                                                     qtbot,
                                                                                     edit_metadata_dialog,
                                                                                     mock_database_api):
    edit_metadata_dialog.show()
    test_data = [("Description1", "2024-01-01"), ("Description2", "2024-01-23"),
                 ("Description3", "2024-01-23"), ("Description4", "2024-01-23")]
    expected_data = [("Description3", "2024-01-23"), ("Description4", "2024-01-23")]
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Citation Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Citation Metadata", "metadataBlockComboBox must be initialized with  citation metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Ds Description', delay=1)
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Ds Description', "typesComboBox must be initialized with 'Ds Description' option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be enabled!"

      assert edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count() == 2, "EditMetadataDialog primitive_vertical_layout should have 2 children!"
      # Add three entries
      for _ in range(3):
        qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.addPushButton, Qt.LeftButton)
      assert edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count() == 5, "EditMetadataDialog primitive_vertical_layout should have 5 children!"
      for pos in range(1, edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count()):
        line_edit = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(0).widget()
        assert line_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert line_edit.toolTip() == 'Enter the Ds Description Value value here. e.g. DescriptionText1', "EditMetadataDialog primitive_compound_frame line_edit should have right tooltip!"
        assert line_edit.placeholderText() == 'Enter the Ds Description Value here.', "EditMetadataDialog primitive_compound_frame line_edit should have right placeholderText!"
        date_time_edit = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(1).widget()
        assert date_time_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert date_time_edit.toolTip() == 'Enter the Ds Description Date value here. e.g. 1000-01-01', "EditMetadataDialog primitive_compound_frame date_time_edit should have right tooltip!"
        delete_button = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(2).widget()
        assert delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete_button should be enabled!"
        assert delete_button.toolTip() == 'Delete this particular entry.', "EditMetadataDialog primitive_compound_frame delete_button should have right tooltip!"
        line_edit.setText(test_data[pos - 1][0])
        date_time_edit.setDateTime(QDateTime.fromString(test_data[pos - 1][1], 'yyyy-MM-dd'))

      # Delete two populated items
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(1).itemAt(2).widget(),
                       Qt.LeftButton)
      assert edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count() == 4, "EditMetadataDialog primitive_vertical_layout should have 4 children!"
      qtbot.mouseClick(edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(1).itemAt(2).widget(),
                       Qt.LeftButton)
      assert edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count() == 3, "EditMetadataDialog primitive_vertical_layout should have 3 children!"

    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    for pos in range(len(expected_data)):
      assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['citation']['fields'][7][
               'value'][pos]['dsDescriptionValue']['value'] == expected_data[pos][0]
    assert edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['citation']['fields'][7][
             'value'][pos]['dsDescriptionDate']['value'] == expected_data[pos][1]
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  def test_add_field_controlled_type_and_save_click_should_do_as_expected(self, qtbot, edit_metadata_dialog,
                                                                          mock_database_api):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Life Sciences Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Life Sciences Metadata", "metadataBlockComboBox must be initialized with Life Sciences Metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Study Factor Type', delay=10)
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Study Factor Type', "typesComboBox must be initialized with Study Factor Type option"
      assert not edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should not be shown!"
      assert edit_metadata_dialog.controlled_vocab_frame.instance.isVisible(), "EditMetadataDialog controlled_vocab_frame should be shown!"
      assert edit_metadata_dialog.controlled_vocab_frame.addPushButton.isVisible(), "EditMetadataDialog controlled_vocab_frame addPushButton should be shown!"
      assert edit_metadata_dialog.controlled_vocab_frame.addPushButton.isEnabled(), "EditMetadataDialog controlled_vocab_frame addPushButton should be enabled!"
      assert edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count() == 2, "EditMetadataDialog controlled_vocab_frame mainVerticalLayout should contain 2 children!"
      combo_box_items = ['Age', 'Biomarkers', 'Cell Surface Markers', 'Developmental Stage']
      combo_box = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(1).itemAt(0).widget()
      assert combo_box.isEnabled(), "EditMetadataDialog controlled_vocab_frame combo_box should be enabled!"
      assert combo_box.toolTip() == 'Select the controlled vocabulary.', "EditMetadataDialog controlled_vocab_frame combo_box should have right tooltip!"
      assert [combo_box.itemText(i) for i in range(
        combo_box.count())] == combo_box_items, "EditMetadataDialog controlled_vocab_frame combo_box should have right options!"
      assert combo_box.currentText() == 'Age', "EditMetadataDialog controlled_vocab_frame combo_box should have right default value!"
      delete_button = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(1).itemAt(1).widget()
      assert delete_button.isEnabled(), "EditMetadataDialog controlled_vocab_frame delete_button should be enabled!"
      assert delete_button.toolTip() == 'Delete this particular vocabulary entry.', "EditMetadataDialog controlled_vocab_frame delete_button should have right tooltip!"

      # Add new field items
      for _ in range(3):
        qtbot.mouseClick(edit_metadata_dialog.controlled_vocab_frame.addPushButton,
                         Qt.LeftButton)

      # Check if the new field items are added in UI
      assert edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count() == 5, "EditMetadataDialog controlled_vocab_frame mainVerticalLayout should contain 5 children!"
      for pos in range(1, edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count()):
        combo_box = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(pos).itemAt(0).widget()
        assert combo_box.isEnabled(), "EditMetadataDialog controlled_vocab_frame combo_box should be enabled!"
        assert combo_box.toolTip() == 'Select the controlled vocabulary.', "EditMetadataDialog controlled_vocab_frame combo_box should have right tooltip!"
        assert [combo_box.itemText(i) for i in range(
          combo_box.count())] == combo_box_items, "EditMetadataDialog controlled_vocab_frame combo_box should have right options!"
        assert combo_box.currentText() == 'Age', "EditMetadataDialog controlled_vocab_frame combo_box should have right default value!"
        delete_button = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(pos).itemAt(1).widget()
        assert delete_button.isEnabled(), "EditMetadataDialog controlled_vocab_frame delete_button should be enabled!"
        assert delete_button.toolTip() == 'Delete this particular vocabulary entry.', "EditMetadataDialog controlled_vocab_frame delete_button should have right tooltip!"

      # Set combo box items
      for i in range(4):
        qtbot.keyClicks(edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(i + 1).itemAt(0).widget(),
                        combo_box_items[i], delay=1)

      # Check if combo box items are updated in UI
      for pos in range(1, edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count()):
        combo_box = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(pos).itemAt(0).widget()
        assert combo_box.currentText() == combo_box_items[
          pos - 1], "EditMetadataDialog controlled_vocab_frame combo_box should have right default value!"

    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    value = edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['biomedical']['fields'][1]['value']
    value.sort()
    assert value == combo_box_items, "EditMetadataDialog field value should be updated!"
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  def test_delete_field_controlled_type_and_save_click_should_do_as_expected(self, qtbot, edit_metadata_dialog,
                                                                             mock_database_api):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Life Sciences Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Life Sciences Metadata", "metadataBlockComboBox must be initialized with Life Sciences Metadata option"
      qtbot.keyClicks(edit_metadata_dialog.typesComboBox, 'Study Factor Type', delay=10)
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Study Factor Type', "typesComboBox must be initialized with Study Factor Type option"
      assert edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count() == 2, "EditMetadataDialog controlled_vocab_frame mainVerticalLayout should contain 2 children!"
      combo_box_items = ['Age', 'Biomarkers', 'Cell Surface Markers', 'Developmental Stage']

      # Add new field items
      for _ in range(3):
        qtbot.mouseClick(edit_metadata_dialog.controlled_vocab_frame.addPushButton,
                         Qt.LeftButton)

      assert edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count() == 5, "EditMetadataDialog controlled_vocab_frame mainVerticalLayout should contain 5 children!"

      # Set combo box items
      for i in range(4):
        qtbot.keyClicks(edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(i + 1).itemAt(0).widget(),
                        combo_box_items[i], delay=1)
      for pos in range(1, edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count()):
        combo_box = edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(pos).itemAt(0).widget()
        assert combo_box.currentText() == combo_box_items[
          pos - 1], "EditMetadataDialog controlled_vocab_frame combo_box should have right default value!"

      # Delete first two combo box items
      qtbot.mouseClick(edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(1).itemAt(1).widget(),
                       Qt.LeftButton)
      qtbot.mouseClick(edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.itemAt(1).itemAt(1).widget(),
                       Qt.LeftButton)
      assert edit_metadata_dialog.controlled_vocab_frame.mainVerticalLayout.count() == 3, "EditMetadataDialog controlled_vocab_frame mainVerticalLayout should contain 3 children!"

    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    value = edit_metadata_dialog.metadata['datasetVersion']['metadataBlocks']['biomedical']['fields'][1]['value']
    value.sort()
    assert value == combo_box_items[2:], "EditMetadataDialog field value should be updated!"
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  def test_if_data_loaded_is_populated_as_expected(self, qtbot, edit_metadata_dialog,
                                                   mock_database_api):
    config_model = mock_database_api.get_model.return_value
    journal_volume_test_data = [
      ("JournalVolumeTest1", "JournalIssueTest1", "2024-12-01"),
      ("JournalVolumeTest2", "JournalIssueTest2", "2014-12-01"),
      ("JournalVolumeTest3", "JournalIssueTest3", "2007-01-01"),
      ("JournalVolumeTest4", "JournalIssueTest4", "1997-03-01"),
    ]
    config_model.metadata['datasetVersion']['metadataBlocks']['journal']['fields'][0]['value'] = [
      {
        "journalVolume": {
          "typeName": "journalVolume",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[0][0]
        },
        "journalIssue": {
          "typeName": "journalIssue",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[0][1]
        },
        "journalPubDate": {
          "typeName": "journalPubDate",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[0][2]
        }
      },
      {
        "journalVolume": {
          "typeName": "journalVolume",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[1][0]
        },
        "journalIssue": {
          "typeName": "journalIssue",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[1][1]
        },
        "journalPubDate": {
          "typeName": "journalPubDate",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[1][2]
        }
      },
      {
        "journalVolume": {
          "typeName": "journalVolume",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[2][0]
        },
        "journalIssue": {
          "typeName": "journalIssue",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[2][1]
        },
        "journalPubDate": {
          "typeName": "journalPubDate",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[2][2]
        }
      },
      {
        "journalVolume": {
          "typeName": "journalVolume",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[3][0]
        },
        "journalIssue": {
          "typeName": "journalIssue",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[3][1]
        },
        "journalPubDate": {
          "typeName": "journalPubDate",
          "multiple": False,
          "typeClass": "primitive",
          "value": journal_volume_test_data[3][2]
        }
      }
    ]
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      qtbot.keyClicks(edit_metadata_dialog.metadataBlockComboBox, "Journal Metadata", delay=1)
      assert edit_metadata_dialog.metadataBlockComboBox.currentText() == "Journal Metadata", "metadataBlockComboBox must be initialized with Journal Metadata option"
      assert edit_metadata_dialog.typesComboBox.currentText() == 'Journal Volume Issue', "typesComboBox must be initialized with Journal Volume Issue option"
      assert edit_metadata_dialog.primitive_compound_frame.instance.isVisible(), "EditMetadataDialog primitive_compound_frame should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isVisible(), "EditMetadataDialog primitive_compound_frame addPushButton should be shown!"
      assert edit_metadata_dialog.primitive_compound_frame.addPushButton.isEnabled(), "EditMetadataDialog primitive_compound_frame addPushButton should be enabled!"
      assert edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count() == 5, "EditMetadataDialog primitive_vertical_layout should have 5 children!"
      for pos in range(1, edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.count()):
        journal_volume_line_edit = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(
          0).widget()
        assert journal_volume_line_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert journal_volume_line_edit.toolTip() == 'Enter the Journal Volume value here. e.g. JournalVolume1', "EditMetadataDialog primitive_compound_frame journal_volume_line_edit should have right tooltip!"
        assert journal_volume_line_edit.placeholderText() == 'Enter the Journal Volume here.', "EditMetadataDialog primitive_compound_frame journal_volume_line_edit should have right placeholderText!"
        assert journal_volume_line_edit.text() == journal_volume_test_data[pos - 1][
          0], "EditMetadataDialog primitive_compound_frame journal_volume_line_edit should have right text!"
        journal_issue_line_edit = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(
          1).widget()
        assert journal_issue_line_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame journal_issue_line_edit should be enabled!"
        assert journal_issue_line_edit.toolTip() == 'Enter the Journal Issue value here. e.g. JournalIssue1', "EditMetadataDialog primitive_compound_frame journal_issue_line_edit should have right tooltip!"
        assert journal_issue_line_edit.placeholderText() == 'Enter the Journal Issue here.', "EditMetadataDialog primitive_compound_frame journal_issue_line_edit should have right placeholderText!"
        assert journal_issue_line_edit.text() == journal_volume_test_data[pos - 1][
          1], "EditMetadataDialog primitive_compound_frame journal_issue_line_edit should have right text!"
        date_time_edit = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(2).widget()
        assert date_time_edit.isEnabled(), "EditMetadataDialog primitive_compound_frame line_edit should be enabled!"
        assert date_time_edit.toolTip() == 'Enter the Journal Pub Date value here. e.g. 1008-01-01', "EditMetadataDialog primitive_compound_frame date_time_edit should have right tooltip!"
        assert date_time_edit.date().toString("yyyy-MM-dd") == journal_volume_test_data[pos - 1][
          2], "EditMetadataDialog primitive_compound_frame date_time_edit should have right text!"
        delete_button = edit_metadata_dialog.primitive_compound_frame.mainVerticalLayout.itemAt(pos).itemAt(3).widget()
        assert delete_button.isEnabled(), "EditMetadataDialog primitive_compound_frame delete_button should be enabled!"
        assert delete_button.toolTip() == 'Delete this particular entry.', "EditMetadataDialog primitive_compound_frame delete_button should have right tooltip!"
      qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)

  def test_update_license_information_and_save_should_do_as_expected(self, qtbot, edit_metadata_dialog,
                                                                     mock_database_api):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      edit_metadata_dialog.licenseNameLineEdit.setText("New License Name")
      edit_metadata_dialog.licenseURLLineEdit.setText("New License Url")
    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Save), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    assert edit_metadata_dialog.metadata['datasetVersion']['license'][
             'name'] == "New License Name", "licenseName should have right text!"
    assert edit_metadata_dialog.metadata['datasetVersion']['license'][
             'uri'] == "New License Url", "licenseURL should have right text!"
    mock_database_api.update_model_document.assert_called_once_with(edit_metadata_dialog.config_model)

  def test_update_license_information_and_cancel_should_do_as_expected(self, qtbot, edit_metadata_dialog,
                                                                       mock_database_api):
    edit_metadata_dialog.show()
    with qtbot.waitExposed(edit_metadata_dialog.instance, timeout=500):
      assert edit_metadata_dialog.minimalFullComboBox.currentText() == "Full", "minimalFullComboBox must be initialized with default full option"
      edit_metadata_dialog.licenseNameLineEdit.setText("New License Name")
      edit_metadata_dialog.licenseURLLineEdit.setText("New License Url")
    qtbot.mouseClick(edit_metadata_dialog.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert not edit_metadata_dialog.instance.isVisible(), "EditMetadataDialog instance should be closed!"
    assert edit_metadata_dialog.metadata['datasetVersion']['license'][
             'name'] == "New License Name", "licenseName should have right text!"
    assert edit_metadata_dialog.metadata['datasetVersion']['license'][
             'uri'] == "New License Url", "licenseURL should have right text!"
    mock_database_api.update_model_document.assert_not_called()
