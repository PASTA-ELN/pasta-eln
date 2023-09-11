""" OntologyConfigKeyNotFoundException used for the ontology configuration """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: ontology_config_key_not_found_exception.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

class OntologyConfigKeyNotFoundException(Exception):
  """
  Custom exception class for null ontology document
  """
  def __init__(self,
               message: str,
               detailed_errors: dict[str, str]):
    """
    Constructs OntologyConfigKeyNotFoundException
    Args:
      message (str): Error message to be thrown
      detailed_errors (dict): Additional errors passed via exception
    """
    super().__init__(message)
    self.message = message
    self.detailed_errors = detailed_errors
