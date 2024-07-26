#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: data_type_class_names.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from enum import Enum

class DataTypeClassName(Enum):
    PRIMITIVE = "primitive"
    COMPOUND = "compound"
    CONTROLLED_VOCAB = "controlledVocabulary"

    def __str__(self):
        return self.value
