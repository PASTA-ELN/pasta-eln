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
from json import load
from logging import Logger
from os.path import exists, join
from pathlib import Path
from typing import Any, Type

from PySide6.QtWidgets import QLabel
from qtawesome import icon

from pasta_eln.dataverse.database_error import DatabaseError
from pasta_eln.dataverse.upload_status_values import UploadStatusValues


def update_status(status: str,
                  statusIconLabel: QLabel,
                  statusLabel: QLabel) -> None:
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

  Returns:
      None
  """
  config = read_pasta_config_file(logger)
  if 'authors' not in config:
    raise log_and_create_error(logger, DatabaseError, "Incorrect config file, authors not found!")
  author_field = next(f for f in metadata['datasetVersion']['metadataBlocks']['citation']['fields'] if
                      f['typeName'] == 'author')
  authors_list = author_field['value']
  if not authors_list:
    raise log_and_create_error(logger, DatabaseError, "Incorrect config file, authors not found!")
  author_copy = authors_list[0].copy()
  authors_list.clear()
  for author in config['authors']:
    author_copy['authorName']['value'] = ', '.join(filter(None, [author['last'], author['first']]))
    author_copy['authorIdentifierScheme']['value'] = "ORCID"
    author_copy['authorIdentifier']['value'] = author['orcid']
    author_copy['authorAffiliation']['value'] = ', '.join([o['organization'] for o in author['organizations']])
    authors_list.append(copy.deepcopy(author_copy))


def read_pasta_config_file(logger: Logger) -> dict[str, Any] | None:
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
    raise log_and_create_error(logger, DatabaseError, "Config file not found, Corrupt installation!")
  with open(config_file_name, 'r', encoding='utf-8') as confFile:
    config = load(confFile)
  return config


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
