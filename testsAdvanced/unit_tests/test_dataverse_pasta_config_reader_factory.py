#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: test_dataverse_pasta_config_reader_factory.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from PySide6 import QtCore
from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication
from _pytest.mark import param
from pytestqt.qtbot import QtBot

from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.pasta_config_reader_factory import PastaConfigReaderFactory


@pytest.fixture
def mock_file_system_watcher():
  with patch('pasta_eln.dataverse.pasta_config_reader_factory.QFileSystemWatcher') as mock_watcher:
    yield mock_watcher


@pytest.fixture
def mock_logger():
  with patch('pasta_eln.dataverse.pasta_config_reader_factory.logging.getLogger') as mock_logger:
    yield mock_logger


@pytest.fixture
def mock_exists():
  with patch('pasta_eln.dataverse.pasta_config_reader_factory.exists') as mock_exists:
    yield mock_exists


@pytest.fixture
def mock_open_file():
  with patch('pasta_eln.dataverse.pasta_config_reader_factory.open',
             mock_open(read_data='{"key": "value"}')) as mock_file:
    yield mock_file


@pytest.fixture
def mock_load():
  with patch('pasta_eln.dataverse.pasta_config_reader_factory.load', return_value={'key': 'value'}) as mock_load:
    yield mock_load


@pytest.fixture
def pasta_config_reader(mocker, mock_file_system_watcher, mock_logger, mock_exists, mock_open_file, mock_load):
  mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.Path.home', return_value=Path('/mock/path'))
  PastaConfigReaderFactory._instance = None
  return PastaConfigReaderFactory.get_instance()


@pytest.fixture
def application():
  import sys
  instance = QApplication.instance()
  application = QApplication(sys.argv) if instance is None else instance
  qtbot: QtBot = QtBot(application)
  return application, qtbot


