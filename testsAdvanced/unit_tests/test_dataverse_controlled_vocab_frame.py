#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_controlled_vocab_frame.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import pytest
from _pytest.mark import param

from pasta_eln.GUI.dataverse.controlled_vocab_frame import ControlledVocabFrame
from pasta_eln.GUI.dataverse.data_type_class_names import DataTypeClassName


@pytest.fixture
def qtbot(mocker):
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QFrame')
  mocker.patch(
    'pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi')
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.logging.getLogger')
  mocker.patch.object(ControlledVocabFrame, 'addPushButton', create=True)
  mocker.patch.object(ControlledVocabFrame, 'mainVerticalLayout', create=True)
  mocker.patch.object(ControlledVocabFrame, 'meta_field', create=True)


# Fixture to create a ControlledVocabFrame instance with a mocked parent
@pytest.fixture
def controlled_vocab_frame(qtbot, mocker):
  actual_load_ui = ControlledVocabFrame.load_ui
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.ControlledVocabFrame.load_ui')
  type_field = {
    'typeClass': 'primitive',
    'multiple': False,
    'typeName': 'testType',
    'value': 'testValue',
    'valueTemplate': 'testTemplate'
  }
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.DataTypeClassFactory')
  mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.DataTypeClassContext')
  frame = ControlledVocabFrame(type_field)
  ControlledVocabFrame.load_ui = actual_load_ui
  return frame


class TestControlledVocabFrame:
  @pytest.mark.parametrize('test_id, meta_field', [
    (
        'success_multiple_values_init_primitve',
        {'multiple': True, 'typeClass': 'primitive', 'typeName': 'testType', 'value': ['entry1', 'entry2'],
         'valueTemplate': ['entry1', 'entry2', 'entry3']}),
    (
        'success_multiple_values_init_compound',
        {'multiple': True, 'typeClass': 'compound', 'typeName': 'testType', 'value': ['entry1', 'entry2'],
         'valueTemplate': ['entry1', 'entry2', 'entry3']})
  ])
  def test_init(self, mocker, qtbot, test_id, meta_field):
    # Arrange
    mock_load_ui = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.ControlledVocabFrame.load_ui')
    mock_data_type_class_factory = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.DataTypeClassFactory')
    mock_data_type_class_context = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.DataTypeClassContext')
    mock_super_setup_ui = mocker.patch(
      'pasta_eln.GUI.dataverse.primitive_compound_controlled_frame_base.Ui_PrimitiveCompoundControlledFrameBase.setupUi')
    mock_get_logger = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.logging.getLogger')
    mock_meta_frame_constructor = mocker.patch('pasta_eln.GUI.dataverse.metadata_frame_base.MetadataFrame.__init__')
    mock_frame_constructor = mocker.patch('pasta_eln.GUI.dataverse.controlled_vocab_frame.QFrame')

    # Act
    frame = ControlledVocabFrame(meta_field)

    # Assert
    assert frame is not None
    mock_get_logger.assert_called_once_with('pasta_eln.GUI.dataverse.controlled_vocab_frame.ControlledVocabFrame')
    mock_frame_constructor.assert_called_once_with()
    mock_meta_frame_constructor.assert_called_once_with(frame.instance)
    mock_super_setup_ui.assert_called_once_with(frame.instance)
    mock_data_type_class_context.assert_called_once_with(frame.mainVerticalLayout, frame.addPushButton, frame.instance,
                                                         meta_field)
    mock_data_type_class_factory.assert_called_once_with(mock_data_type_class_context.return_value)
    mock_data_type_class_factory.return_value.make_data_type_class.assert_called_once_with(
      DataTypeClassName(meta_field['typeClass']))
    assert frame.meta_field == meta_field
    assert frame.data_type_class_factory == mock_data_type_class_factory.return_value
    assert frame.data_type == mock_data_type_class_factory.return_value.make_data_type_class.return_value
    frame.addPushButton.clicked.connect.assert_called_once_with(frame.add_button_click_handler)
    mock_load_ui.assert_called_once()

  @pytest.mark.parametrize(
    'logger_info_call_count, data_type_call_count',
    [
      param(1, 1, id='success_path_single_entry'),
      param(1, 1, id='success_path_multiple_entries'),
      param(1, 0, id='error_case_logger_fails'),
      param(1, 1, id='error_case_data_type_fails'),
    ],
    ids=lambda param: param[2]
  )
  def test_load_ui(self, controlled_vocab_frame, logger_info_call_count, data_type_call_count, request):
    # Arrange
    if request.node.callspec.id == 'error_case_logger_fails':
      controlled_vocab_frame.logger.info.side_effect = Exception('Logger failed')
    elif request.node.callspec.id == 'error_case_data_type_fails':
      controlled_vocab_frame.data_type.populate_entry.side_effect = Exception('Data type failed')

    # Act
    if 'error_case' in request.node.callspec.id:
      with pytest.raises(Exception):
        controlled_vocab_frame.load_ui()
    else:
      controlled_vocab_frame.load_ui()

    # Assert
    controlled_vocab_frame.logger.info.assert_called_once_with('Loading controlled vocabulary frame ui..')
    assert controlled_vocab_frame.logger.info.call_count == logger_info_call_count
    assert controlled_vocab_frame.data_type.populate_entry.call_count == data_type_call_count

  @pytest.mark.parametrize(
    'meta_field',
    [
      ('test_value'),  # success path
      (''),  # edge case: empty string
      (None),  # edge case: None value
    ],
    ids=['success_path', 'empty_string', 'none_value']
  )
  def test_add_button_click_handler(self, controlled_vocab_frame, meta_field):
    # Arrange
    controlled_vocab_frame.meta_field = meta_field

    # Act
    controlled_vocab_frame.add_button_click_handler()

    # Assert
    controlled_vocab_frame.logger.info.assert_called_once_with('Adding new vocabulary entry, value: %s',
                                                               controlled_vocab_frame.meta_field)
    controlled_vocab_frame.data_type.add_new_entry.assert_called_once()

  def test_save_modifications(self, controlled_vocab_frame):
    # Act
    controlled_vocab_frame.save_modifications()

    # Assert
    controlled_vocab_frame.data_type.save_modifications.assert_called_once()
