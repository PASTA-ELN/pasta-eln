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
from json import dump
from logging import Logger
from os.path import exists, join
from pathlib import Path
from typing import Any, Callable
from cryptography.fernet import Fernet, InvalidToken
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPixmap
from qtawesome import icon
from sqlalchemy import Executable, and_, select
from sqlalchemy.orm import aliased
from pasta_eln.database.models.data_hierarchy_model import DataHierarchyModel
from pasta_eln.database.models.main_orm_model import MainOrmModel
from pasta_eln.database.models.properties_orm_model import PropertiesOrmModel
from pasta_eln.dataverse.client import DataverseClient
from pasta_eln.dataverse.config_error import ConfigError
from pasta_eln.dataverse.pasta_config_reader_factory import PastaConfigReaderFactory
from pasta_eln.dataverse.upload_status_values import UploadStatusValues


def update_status(status: str,
                  status_label_set_text_callback: Callable[[str], None],
                  status_icon_set_pixmap_callback: Callable[[QPixmap | QImage | str], None]) -> None:
  """
  Updates the status with the corresponding label and icon.

  Args:
      status (str): The status value.
      status_label_set_text_callback (Callable[[str], None]): The callback function to set the status label text.
      status_icon_set_pixmap_callback (Callable[[QPixmap | QImage | str], None]): The callback function to set the status icon pixmap.

  Explanation:
      This function updates the status with the corresponding label and icon based on the given status value.
      It uses the provided callback functions to set the status label text and status icon pixmap.
  """
  match status:
    case UploadStatusValues.Queued.name:
      icon_name = 'fa.circle-o-notch'
    case UploadStatusValues.Uploading.name:
      icon_name = 'fa.cloud-upload'
    case UploadStatusValues.Cancelled.name:
      icon_name = 'fa.minus-circle'
    case UploadStatusValues.Finished.name:
      icon_name = 'fa.check-circle-o'
    case UploadStatusValues.Error.name:
      icon_name = 'fa.times-circle-o'
    case UploadStatusValues.Warning.name:
      icon_name = 'fa.warning'
    case _:
      icon_name = 'fa.times-circle-o'
  status_label_set_text_callback(status)
  status_icon_set_pixmap_callback(icon(icon_name).pixmap(QSize(30, 30)))


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
  config = PastaConfigReaderFactory.get_instance().config
  if config is None:
    raise log_and_create_error(logger, ConfigError, 'Config file not found, Corrupt installation!')
  if 'authors' not in config:
    raise log_and_create_error(logger, ConfigError, 'Incorrect config file, authors not found!')
  author_field = next(
    f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if f['typeName'] == 'author')
  authors_list = author_field.get('value')
  if authors_list is None:
    raise log_and_create_error(logger, ConfigError, 'Incorrect config file, authors value should be found!')
  template_list = author_field.get('valueTemplate', [{}])
  template = template_list[0] if isinstance(template_list, list) and template_list else {}
  authors_list.clear()
  for author in config['authors']:
    author_copy = copy.deepcopy(template)
    author_copy['authorName']['value'] = ', '.join(filter(None, [author['last'], author['first']]))
    author_copy['authorIdentifierScheme']['value'] = 'ORCID'
    author_copy['authorIdentifier']['value'] = author['orcid']
    author_copy['authorAffiliation']['value'] = ', '.join([o['organization'] for o in author['organizations']])
    authors_list.append(author_copy)


