#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: terminology_lookup_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging

from PySide6 import QtWidgets, QtCore

from pasta_eln.GUI.ontology_configuration.terminology_lookup_dialog_base import Ui_TerminologyLookupDialogBase


class TerminologyLookupDialog(Ui_TerminologyLookupDialogBase):

  def __init__(self) -> None:
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    # Set up the UI elements
    self.instance = QtWidgets.QDialog()
    super().setupUi(self.instance)

  def show(self) -> None:
    """
    Displays the dialog

    Returns: None

    """
    self.instance.setWindowModality(QtCore.Qt.ApplicationModal)
    self.instance.show()


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)
  TerminologyLookupDialogBase = TerminologyLookupDialog()
  TerminologyLookupDialogBase.instance.show()
  sys.exit(app.exec())
