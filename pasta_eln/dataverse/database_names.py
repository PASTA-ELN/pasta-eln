""" Enumeration for database names. """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: database_names.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from enum import Enum


class DatabaseNames(Enum):
  """Enumeration for database names.

  This class defines a set of constants representing different database names used in the application.
  Each member of the enumeration corresponds to a specific database with an associated integer value.

  Attributes:
      DataverseDatabase: Represents the Dataverse database with a value of 1.
      PastaProjectGroupDatabase: Represents the Pasta Project Group database with a value of 2.
  """
  DataverseDatabase = 1
  PastaProjectGroupDatabase = 2
