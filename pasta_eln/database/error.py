""" Represents an error in the database. """


#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: error.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class Error(Exception):
  """
  Represents an error in the database.

  Explanation:
      This class represents a database error and inherits from the Exception class.
      It provides a way to construct a DatabaseError instance with the provided message and detailed_errors.

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
    Constructs a DatabaseError instance.

    Explanation:
        This method initializes a DatabaseError instance with the provided message and detailed_errors.
        It inherits from the Exception class.

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
