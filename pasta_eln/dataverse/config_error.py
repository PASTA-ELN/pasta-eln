""" Exception raised for configuration errors (reading/writing PASTA config file). """


#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: config_error.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class ConfigError(Exception):
  """
  Exception raised for configuration errors (reading/writing PASTA config file).

  Explanation:
  This class represents a custom exception for configuration errors. It is raised when there is an error in the configuration.

  Args:
      message (str): The error message.
      detailed_errors (dict[str, str] | None): Optional detailed error information.

  Attributes:
      message (str): The error message.
      detailed_errors (dict[str, str] | None): Optional detailed error information.
  """

  def __init__(self,
               message: str,
               detailed_errors: dict[str, str] | None = None) -> None:
    """
    Initializes a ConfigError exception.

    Explanation:
    This class represents a custom exception for configuration errors. It is raised when there is an error in the configuration.

    Args:
        message (str): The error message.
        detailed_errors (dict[str, str] | None): Optional detailed error information.

    Attributes:
        message (str): The error message.
        detailed_errors (dict[str, str] | None): Optional detailed error information.
    """
    super().__init__(message)
    self.message = message
    self.detailed_errors = detailed_errors
