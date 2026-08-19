"""Tests for encrypted API keys in the version-4 configuration."""
# pylint: disable=consider-using-with,invalid-name,missing-function-docstring
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.exceptions import InvalidTag

from pasta_eln import configuration_file


def configurationWithSecrets(version:int=4) -> dict:
  """Return a minimal configuration containing every supported secret field."""
  return {
      'version': version,
      'projectGroups': {'research': {'remote': {'key': 'elab-secret'}}},
      'repositories': {
          'zenodo': {'key': 'zenodo-secret'},
          'dataverse': {'key': 'dataverse-secret'},
      },
      'addOnParameter': {'form_auto': {'key': 'addon-secret'}},
  }


class TestConfigSecrets(unittest.TestCase):
  """Envelope encryption stays confined to the configuration serializer."""

  def setUp(self) -> None:
    self.tempDir = tempfile.TemporaryDirectory()
    self.fileName = Path(self.tempDir.name)/'.pastaELN.json'
    self.keyring:dict[str, str] = {}
    self.getPatch = patch('pasta_eln.configuration_file.keyring.get_password', side_effect=lambda *_: self.keyring.get('key'))
    self.setPatch = patch('pasta_eln.configuration_file.keyring.set_password', side_effect=self._setKey)
    self.applicationPatch = patch('pasta_eln.configuration_file.QApplication.instance', return_value=None)
    self.printPatch = patch('builtins.print')
    self.getPatch.start()
    self.setPatch.start()
    self.applicationPatch.start()
    self.showMasterKey = self.printPatch.start()


  def tearDown(self) -> None:
    patch.stopall()
    self.tempDir.cleanup()


  def _setKey(self, service:str, account:str, value:str) -> None:
    self.assertEqual(service, 'com.github.pasta-eln')
    self.assertEqual(account, 'configuration-master-key')
    self.keyring['key'] = value


  def test_encrypts_every_secret_and_reuses_master_key(self) -> None:
    configuration = configurationWithSecrets()
    configuration_file.saveConfiguration(configuration, self.fileName)
    storedText = self.fileName.read_text(encoding='utf-8')
    for secret in ('elab-secret', 'zenodo-secret', 'dataverse-secret', 'addon-secret'):
      self.assertNotIn(secret, storedText)
    self.assertEqual(configuration_file.loadConfiguration(self.fileName), configuration)
    configuration_file.saveConfiguration(configuration, self.fileName)
    self.showMasterKey.assert_called_once()


  def test_each_save_uses_a_fresh_nonce(self) -> None:
    configuration = configurationWithSecrets()
    configuration_file.saveConfiguration(configuration, self.fileName)
    first = json.loads(self.fileName.read_text(encoding='utf-8'))['repositories']['zenodo']['key']
    configuration_file.saveConfiguration(configuration, self.fileName)
    second = json.loads(self.fileName.read_text(encoding='utf-8'))['repositories']['zenodo']['key']
    self.assertNotEqual(first, second)


  def test_ciphertext_cannot_be_moved_between_paths(self) -> None:
    configuration_file.saveConfiguration(configurationWithSecrets(), self.fileName)
    stored = json.loads(self.fileName.read_text(encoding='utf-8'))
    stored['repositories']['dataverse']['key'] = stored['repositories']['zenodo']['key']
    self.fileName.write_text(json.dumps(stored), encoding='utf-8')
    with self.assertRaises(InvalidTag):
      configuration_file.loadConfiguration(self.fileName)


  def test_dotted_add_on_paths_are_distinct(self) -> None:
    configuration = configurationWithSecrets()
    configuration['addOnParameter'] = {'a.b': {'c': 'first'}, 'a': {'b.c': 'second'}}
    configuration_file.saveConfiguration(configuration, self.fileName)
    stored = json.loads(self.fileName.read_text(encoding='utf-8'))
    stored['addOnParameter']['a']['b.c'] = stored['addOnParameter']['a.b']['c']
    self.fileName.write_text(json.dumps(stored), encoding='utf-8')
    with self.assertRaises(InvalidTag):
      configuration_file.loadConfiguration(self.fileName)


  def test_migrates_version_three_plaintext(self) -> None:
    legacy = configurationWithSecrets(3)
    legacy['GUI'] = {
        'showProjectBtn': 'Yes',
        'maxTableColumnWidth': 400,
        'imageWidthProject': 300,
        'widthContent': 600,
        'docTypeOffset': 500,
        'frameSize': 6,
        'maxProjectLeafHeight': 300,
    }
    self.fileName.write_text(json.dumps(legacy), encoding='utf-8')
    migrated = configurationWithSecrets(4)
    migrated['GUI'] = {key: value[1] for section in configuration_file.configurationGUI.values()
                       for key, value in section.items()}
    migrated['GUI']['projectItemHeight'] = 300
    self.assertEqual(configuration_file.loadConfiguration(self.fileName), migrated)
    stored = json.loads(self.fileName.read_text(encoding='utf-8'))
    self.assertEqual(stored['version'], 4)
    self.assertNotEqual(stored['repositories']['zenodo']['key'], 'zenodo-secret')


  def test_migrates_legacy_gui_settings(self) -> None:
    legacy = configurationWithSecrets(3)
    legacy['GUI'] = {
        'showProjectBtn': 'Yes',
        'maxTableColumnWidth': 400,
        'imageWidthProject': 300,
        'widthContent': 600,
        'docTypeOffset': 500,
        'frameSize': 6,
        'maxProjectLeafHeight': 300,
    }
    self.fileName.write_text(json.dumps(legacy), encoding='utf-8')
    migrated = configuration_file.loadConfiguration(self.fileName)
    self.assertNotIn('showProjectBtn', migrated['GUI'])
    self.assertNotIn('maxTableColumnWidth', migrated['GUI'])
    self.assertNotIn('imageWidthProject', migrated['GUI'])
    self.assertEqual(migrated['GUI']['projectItemHeight'], 300)
    self.assertEqual(migrated['GUI']['detailsWidth'], 360)


  def test_invalid_ciphertext_and_keyring_errors_raise(self) -> None:
    configuration_file.saveConfiguration(configurationWithSecrets(), self.fileName)
    stored = json.loads(self.fileName.read_text(encoding='utf-8'))
    stored['repositories']['zenodo']['key'] = 'invalid'
    self.fileName.write_text(json.dumps(stored), encoding='utf-8')
    with self.assertRaises(Exception):
      configuration_file.loadConfiguration(self.fileName)
    with patch('pasta_eln.configuration_file.keyring.get_password', side_effect=RuntimeError('keyring unavailable')):
      with self.assertRaises(RuntimeError):
        configuration_file.saveConfiguration(configurationWithSecrets(), self.fileName)


if __name__ == '__main__':
  unittest.main()
