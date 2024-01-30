#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: incorrect_parameter_error.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
class IncorrectParameterError(Exception):
  """
  IncorrectParameterError for dataverse API
  """

  def __init__(self,
               message: str,
               detailed_errors: dict[str, str] = None):
    """
    Constructs IncorrectParameterError
    Args:
      message (str): Error message to be thrown
      detailed_errors (dict): Additional errors passed via exception
    """
    super().__init__(message)
    self.message = message
    self.detailed_errors = detailed_errors