def get_flattened_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
  """
  Returns a flattened version of the metadata.

  Args:
      metadata (dict[str, Any]): The metadata to be flattened.

  Returns:
      dict[str, Any]: The flattened metadata.

  Explanation:
      This function takes a nested metadata dictionary and returns a flattened version of the metadata.
      It extracts the values from the nested structure and creates a new dictionary with a flattened structure.
      The resulting dictionary contains the field names as keys and their corresponding values.

  Exceptions:
      KeyError: If a field name is not found in the metadata dictionary.
  """
  adjusted_metadata = {}
  if metadata['datasetVersion']['license']:
    adjusted_metadata['license'] = metadata['datasetVersion']['license']
  for _, metablock in metadata['datasetVersion']['metadataBlocks'].items():
    for field in metablock['fields']:
      if field['value']:
        adjusted_metadata[field['typeName']] = field['value']
  return adjusted_metadata


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
    logger.warning('Empty metadata, make sure the metadata is loaded correctly...')
    return
  for _, metablock in metadata['datasetVersion']['metadataBlocks'].items():
    for field in metablock['fields']:
      match field['typeClass']:
        case 'primitive':
          set_field_template_value(field)
        case 'controlledVocabulary':
          set_field_template_value(field)
          if field['multiple']:
            field['valueTemplate'].insert(0, 'No Value')
        case 'compound':
          field['valueTemplate'] = field['value'].copy()
          field['value'].clear()
        case _:
          logger.warning(f"Unsupported type class: {field['typeClass']}")