class TestDataversePastaConfigReaderFactory:
  @pytest.mark.parametrize('file_exists, expected_connect_call', [
    (True, True),  # file exists, should connect signal
    (False, False),  # file does not exist, should not connect signal
  ], ids=['file_exists', 'file_does_not_exist'])
  def test_init_file_watcher_connection(self, mocker, mock_file_system_watcher, mock_exists,
                                        file_exists,
                                        expected_connect_call):
    # Arrange
    mock_read_pasta_config = mocker.patch(
      'pasta_eln.dataverse.pasta_config_reader_factory.PastaConfigReaderFactory.read_pasta_config')
    PastaConfigReaderFactory._instance = None
    mock_exists.return_value = file_exists
    mock_fs_watcher_instance = mocker.MagicMock()
    mock_file_system_watcher.return_value = mock_fs_watcher_instance

    # Act
    config_reader = PastaConfigReaderFactory.get_instance()

    # Assert
    if expected_connect_call:
      mock_fs_watcher_instance.fileChanged.connect.assert_called_once_with(config_reader.config_file_changed)
    else:
      mock_fs_watcher_instance.fileChanged.connect.assert_not_called()
    mock_read_pasta_config.assert_called_once()

  @pytest.mark.parametrize('config_file_name', [
    ('/mock/path/.pastaELN_v3.json'),
  ], ids=['default_config_path'])
  def test_init_config_file_name(self, mocker, config_file_name):
    # Arrange
    mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.Path.home', return_value=Path('/mock/path'))
    PastaConfigReaderFactory._instance = None
    mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.PastaConfigReaderFactory.read_pasta_config')

    # Act
    config_reader = PastaConfigReaderFactory.get_instance()

    # Assert
    assert config_reader.config_file_name == config_file_name

  def test_init_logger(self, mocker, mock_logger, mock_exists, mock_open_file, mock_load):
    # Arrange
    PastaConfigReaderFactory._instance = None
    mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.Path.home', return_value=Path('/mock/path'))

    # Act
    config_reader = PastaConfigReaderFactory.get_instance()

    # Assert
    mock_logger.assert_any_call('pasta_eln.dataverse.pasta_config_reader_factory.PastaConfigReaderFactory')
    assert config_reader.config_file_name == '/mock/path/.pastaELN_v3.json'

  @pytest.mark.parametrize(
    'file_exists, file_content, expected_config, raises_exception, exception',
    [
      # Happy path test cases
      param(True, '{"key": "value"}', {'key': 'value'}, False, None, id='valid_json'),
      param(True, '{"another_key": 123}', {'another_key': 123}, False, None, id='valid_json_with_number'),

      # Edge cases
      param(True, '{}', {}, False, None, id='empty_json'),
      param(True, '{"nested": {"key": "value"}}', {'nested': {'key': 'value'}}, False, None, id='nested_json'),

      # Error cases
      param(False, '', None, True, ConfigError, id='file_not_exist'),
      param(True, 'invalid_json', None, True, NameError, id='invalid_json_format'),
    ],
    ids=lambda x: x[-1]
  )
  def test_read_pasta_config(self, pasta_config_reader, file_exists, file_content, expected_config, raises_exception,
                             exception):
    # Arrange
    with patch('pasta_eln.dataverse.pasta_config_reader_factory.exists', return_value=file_exists), \
        patch('builtins.open', mock_open(read_data=file_content)), \
        patch('pasta_eln.dataverse.pasta_config_reader_factory.load',
              side_effect=lambda f: eval(file_content) if file_content else None):

      # Act
      if raises_exception:
        with pytest.raises(exception):
          pasta_config_reader.read_pasta_config()
      else:
        pasta_config_reader.read_pasta_config()

      # Assert
      if not raises_exception:
        assert pasta_config_reader.config == expected_config
        pasta_config_reader.logger.info.assert_any_call('Reading config file: %s', pasta_config_reader.config_file_name)

  def test_singleton_instance(self, mocker, tmp_path):
    # Arrange
    PastaConfigReaderFactory._instance = None
    config_file = tmp_path / '.pastaELN_v3.json'
    config_file.write_text(json.dumps({'key': 'value'}))

    # Act
    with mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.Path.home', return_value=tmp_path):
      instance1 = PastaConfigReaderFactory.get_instance()
      instance2 = PastaConfigReaderFactory.get_instance()

    # Assert
    assert instance1 is instance2

  @pytest.mark.parametrize(
    'initial_config, expected_config',
    [
      # Success path tests
      param({'key1': 'value1'}, {'key1': 'value1'}, id='success_path_single_key'),
      param({'key1': 'value1', 'key2': 'value2'}, {'key1': 'value1', 'key2': 'value2'},
            id='success_path_multiple_keys'),
      param(None, None, id='success_path_none_config'),

      # Edge cases
      param({}, {}, id='edge_case_empty_dict'),
      param({'key': None}, {'key': None}, id='edge_case_none_value'),
      param({'': 'value'}, {'': 'value'}, id='edge_case_empty_key'),

      # Error cases
      param(None, None, id='error_case_no_config_attribute'),
    ],
    ids=lambda x: x[2]
  )
  def test_config_property(self, initial_config, expected_config, pasta_config_reader):
    # Arrange
    pasta_config_reader.config = initial_config

    # Act
    result = pasta_config_reader.config

    # Assert
    assert result == expected_config

  def test_config_deleter(self, pasta_config_reader):
    # Arrange
    pasta_config_reader.config = {'key': 'value'}

    # Act
    del pasta_config_reader.config

    # Assert
    assert pasta_config_reader.config is None

  def test_config_modified(self, mocker, application, tmp_path):
    # Arrange
    PastaConfigReaderFactory._instance = None
    loop = QEventLoop()
    timer = QtCore.QTimer()
    config_file = tmp_path / '.pastaELN_v3.json'
    config_file.write_text(json.dumps({'key': 'value'}))
    mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.Path.home', return_value=tmp_path)

    def close_config_file():
      config_file.write_text(json.dumps(
        {
          'key1': 'value1',
          'key2': 'value2'
        }
      ))
      loop.quit()

    # Act
    instance1 = PastaConfigReaderFactory.get_instance()

    # Assert
    assert instance1.config == {'key': 'value'}

    # Act
    timer.timeout.connect(close_config_file)
    timer.start(1000)
    loop.exec()

    # Act
    # Wait for the config file to be modified
    timer.timeout.connect(loop.quit)
    timer.start(1000)
    loop.exec()

    # Act
    instance2 = PastaConfigReaderFactory.get_instance()

    # Assert
    assert instance1.config == {
      'key1': 'value1',
      'key2': 'value2'
    }
    assert instance2.config == {
      'key1': 'value1',
      'key2': 'value2'
    }

  def test_config_modified_with_multiple_modifications(self, mocker, application, tmp_path):
    # Arrange
    PastaConfigReaderFactory._instance = None
    load_mock = mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.load')
    load_mock.side_effect = lambda x: json.load(x)
    loop = QEventLoop()
    timer = QtCore.QTimer()
    config_file = tmp_path / '.pastaELN_v3.json'
    config_file.write_text(json.dumps({'key': 'value'}))
    mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.Path.home', return_value=tmp_path)
    configs = [
      {'key1': 'value1', 'key2': 'value2'},
      {'key3': 'value3'},
      {'key1': 'value1', 'key3': 'value3'},
      {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'},
      {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4'},
      {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4', 'key5': 'value5'},
      {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4', 'key5': 'value5', 'key6': 'value6'},
      {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4', 'key5': 'value5', 'key6': 'value6',
       'key7': 'value7'},
      {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4', 'key5': 'value5', 'key6': 'value6',
       'key7': 'value7', 'key8': 'value8'}
    ]

    def modify_config_file(config):
      config_file.write_text(json.dumps(config))
      loop.quit()

    # Act
    instance1 = PastaConfigReaderFactory.get_instance()

    # Act
    for config in configs:
      timer.timeout.connect(lambda: modify_config_file(config))
      timer.start(100)
      loop.exec()

    # Wait for all the modifications to be finished
    timer.timeout.connect(loop.quit)
    timer.start(2000)
    loop.exec()

    # Act
    instance2 = PastaConfigReaderFactory.get_instance()

    # Assert
    assert load_mock.call_count == len(configs) + 1
    assert instance1.config in configs
    assert instance2.config in configs

  @pytest.mark.parametrize(
    'config_file_path, file_exists, expected_remove_call, expected_add_call',
    [
      ('valid_path_1', True, True, True),  # happy path
      ('valid_path_2', True, True, True),  # happy path
      ('non_existent_path', False, False, False),  # edge case: file does not exist
      ('', False, False, False),  # edge case: empty path
    ],
    ids=[
      'happy_path_valid_path_1',
      'happy_path_valid_path_2',
      'edge_case_non_existent_path',
      'edge_case_empty_path',
    ]
  )
  def test_config_file_changed(self, mocker, pasta_config_reader, config_file_path, file_exists, expected_remove_call,
                               expected_add_call):
    # Arrange
    mocker.patch('pasta_eln.dataverse.pasta_config_reader_factory.PastaConfigReaderFactory.read_pasta_config')
    pasta_config_reader.fs_watcher.removePath = mocker.MagicMock()
    pasta_config_reader.fs_watcher.addPath = mocker.MagicMock()
    with patch('pasta_eln.dataverse.pasta_config_reader_factory.exists', return_value=file_exists):
      # Act
      pasta_config_reader.config_file_changed(config_file_path)

      # Assert
      pasta_config_reader.read_pasta_config.assert_called_once()
      if expected_remove_call:
        pasta_config_reader.fs_watcher.removePath.assert_any_call(config_file_path)
      else:
        pasta_config_reader.fs_watcher.removePath.assert_not_called()

      if expected_add_call:
        pasta_config_reader.fs_watcher.addPath.assert_any_call(config_file_path)
      else:
        pasta_config_reader.fs_watcher.addPath.assert_not_called()
