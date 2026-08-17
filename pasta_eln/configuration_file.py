"""Read and write configuration files"""
import base64
import copy
import json
import secrets
from pathlib import Path
from typing import Any

import keyring
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

CONFIGURATION_FILE_NAME = '.pastaELN.json'
CONFIGURATION_VERSION = 4
NONCE_SIZE = 12

def _masterKey() -> bytes:
  """Return the master key, creating and disclosing it once when absent.
  Returns:
    bytes: master key
  """
  keyringService = 'com.github.pasta-eln'
  keyringAccount = 'configuration-master-key'
  storedKey = keyring.get_password(keyringService, keyringAccount)
  if storedKey is None:
    masterKey = secrets.token_bytes(32)
    keyring.set_password(keyringService, keyringAccount, base64.b64encode(masterKey).decode('ascii'))
    keyText = base64.b64encode(masterKey).decode('ascii')
    if QApplication.instance() is not None:
      dialog = QMessageBox()
      dialog.setWindowTitle('PASTA-ELN recovery key')
      dialog.setText('Copy and store this recovery key now. It will not be shown again.')
      dialog.setInformativeText(keyText)
      dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
      dialog.exec()
    else:
      print(f'PASTA-ELN recovery key (shown once): {keyText}')
    return masterKey
  masterKey = base64.b64decode(storedKey, validate=True)
  if len(masterKey) != 32:
    raise ValueError('Configuration master key must be 32 bytes')
  return masterKey


def _secretPaths(configuration:dict[str, Any]) -> list[tuple[tuple[str, ...], str]]:
  """Return all configured API-key fields and their stable AAD paths.
  Args:
    configuration (dict[str, Any]): configuration dictionary
  Returns:
    list[tuple[tuple[str, ...], str]]: list of secret paths and their AAD paths
  """
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
  """Encrypt API keys and save the version-4 configuration.
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
    value = target[path[-1]]
    if value:
      cipher = cipher or AESGCM(_masterKey())
      nonce = secrets.token_bytes(NONCE_SIZE)
      ciphertext = cipher.encrypt(nonce, str(value).encode('utf-8'), aadPath.encode('utf-8'))
      target[path[-1]] = base64.b64encode(nonce + ciphertext).decode('ascii')
  stored['version'] = CONFIGURATION_VERSION
  temporaryFile = fileName.with_suffix(fileName.suffix + '.tmp')
  temporaryFile.write_text(json.dumps(stored, indent=2), encoding='utf-8')
  temporaryFile.replace(fileName)


def loadConfiguration(fileName:Path|None=None) -> dict[str, Any]:
  """Load configuration and migrate version 3 plaintext API keys.
  Returns:
    dict[str, Any]: configuration dictionary
  """
  fileName = fileName or Path.home()/CONFIGURATION_FILE_NAME
  configuration = json.loads(fileName.read_text(encoding='utf-8'))
  version = configuration.get('version')
  if version == 3:
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
    value = target[path[-1]]                                       # final path is the value that is encrypted
    if value:
      cipher = cipher or AESGCM(_masterKey())
      raw = base64.b64decode(value, validate=True)
      target[path[-1]] = cipher.decrypt(raw[:NONCE_SIZE], raw[NONCE_SIZE:], aadPath.encode('utf-8')).decode('utf-8')
  return configuration
