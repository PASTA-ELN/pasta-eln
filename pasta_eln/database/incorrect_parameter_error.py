""" Represents an error due to incorrect parameters. """


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
  Represents an error due to incorrect parameters.

  Explanation:
      This class represents an error that occurs when incorrect parameters are provided.
      It inherits from the Exception class.

  Args:
      message (str): The error message.
      detailed_errors (dict[str, str], optional): Additional detailed errors.
      Defaults to None.

  Returns:
      None
  """

  def __init__(self,
               message: str,
               detailed_errors: dict[str, str] | None = None):
    """
    Constructs an IncorrectParameterError instance.

    Args:
        message (str): The error message.
        detailed_errors (dict[str, str], optional): Additional detailed errors.
        Defaults to None.

    Returns:
        None
    """
    super().__init__(message)
    self.message = message
    self.detailed_errors = detailed_errors
