""" GenericException used for the ontology configuration """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: generic_exception.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class GenericException(Exception):
  """
  Custom generic exception class for ontology configuration
  """

  def __init__(self,
               message: str,
               detailed_errors: dict[str, str]):
    """
    Constructs GenericException
    Args:
      message (str): Error message to be thrown
      detailed_errors (dict): Additional errors passed via exception
    """
    super().__init__(message)
    self.message = message
    self.detailed_errors = detailed_errors
