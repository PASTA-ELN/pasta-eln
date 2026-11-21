"""Read and write configuration files"""
import base64
import copy
import json
import logging
import secrets
import uuid
from pathlib import Path
from typing import Any
import keyring
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from keyring.errors import KeyringError
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox
from . import minisign
from .constants import configurationGUI, defaultConfiguration, defaultScanExcludePatterns, defaultUIState


def getConfiguration(defaultProjectGroup: str = '') -> tuple[dict[str, Any], str]:
  """Load configuration, apply defaults, and select the active project group
    Args:
      defaultProjectGroup (str): project group selected when none is configured
    Returns:
      tuple[dict[str, Any], str]: The configuration dictionary and selected project group
  """
  configuration = copy.deepcopy(defaultConfiguration)
  try:
    configuration |= loadConfiguration()
  except FileNotFoundError:
    pass
  for _, items in configurationGUI.items():
    for key, value in items.items():
      if key != 'scanExcludePatterns' and key not in configuration['GUI']:
        configuration['GUI'][key] = value[1]
  uiState = configuration.setdefault('uiState', copy.deepcopy(defaultUIState))
  for key, value in defaultUIState.items():
    uiState.setdefault(key, value)
  configuration.setdefault('scanExcludePatterns', list(defaultScanExcludePatterns))
  if configuration['version'] != CONFIGURATION_VERSION:
    logging.info('Configuration file does not exist or version is != %s', CONFIGURATION_VERSION)
    return {}, ''
  if not configuration['signingKeyPair']:                           # first start: key that signs .eln exports
    keyPair = minisign.KeyPair.generate()
    configuration['signingKeyPair'] = {'id':str(uuid.uuid4()), 'secret':bytes(keyPair.secret_key).decode(),
                                       'public':bytes(keyPair.public_key).decode()}
    saveConfiguration(configuration)
  defaultProjectGroup = defaultProjectGroup or configuration['defaultProjectGroup']
  if defaultProjectGroup not in configuration['projectGroups']:
    possibleGroups = list(configuration['projectGroups'].keys())
    raise ValueError(f'BadProjectGroup: {defaultProjectGroup}. Possible: {possibleGroups}')
  return configuration, defaultProjectGroup


def getRORIDLabel(idString: str) -> str:
  """Get an organization label from a ROR ID
    Args:
      idString (str): ROR or ORCID identifier to resolve
    Returns:
      str: Organization label resolved from the ROR identifier
  """
  import requests
  reply = requests.get(f'https://api.ror.org/organizations/{idString}', timeout=10)
  labels = [item for item in reply.json()['names'] if 'ror_display' in item['types']]
  labels = labels or [item for item in reply.json()['names'] if 'acronym' not in item['types']]
  labels = labels or reply.json()['names']
  return labels[0]['value'] if labels else ''


def getORCIDName(idString: str) -> tuple[str, str]:
  """Get first and family names from an ORCID
    Args:
      idString (str): ROR or ORCID identifier to resolve
    Returns:
      tuple[str, str]: Given and family names resolved from the ORCID identifier
  """
  import requests
  reply = requests.get(f'https://pub.orcid.org/v3.0/{idString}', timeout=10)
  text = reply.content.decode()
  first = text.split('<personal-details:given-names>')[1].split('</personal-details:given-names>')[0]
  last = text.split('<personal-details:family-name>')[1].split('</personal-details:family-name>')[0]
  return first, last

CONFIGURATION_FILE_NAME = '.pastaELN.json'
CONFIGURATION_VERSION = 4
NONCE_SIZE = 12

def masterKey() -> bytes:
  """Return the master key, creating and disclosing it once when absent.
  Returns:
    bytes: master key
  """
  keyringService = 'com.github.pasta-eln'
  keyringAccount = 'configuration-master-key'
  try:
    storedKey = keyring.get_password(keyringService, keyringAccount)
  except KeyringError as exc:
    raise RuntimeError(f'System keyring unavailable, cannot read the configuration master key: {exc}') from exc
  if storedKey is None:
    key = secrets.token_bytes(32)
    keyText = base64.b64encode(key).decode('ascii')
    try:
      keyring.set_password(keyringService, keyringAccount, keyText)
    except KeyringError as exc:
      raise RuntimeError(f'System keyring unavailable, cannot store the configuration master key: {exc}') from exc
    if QApplication.instance() is not None:
      dialog = QMessageBox()
      dialog.setWindowTitle('PASTA-ELN recovery key')
      dialog.setText(f'Copy and store this recovery key now.\n\n{keyText}')
      dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
      copyButton = dialog.addButton('Copy key and close', QMessageBox.ButtonRole.AcceptRole)
      dialog.addButton(QMessageBox.StandardButton.Close)
      dialog.exec()
      if dialog.clickedButton() is copyButton:
        QApplication.clipboard().setText(keyText)
    else:
      print(f'PASTA-ELN recovery key: {keyText}')
    return key
  key = base64.b64decode(storedKey, validate=True)
  if len(key) != 32:
    raise ValueError('Configuration master key must be 32 bytes')
  return key


