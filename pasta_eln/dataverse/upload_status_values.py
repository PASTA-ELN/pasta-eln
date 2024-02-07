""" Represents the possible upload status values. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_status_values.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from enum import Enum


class UploadStatusValues(Enum):
  """
  Represents the possible upload status values.

  Explanation:
      This enumeration class defines the possible values for the upload status.
      It provides a set of named constants to represent different upload statuses.

  Examples:
      UploadStatusValues.Queued
      UploadStatusValues.Uploading
      UploadStatusValues.Cancelled
      UploadStatusValues.Finished
      UploadStatusValues.Error
      UploadStatusValues.Warning
  """
  Queued = 1
  Uploading = 2
  Cancelled = 3
  Finished = 4
  Error = 5
  Warning = 6
