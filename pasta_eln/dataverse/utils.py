""" Contains utility functions. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

import copy
import re
from asyncio import get_event_loop
from base64 import b64decode, b64encode
from json import dump, load
from logging import Logger
from os.path import exists, join
from pathlib import Path
from typing import Any, Type

from PySide6.QtWidgets import QBoxLayout, QLabel
from cryptography.fernet import Fernet, InvalidToken
from qtawesome import icon

from pasta_eln.dataverse.client import DataverseClient
from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.upload_status_values import UploadStatusValues


def update_status(status: str, statusIconLabel: QLabel, statusLabel: QLabel) -> None:
  """
  Updates the status and status icon of the upload.

  Explanation:
      This function updates the status and status icon of the upload based on the given status.
      It sets the text of the statusLabel and the pixmap of the statusIconLabel based on the status value.

  Args:
      status (str): The status of the upload.
      statusIconLabel (QLabel): The label to display the status icon.
      statusLabel (QLabel): The label to display the status text.
  """
  statusLabel.setText(status)
  match status:
    case UploadStatusValues.Queued.name:
      statusIconLabel.setPixmap(icon('ph.queue-bold').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Uploading.name:
      statusIconLabel.setPixmap(icon('mdi6.progress-upload').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Cancelled.name:
      statusIconLabel.setPixmap(icon('mdi.cancel').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Finished.name:
      statusIconLabel.setPixmap(icon('fa.check-circle-o').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Error.name:
      statusIconLabel.setPixmap(icon('msc.error-small').pixmap(statusIconLabel.size()))
    case UploadStatusValues.Warning.name:
      statusIconLabel.setPixmap(icon('fa.warning').pixmap(statusIconLabel.size()))


def set_authors(logger: Logger, metadata: dict[str, Any]) -> None:
  """
  Sets the authors in the metadata.

  Explanation:
      This function sets the authors in the metadata based on the configuration file.
      It retrieves the authors from the configuration file and updates the metadata accordingly.

  Args:
      logger (Logger): The logger instance for logging errors.
      metadata (dict[str, Any]): The metadata dictionary to update.
  """
  config = read_pasta_config_file(logger)
  if config is None:
    raise log_and_create_error(logger, ConfigError, "Config file not found, Corrupt installation!")
  if 'authors' not in config:
    raise log_and_create_error(logger, ConfigError, "Incorrect config file, authors not found!")
  author_field = next(
    f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if f['typeName'] == 'author')
  authors_list = author_field.get('value')
  if authors_list is None:
    raise log_and_create_error(logger, ConfigError, "Incorrect config file, authors value should be found!")
  template_list = author_field.get('valueTemplate', [{}])
  template = template_list[0] if isinstance(template_list, list) and template_list else {}
  authors_list.clear()
  for author in config['authors']:
    author_copy = copy.deepcopy(template)
    author_copy['authorName']['value'] = ', '.join(filter(None, [author['last'], author['first']]))
    author_copy['authorIdentifierScheme']['value'] = "ORCID"
    author_copy['authorIdentifier']['value'] = author['orcid']
    author_copy['authorAffiliation']['value'] = ', '.join([o['organization'] for o in author['organizations']])
    authors_list.append(author_copy)


def set_template_values(logger: Logger, metadata: dict[str, Any]) -> None:
  """
  Set template values in the metadata.

  This function sets template values in the metadata dictionary based on the type of each field.
  If the metadata is empty, a warning is logged.
  The function iterates through the metadata blocks
  and fields, and for each field, it matches the type class and performs the following actions:
  - For "primitive" or "controlledVocabulary" types:
      - If the field is a multiple type, the value template is set to a copy of the value, and the value is cleared.
      - If the field is a single type, the value template is set to the value, and the value is set to an empty string.
  - For "compound" types:
      - The value template is set to a copy of the value, and the value is cleared.
  - For unknown type classes, a warning is logged.

  Args:
      logger (Logger): The logger object used for logging warnings.
      metadata (dict[str, Any]): The metadata dictionary to update.

  Examples:
      >>> logger = Logger()
      >>> metadata = {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeClass': 'primitive', 'multiple': False, 'value': 'Example'}]}}}}
      >>> set_template_values(logger, metadata)
      >>> metadata
      {'datasetVersion': {'metadataBlocks': {'citation': {'fields': [{'typeClass': 'primitive', 'multiple': False, 'value': '', 'valueTemplate': 'Example'}]}}}}
  """
  if not metadata:
    logger.warning("Empty metadata, make sure the metadata is loaded correctly...")
    return
  for _, metablock in metadata['datasetVersion']['metadataBlocks'].items():
    for field in metablock['fields']:
      match field['typeClass']:
        case "primitive" | "controlledVocabulary":
          # Array of primitive types
          if field['multiple']:
            field['valueTemplate'] = field['value'].copy()
            field['value'].clear()
          # Single primitive type, set to empty string
          else:
            field['valueTemplate'] = field['value']
            field['value'] = ""
        case "compound":
          field['valueTemplate'] = field['value'].copy()
          field['value'].clear()
        case _:
          logger.warning(f"Unsupported type class: {field['typeClass']}")


def check_if_minimal_metadata_exists(logger: Logger,
                                     metadata: dict[str, Any],
                                     check_title: bool = True) -> dict[str, list[str]] | None:
  """
  Checks if the minimal metadata exists and returns the missing information.

  Args:
      logger (Logger): The logger object for logging warnings.
      metadata (dict[str, Any]): The metadata dictionary.
      check_title (bool, optional): Flag to indicate if the title should be checked.
      Defaults to True.

  Returns:
      dict[str, list[str]] | None: The missing information dictionary or None if metadata is empty.

  """
  if not metadata:
    logger.warning("Empty metadata, make sure the metadata is loaded correctly...")
    return None
  missing_information: dict[str, list[str]] = {
    'title': [],
    'author': [],
    'datasetContact': [],
    'dsDescription': [],
    'subject': []
  }
  check_if_field_value_not_null(get_citation_field(metadata, 'title'),
                                missing_information,
                                "title",
                                check_title)
  check_if_field_value_not_null(get_citation_field(metadata, 'subject'),
                                missing_information,
                                "subject")
  check_if_compound_field_value_is_missing(
    get_citation_field(metadata, 'author'),
    'author',
    missing_information,
    [('authorName', 'Author Name'),
     ('authorAffiliation', 'Author Affiliation'),
     ('authorIdentifierScheme', 'Author Identifier Scheme'),
     ('authorIdentifier', 'Author Identifier')])
  check_if_compound_field_value_is_missing(
    get_citation_field(metadata, 'datasetContact'),
    'datasetContact',
    missing_information,
    [('datasetContactName', 'Dataset Contact Name'),
     ('datasetContactAffiliation', 'Dataset Contact Affiliation'),
     ('datasetContactEmail', 'Dataset Contact Email')])
  check_if_compound_field_value_is_missing(
    get_citation_field(metadata, 'dsDescription'),
    'dsDescription',
    missing_information,
    [('dsDescriptionValue', 'Dataset Description Value'),
     ('dsDescriptionDate', 'Dataset Description Date')])
  return missing_information


def get_citation_field(metadata: dict[str, Any], name: str) -> dict[str, Any]:
  """
  Retrieves the citation field from the metadata.

  Args:
      metadata (dict[str, Any]): The metadata dictionary.
      name (str): The name of the field to retrieve.

  Returns:
      dict[str, Any]: The citation field.

  """
  return next(
    f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if f.get('typeName') == name)


def check_if_compound_field_value_is_missing(field: dict[str, Any],
                                             field_key: str,
                                             missing_information: dict[str, list[str]],
                                             sub_fields: list[tuple[str, str]]) -> None:
  """
  Checks if the compound field value is missing and updates the missing_information dictionary if it is.

  Args:
      field (dict[str, Any]): The compound field dictionary.
      field_key (str): The key representing the compound field.
      missing_information (dict[str, list[str]]): The dictionary to track missing information.
      sub_fields (list[tuple[str, str]]): The list of sub-fields to check.
  """
  check_if_field_value_not_null(field, missing_information, field_key)
  if values := field.get('value'):
    for field_value in values:
      for field_name, missing_field_name in sub_fields:
        check_if_field_value_is_missing(field_value, field_key, field_name, missing_field_name,
                                        missing_information)


def check_if_field_value_is_missing(field: dict[str, Any],
                                    field_key: str,
                                    field_name: str,
                                    missing_field_name: str,
                                    missing_information: dict[str, list[str]]) -> None:
  """
  Checks if the field value is missing and updates the missing_information dictionary if it is.

  Args:
      field (dict[str, Any]): The field dictionary.
      field_key (str): The key representing the field.
      field_name (str): The name of the field.
      missing_field_name (str): The name of the missing field.
      missing_information (dict[str, list[str]]): The dictionary to track missing information.

  """
  if not field.get(field_name, {}).get('value'):
    missing_message = f"{missing_field_name} field is missing for one of the {field_key}s!"
    if missing_message not in missing_information[field_key]:
      missing_information[field_key].append(missing_message)


def check_if_field_value_not_null(field: dict[str, Any],
                                  missing_information: dict[str, list[str]],
                                  missing_field_name: str,
                                  check: bool = True) -> None:
  """
  Checks if the field value is not null and updates the missing_information dictionary if it is.

  Args:
      field (dict[str, Any]): The field dictionary.
      missing_information (dict[str, list[str]]): The dictionary to track missing information.
      missing_field_name (str): The name of the missing field.
      check (bool, optional): Flag to indicate if the check should be performed. Defaults to True.

  """
  if check and not field.get('value'):
    missing_message = f"{missing_field_name.capitalize()} field is missing!"
    if missing_message not in missing_information[missing_field_name]:
      missing_information[missing_field_name].append(missing_message)


def get_encrypt_key(logger: Logger) -> tuple[bool, bytes]:
  """
  Gets the dataverse encryption key.

  Explanation:
  This function retrieves the dataverse encryption key from the configuration file. If the key does not exist, a new key is generated and stored in the configuration file.

  Args:
      logger (Logger): The logger instance for logging messages.

  Raises:
    EnvironmentError: If the config file is not found or corrupt.

  Returns:
      tuple[bool, bytes]: A tuple containing a boolean indicating whether the key exists and the encryption key itself.
  """
  logger.info("Getting dataverse encrypt key..")
  config = read_pasta_config_file(logger)
  key_exists = False
  if 'dataverseEncryptKey' not in config:
    logger.warning("Dataverse encrypt key does not exist, hence generating a new key..")
    config['dataverseEncryptKey'] = b64encode(Fernet.generate_key()).decode('ascii')
    write_pasta_config_file(logger, config)
  else:
    key_exists = True
  key = b64decode(config['dataverseEncryptKey'])
  return key_exists, key


def encrypt_data(logger: Logger, encrypt_key: bytes | None, data: str | None) -> str | None:
  """
  Encrypts the provided data using the given encryption key.

  Explanation:
      This function encrypts the provided data using the given encryption key.
      It returns the encrypted data as a string.

  Args:
      logger (Logger): The logger instance for logging information.
      encrypt_key (bytes | None): The encryption key used for encryption.
      data (str | None): The data to be encrypted.

  Returns:
      str | None: The encrypted data as a string, or None if either the encrypt_key or data is None.
  """
  if encrypt_key is None or data is None:
    logger.warning("encrypt_key/data cannot be None")
    return None
  try:
    fernet = Fernet(encrypt_key)
    data = fernet.encrypt(data.encode('ascii')).decode('ascii')
  except InvalidToken as e:
    logger.error("Invalid token: %s", e)
    return None
  except ValueError as e:
    logger.error("Value error: %s", e)
    return None
  except AttributeError as e:
    logger.error("AttributeError: %s", e)
    return None
  return data


def decrypt_data(logger: Logger, encrypt_key: bytes | None, data: str | None) -> str | None:
  """
  Decrypts the provided data using the given encryption key.

  Explanation:
      This function decrypts the provided data using the given encryption key.
      It returns the decrypted data as a string.

  Args:
      logger (Logger): The logger instance for logging information.
      encrypt_key (bytes | None): The encryption key used for decryption.
      data (str | None): The data to be decrypted.

  Returns:
      str | None: The decrypted data as a string, or None if either the encrypt_key or data is None.
  """
  if encrypt_key is None or data is None:
    logger.warning("encrypt_key/data cannot be None")
    return None
  try:
    fernet = Fernet(encrypt_key)
    data = fernet.decrypt(data.encode('ascii')).decode('ascii')
  except InvalidToken as e:
    logger.error("Invalid token: %s", e)
    return None
  except ValueError as e:
    logger.error("Value error: %s", e)
    return None
  except AttributeError as e:
    logger.error("AttributeError: %s", e)
    return None
  return data


def read_pasta_config_file(logger: Logger) -> dict[str, Any]:
  """
  Reads the PASTA configuration file.

  Explanation:
      This function reads the PASTA configuration file and returns the configuration as a dictionary.
      If the configuration file is not found, it raises a DatabaseError.

  Args:
      logger (Logger): The logger instance for logging errors.

  Returns:
      dict[str, Any] | None: The configuration dictionary, or None if the configuration file is not found.
  """
  config_file_name = join(Path.home(), '.pastaELN.json')
  if not exists(config_file_name):
    raise log_and_create_error(logger, ConfigError, "Config file not found, Corrupt installation!")
  logger.info("Reading config file: %s", config_file_name)
  with open(config_file_name, 'r', encoding='utf-8') as confFile:
    config = load(confFile)
  return config


def write_pasta_config_file(logger: Logger, config_data: dict[str, Any]) -> None:
  """
  Writes the PASTA config file with the provided configuration data.

  Explanation:
      This function writes the PASTA config file with the provided configuration data.
      It raises a DatabaseError if the config file does not exist.

  Args:
      logger (Logger): The logger instance for logging information.
      config_data (dict[str, Any]): The configuration data to be written to the config file.
  """
  config_file_name = join(Path.home(), '.pastaELN.json')
  if not exists(config_file_name):
    raise log_and_create_error(logger, ConfigError, "Config file not found, Corrupt installation!")
  logger.info("Writing config file: %s", config_file_name)
  with open(config_file_name, 'w', encoding='utf-8') as confFile:
    dump(config_data, confFile, ensure_ascii=False, indent=4)


def log_and_create_error(logger: Logger, exception_type: Type[Exception], error_message: str) -> Exception:
  """
  Logs an error message and creates an exception.

  Explanation:
      This function logs the provided error message and creates an exception of the specified type.

  Args:
      logger (Logger): The logger instance for logging errors.
      exception_type (Type[Exception]): The type of exception to create.
      error_message (str): The error message to log and include in the exception.

  Returns:
      Exception: The created exception.
  """
  logger.error(error_message)
  return exception_type(error_message)


def check_login_credentials(logger: Logger, api_token: str, server_url: str) -> tuple[bool, str]:
  """
  Checks if the login credentials (API token and server URL) are valid.

  Explanation:
      This function checks if the provided API token and server URL are valid by
      attempting to reach the dataverse server and verifying the token.

  Args:
      logger (Logger): The logger instance for logging information.
      api_token (str): The API token for authentication.
      server_url (str): The URL of the dataverse server.

  Returns:
      tuple[bool, str]: A tuple containing a boolean indicating if the login credentials are valid
      and a message describing the result.
  """
  logger.info("Checking if login info is valid, server_url: %s", server_url)
  dataverse_client = DataverseClient(server_url, api_token)
  event_loop = get_event_loop()
  success, message = event_loop.run_until_complete(dataverse_client.check_if_dataverse_server_reachable())
  if success:
    token_valid = event_loop.run_until_complete(dataverse_client.check_if_api_token_is_valid())
    if token_valid:
      result = True, "Data server is reachable and token is valid"
    else:
      result = False, "Data server is reachable but token is invalid"
      logger.warning("Data server is reachable but API token is invalid!")
  elif 'Unauthorized' in message:
    result = False, "Data server is reachable but API token is invalid"
    logger.warning("Data server is reachable but API token is invalid: %s", message)
  else:
    result = False, "Data server is not reachable"
    logger.warning("Data server is not reachable: %s", message)
  return result


def adjust_type_name(camel_case_string: str) -> str:
  """
  Adjusts the type name from camel case to title case.

  Splits the camel case string into individual words and capitalizes the first letter of each word.
  If a word starts with an uppercase letter, it is left as is.

  Args:
      camel_case_string (str): The input string in camel case.

  Returns:
      str: The adjusted type name in title case.
  """
  split = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)',
                     camel_case_string)
  return ' '.join([i.capitalize() if i[0].islower() else i for i in split])


def clear_value(items: dict[str, Any] | None = None) -> None:
  """
  Clears the 'value' attribute of each item in the given dictionary.

  Args:
      items(dict[str, Any] | None): The dictionary containing items to be cleared.

  Explanation:
      This function iterates over the values of the given dictionary and sets the 'value'
      attribute to None for each item.
      If the 'items' argument is None, the function returns immediately.

  """
  if items is None:
    return
  for item in items.values():
    if item and "value" in item:
      item["value"] = None


def is_date_time_type(type_name: str) -> bool:
  """
  Checks if the given type_name contains 'date' or 'time' as a substring.

  Args:
      type_name (str): The type name to check.

  Returns:
      bool: True if the type_name contains 'date' or 'time', False otherwise.

  Explanation:
      This function checks if the given type_name contains 'date' or 'time' as a substring.
      It performs a case-insensitive search to determine the presence of 'date' or 'time' in the type_name.

  """
  return any(
    map(type_name.lower().__contains__, ["date", "time"]))


def delete_layout_and_contents(layout: QBoxLayout) -> None:
  """
  Deletes the layout and its contents.

  Args:
      layout (QBoxLayout): The layout to delete.

  Explanation:
      This function deletes the given layout and its contents.
      It iterates over the widgets in the layout and removes them from their parent.
      Finally, it sets the layout's parent to None.

  """
  if layout is None:
    return
  for widget_pos in reversed(range(layout.count())):
    if item := layout.itemAt(widget_pos):
      item.widget().setParent(None)  # type: ignore[call-overload]
  layout.setParent(None)  # type: ignore[arg-type]