def _secretPaths(configuration:dict[str, Any]) -> list[tuple[tuple[str, ...], str]]:
  """Return all configured API-key fields and their stable AAD paths
  Args:
    configuration (dict[str, Any]): configuration dictionary
  Returns:
    list[tuple[tuple[str, ...], str]]: list of secret paths and their AAD paths
  """
  # This Unicode representation is cryptographic AAD in configuration version 4; changing it would break decryption
  paths:list[tuple[tuple[str, ...], str]] = []
  for groupName, group in configuration.get('projectGroups', {}).items():
    remote = group.get('remote', {})
    if 'key' in remote:
      path1 = ('projectGroups', groupName, 'remote', 'key')
      paths.append((path1, json.dumps(path1, ensure_ascii=False, separators=(',', ':'))))
  for repository in ('zenodo', 'dataverse'):
    data = configuration.get('repositories', {}).get(repository, {})
    if 'key' in data:
      path2 = ('repositories', repository, 'key')
      paths.append((path2, json.dumps(path2, ensure_ascii=False, separators=(',', ':'))))
  for addOnName, parameters in configuration.get('addOnParameter', {}).items():
    for parameterName in parameters:
      path3 = ('addOnParameter', addOnName, parameterName)
      paths.append((path3, json.dumps(path3, ensure_ascii=False, separators=(',', ':'))))
  return paths


def saveConfiguration(configuration:dict[str, Any], fileName:Path|None=None) -> None:
  """Encrypt API keys and save the version-4 configuration
  Args:
    configuration (dict[str, Any]): configuration dictionary
    fileName (Path | None): configuration file, or the default home-directory file
  """
  fileName = fileName or Path.home()/CONFIGURATION_FILE_NAME
  stored = copy.deepcopy(configuration)
  cipher:AESGCM|None = None
  for path, aadPath in _secretPaths(stored):
    target:Any = stored
    for part in path[:-1]:
      target = target[part]
    if value:= target[path[-1]]:
      cipher = cipher or AESGCM(masterKey())
      nonce = secrets.token_bytes(NONCE_SIZE)
      ciphertext = cipher.encrypt(nonce, str(value).encode('utf-8'), aadPath.encode('utf-8'))
      target[path[-1]] = base64.b64encode(nonce + ciphertext).decode('ascii')
  stored['version'] = CONFIGURATION_VERSION
  temporaryFile = fileName.with_suffix(f'{fileName.suffix}.tmp')
  temporaryFile.write_text(json.dumps(stored, indent=2), encoding='utf-8')
  temporaryFile.replace(fileName)


def loadConfiguration(fileName:Path|None=None) -> dict[str, Any]:
  """Load configuration and migrate version 3 plaintext API keys
  Args:
    fileName (Path | None): configuration file to load
  Returns:
    dict[str, Any]: configuration dictionary
  """
  fileName = fileName or Path.home()/CONFIGURATION_FILE_NAME
  configuration = json.loads(fileName.read_text(encoding='utf-8'))
  version = configuration.get('version')
  if version == 3:                                                                # TODO REMOVE IN August 2027
    # Warn before migration
    message = (f'The configuration file {fileName} uses version 3 and will be '
              'updated to version 4. Back up this JSON file before continuing.')
    if QApplication.instance() is not None:
      QMessageBox.warning(None, 'Configuration migration', message)
    else:
      print(f'WARNING: {message}')
      input('Press Enter to continue with the migration.')
    # Clean old GUI content
    gui = configuration.setdefault('GUI', {})
    for key in ['showProjectBtn', 'maxTableColumnWidth', 'imageWidthProject', 'widthContent',
                'docTypeOffset', 'frameSize']:
      gui.pop(key, None)
    if 'maxProjectLeafHeight' in gui and 'projectItemHeight' not in gui:
      gui['projectItemHeight'] = gui.pop('maxProjectLeafHeight')
    else:
      gui.pop('maxProjectLeafHeight', None)
    for section in configurationGUI.values():
      for key, value in section.items():
        if key == 'scanExcludePatterns':
          continue
        gui.setdefault(key, value[1])
    configuration.setdefault('uiState', dict(defaultUIState))
    configuration.setdefault('scanExcludePatterns', list(defaultScanExcludePatterns))
    # Update version
    configuration['version'] = CONFIGURATION_VERSION
    saveConfiguration(configuration, fileName)
    return configuration
  if version != CONFIGURATION_VERSION:
    raise ValueError(f'Unsupported configuration version: {version}')
  cipher:AESGCM|None = None
  for path, aadPath in _secretPaths(configuration):
    target:Any = configuration                                 # recreate the intermediate configuration jsons
    for part in path[:-1]:
      target = target[part]
    if value:= target[path[-1]]:                                   # final path is the value that is encrypted
      cipher = cipher or AESGCM(masterKey())
      raw = base64.b64decode(value, validate=True)
      target[path[-1]] = cipher.decrypt(raw[:NONCE_SIZE], raw[NONCE_SIZE:], aadPath.encode('utf-8')).decode('utf-8')
  return configuration