def set_field_template_value(field: dict[str, Any]) -> None:
  """
  Set template values in the field.

  This function sets template values in the field based on the type of the field.
  If the field is a multiple type, the value template is set to a copy of the value, and the value is cleared.
  If the field is a single type, the value template is set to the value, and the value is set to an empty string.

  Args:
      field (dict[str, Any]): The field dictionary to update.

  Examples:
      >>> field = {'typeClass': 'primitive', 'multiple': False, 'value': 'Example'}
      >>> set_field_template_value(field)
      >>> field
      {'typeClass': 'primitive', 'multiple': False, 'value': '', 'valueTemplate': 'Example'}
  """
  if field.get('multiple'):
    if 'value' in field and field['value']:
      field['valueTemplate'] = field['value'].copy()
      field['value'].clear()
    else:
      field['value'] = []
      field['valueTemplate'] = []
  else:
    field['valueTemplate'] = field.get('value')
    if 'value' in field:
      field['value'] = ''


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
      missing_information = {
                              'title': [],
                              'author': [],
                              'datasetContact': [],
                              'dsDescription': [],
                              'subject': []
                            }

  """
  if not metadata:
    logger.warning('Empty metadata, make sure the metadata is loaded correctly...')
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
                                'title',
                                check_title)
  check_if_field_value_not_null(get_citation_field(metadata, 'subject'),
                                missing_information,
                                'subject')
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
    missing_message = f"Add at-least a single entry for {missing_field_name.capitalize()}!"
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
  logger.info('Getting dataverse encrypt key..')
  config = PastaConfigReaderFactory.get_instance().config
  key_exists = False
  if 'dataverseEncryptKey' not in config:
    logger.warning('Dataverse encrypt key does not exist, hence generating a new key..')
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
    logger.warning('encrypt_key/data cannot be None')
    return None
  try:
    fernet = Fernet(encrypt_key)
    data = fernet.encrypt(data.encode('ascii')).decode('ascii')
  except InvalidToken as e:
    logger.error('Invalid token: %s', e)
    return None
  except ValueError as e:
    logger.error('Value error: %s', e)
    return None
  except AttributeError as e:
    logger.error('AttributeError: %s', e)
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
    logger.warning('encrypt_key/data cannot be None')
    return None
  try:
    fernet = Fernet(encrypt_key)
    data = fernet.decrypt(data.encode('ascii')).decode('ascii')
  except InvalidToken as e:
    logger.error('Invalid token: %s', e)
    return None
  except ValueError as e:
    logger.error('Value error: %s', e)
    return None
  except AttributeError as e:
    logger.error('AttributeError: %s', e)
    return None
  return data


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
  config_file_name = join(Path.home(), '.pastaELN_v3.json')
  if not exists(config_file_name):
    raise log_and_create_error(logger, ConfigError, 'Config file not found, Corrupt installation!')
  logger.info('Writing config file: %s', config_file_name)
  with open(config_file_name, 'w', encoding='utf-8') as conf_file:
    dump(config_data, conf_file, ensure_ascii=False, indent=4)


def log_and_create_error(logger: Logger, exception_type: type[Exception], error_message: str) -> Exception:
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
  logger.info('Checking if login info is valid, server_url: %s', server_url)
  dataverse_client = DataverseClient(server_url, api_token)
  event_loop = get_event_loop()
  success, message = event_loop.run_until_complete(dataverse_client.check_if_dataverse_server_reachable())
  if success:
    token_valid = event_loop.run_until_complete(dataverse_client.check_if_api_token_is_valid())
    if token_valid:
      result = True, 'Data server is reachable and token is valid'
    else:
      result = False, 'Data server is reachable but token is invalid'
      logger.warning('Data server is reachable but API token is invalid!')
  elif 'Unauthorized' in message:
    result = False, 'Data server is reachable but API token is invalid'
    logger.warning('Data server is reachable but API token is invalid: %s', message)
  else:
    result = False, 'Data server is not reachable'
    logger.warning('Data server is not reachable: %s', message)
  return result


def check_if_dataverse_exists(logger: Logger, api_token: str, server_url: str, dataverse_id: str) -> bool:
  """
  Checks if a Dataverse exists based on the provided server URL, API token, and Dataverse ID.

  Args:
      logger (Logger): The logger object for logging information.
      api_token (str): The API token for authentication.
      server_url (str): The URL of the Dataverse server.
      dataverse_id (str): The ID of the Dataverse to check existence for.

  Returns:
      bool: True if the Dataverse exists, False otherwise.
  """
  logger.info('Checking if login info is valid, server_url: %s', server_url)
  dataverse_client = DataverseClient(server_url, api_token)
  event_loop = get_event_loop()
  info = event_loop.run_until_complete(dataverse_client.get_dataverse_info(dataverse_id))
  result = False
  if isinstance(info, dict):
    result = (info.get('id', None) is not None
              and info.get('alias', None) == dataverse_id)
  else:
    logger.warning('Data verse with id %s does not exist, Server message: %s', dataverse_id, info)
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
    if item and 'value' in item:
      item['value'] = None


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
    map(type_name.lower().__contains__, ['date', 'time']))


def get_formatted_message(missing_metadata: dict[str, list[str]]) -> str:
  """
  Returns a formatted message with missing metadata information.

  Args:
      missing_metadata (dict[str, list[str]]): A dictionary containing missing metadata information.

  Returns:
      str: A formatted message with the missing metadata information.

  Explanation:
      This function takes a dictionary of missing metadata information and returns a formatted message
      with the missing information. The message is formatted as an HTML string and includes a list of missing
      metadata items grouped by their corresponding metadata names.
  """
  if not any(missing_metadata.values()):
    return ''
  name_mapping = {
    'author': 'Author',
    'datasetContact': 'Dataset Contact',
    'dsDescription': 'Dataset Description',
    'subject': 'Subject'
  }
  message = (
    "<html><p><i>Goto 'Edit Metadata' dialog, select 'Minimal' metadata list, enter the below given missing information and retry the upload!</i></p>"
  )
  for metadata_name, missing_list in missing_metadata.items():
    if missing_list:
      message += f"<br></br><b><i>{name_mapping[metadata_name]}:</i></b><ul>"
      for missing in missing_list:
        message += f"<i style=\"color:Crimson\"><li>{missing}</li></i>"
      message += '</ul>'
  message += '</html>'
  return message


def get_formatted_metadata_message(metadata: dict[str, Any]) -> str:
  """
  Formats metadata into an HTML message for display.

  Args:
      metadata (dict): A dictionary containing metadata information.

  Returns:
      str: An HTML-formatted message representing the metadata.

  Examples:
      >>> metadata = {
      ...     'datasetVersion': {
      ...         'license': {'name': 'CC0', 'uri': 'https://creativecommons.org/publicdomain/zero/1.0/'},
      ...         'metadataBlocks': {
      ...             'citation': {
      ...                 'displayName': 'Citation Metadata',
      ...                 'fields': [
      ...                     {'typeName': 'title', 'value': 'Test Title', 'multiple': False, 'typeClass': 'primitive'}
      ...                 ]
      ...             }
      ...         }
      ...     }
      ... }
      >>> get_formatted_metadata_message(metadata)
      '<html>...</html>'
  """

  message = '<html>'
  if metadata['datasetVersion']['license']:
    message += "<b style=\"color:Black\">License Metadata:</b><ul>"
    message += f"<li style=\"color:Gray\">Name: <i>{metadata['datasetVersion']['license']['name']}</i></li>"
    message += f"<li style=\"color:Gray\">URI: <i>{metadata['datasetVersion']['license']['uri']}</i></li>"
    message += '</ul>'
  for _, metablock in metadata['datasetVersion']['metadataBlocks'].items():
    message += f"<b style=\"color:Black\">{metablock['displayName']}:</b><ul>"
    has_value = False
    for field in metablock['fields']:
      if field['value']:
        has_value = has_value or len(field['value']) > 0
        message += f"<b style=\"color:#737373\"><li>{adjust_type_name(field['typeName'])}:</li></b><ul>"
        if field['multiple'] and field['typeClass'] == 'compound':
          for index, field_value in enumerate(field['value']):
            message += f"<li style=\"color:Gray\">Item {index + 1}:</li><ul>"
            for _, value in field_value.items():
              message += f"<li style=\"color:Gray\">{adjust_type_name(value['typeName'])}: <i>{value['value']}</li></i>"
            message += '</ul>'
          message += '</ul>'
        elif not field['multiple'] and field['typeClass'] == 'compound':
          for _, value in field['value'].items():
            message += f"<li style=\"color:Gray\">{adjust_type_name(value['typeName'])}: <i>{value['value']}</li></i>"
          message += '</ul>'
        elif field['multiple'] and field['typeClass'] == 'controlledVocabulary':
          for field_value in field['value']:
            message += f"<i style=\"color:Gray\"><li>{field_value}</li></i>"
          message += '</ul>'
        elif field['multiple'] and field['typeClass'] == 'primitive':
          for field_value in field['value']:
            message += f"<i style=\"color:Gray\"><li>{field_value}</li></i>"
          message += '</ul>'
        else:
          message += f"<i style=\"color:Gray\"><li>{field['value']}</li></i></ul>"
    if not has_value:
      message += "<li style=\"color:#737373\">No Value</li></ul>"
    message += '</ul>'
  message += '</html>'
  return message


def get_formatted_dataverse_url(dataverse_url: str) -> str:
  """
  Formats a Dataverse URL.

  Explanation:
      This function takes a Dataverse URL as input and extracts the persistent ID from it.
      It then formats the URL with the persistent ID in an HTML structure for display.

  Args:
      dataverse_url (str): The Dataverse URL to be formatted.

  Returns:
      str: The formatted Dataverse URL in HTML structure.
  """

  formatted_dataverse_url = ''
  if dataverse_url:
    if 'persistentId=' not in dataverse_url:
      return formatted_dataverse_url
    persistent_id = dataverse_url.split('persistentId=', 1)[1]
    formatted_dataverse_url = (
      f"<html><head/><body><p>Dataverse URL: "
      f"<a href='{dataverse_url}'>"
      f"<span style='font-style:italic; text-decoration: underline; color:#77767b;'>{persistent_id}</span>"
      f"</a></p></body></html>")
  return formatted_dataverse_url


def get_data_hierarchy_types(data_hierarchy: list[DataHierarchyModel] | None) -> list[str | Any]:
  """Retrieves a list of unique data hierarchy types from the provided models.

  This function processes a list of DataHierarchyModel instances and extracts
  their document types, excluding specific types ("x0" and "x1"). It returns
  a list of unique, capitalized document types along with an "Unidentified"
  entry if no valid types are found.

  Args:
      data_hierarchy (list[DataHierarchyModel] | None): A list of data hierarchy models
      to extract types from, or None to return an empty list.

  Returns:
      list[str | Any]: A list of unique document types from the data hierarchy models,
      or an empty list if no models are provided.
  """
  if data_hierarchy is None:
    return []
  data_hierarchy_types = []
  for data_model in data_hierarchy:
    if (data_model and data_model.doc_type
        and data_model.doc_type not in ('x0', 'x1')):
      type_capitalized = data_model.doc_type.capitalize()
      if type_capitalized not in data_hierarchy_types:
        data_hierarchy_types.append(type_capitalized)
  data_hierarchy_types.append('Unidentified')
  return data_hierarchy_types


def get_db_info(logger: Logger) -> dict[str, str]:
  """Retrieves database information from the configuration.

  This function reads the configuration to obtain the database path and name
  associated with the default project group. It raises errors if the configuration
  is missing required fields, ensuring that the application has the necessary
  information to connect to the database.

  Args:
      logger (Logger): The logger instance used for logging errors and information.

  Returns:
      dict[str, str]: A dictionary containing the database path and name.

  Raises:
      ConfigError: If the configuration is missing required fields or contains invalid data.
  """
  config = PastaConfigReaderFactory.get_instance().config
  def_project_group_name = config.get('defaultProjectGroup')
  project_groups = config.get('projectGroups')
  if not def_project_group_name or not project_groups:
    raise log_and_create_error(logger, ConfigError,
                               'Incorrect config file, defaultProjectGroup/projectGroups not found!')
  main_group = project_groups.get(def_project_group_name)
  if not main_group:
    raise log_and_create_error(logger, ConfigError,
                               'Incorrect config file, defaultProjectGroup not found in projectGroups!')
  local_info = main_group.get('local')
  if not local_info:
    raise log_and_create_error(logger, ConfigError,
                               'Incorrect config file, user or password not found!')
  db_path = local_info.get('path')
  db_name = local_info.get('database')
  if db_name and db_path:
    return {
      'database_path': db_path,
      'database_name': db_name
    }
  else:
    raise log_and_create_error(logger, ConfigError,
                               'Incorrect config file, database name/path not found!')


def generate_project_join_statement(model_id: str | None) -> Executable:
  """Generates a SQL join statement for project models.

  This function constructs a SQL query to join the main project model with its
  associated properties based on the provided model ID. It allows for flexible
  querying of project data, including optional filtering based on the model ID.

  Args:
      model_id (str | None): The ID of the project model to filter by. If None,
      the query will not filter by model ID.

  Returns:
      Executable: A SQLAlchemy Executable object representing the constructed
      join statement.

  Raises:
      ValueError: If the model ID is invalid or if there is an error in the
      SQL statement construction.
  """
  properties_objective_aliased = aliased(PropertiesOrmModel)
  properties_status_aliased = aliased(PropertiesOrmModel)
  where_condition = and_(MainOrmModel.type == 'x0',
                         MainOrmModel.id == model_id) if model_id else MainOrmModel.type == 'x0'
  return (select(
    MainOrmModel,
    properties_status_aliased.value,
    properties_objective_aliased.value,
  ).where(where_condition).join_from(
    MainOrmModel,
    properties_objective_aliased,
    and_(
      MainOrmModel.id == properties_objective_aliased.id,
      properties_objective_aliased.key == '.objective',
    ),
    isouter=True,
  ).join_from(
    MainOrmModel,
    properties_status_aliased,
    and_(
      MainOrmModel.id == properties_status_aliased.id,
      properties_status_aliased.key == '.status',
    ),
    isouter=True,
  ))
