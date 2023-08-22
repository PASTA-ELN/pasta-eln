#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: create_type_dialog_extended.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6 import QtWidgets

from pasta_eln.ontology_configuration.create_type_dialog.create_type_dialog import Ui_CreateTypeDialog


class CreateTypeDialog(Ui_CreateTypeDialog):

    def __init__(self, accepted_callback, rejected_callback):
      """
      Instantiates the create type dialog
      """
      self.next_struct_level = None
      self.instance = QtWidgets.QDialog()
      ui = super()
      ui.setupUi(self.instance)
      self.buttonBox.accepted.connect(accepted_callback)
      self.buttonBox.rejected.connect(rejected_callback)
      self.structuralLevelCheckBox.stateChanged.connect(self.structural_level_checkbox_callback)

    def structural_level_checkbox_callback(self):
      """Callback invoked when the state changes for structuralLevelCheckBox

      Returns:
          None
      """
      if self.structuralLevelCheckBox.isChecked():
        self.titleLineEdit.setText(self.next_struct_level)
        self.titleLineEdit.setDisabled(True)
      else:
        self.titleLineEdit.clear()
        self.titleLineEdit.setDisabled(False)
    def show(self):
        """Displays the dialog

        Args:


        Returns:
            None
        """
        self.instance.show()
        self.instance.exec_()

    def clear_ui(self):
      self.labelLineEdit.clear()
      self.titleLineEdit.clear()
      self.structuralLevelCheckBox.setChecked(False)

    def set_structural_level_title(self, structural_level: str):
      """
      Set the next possible structural level
      Args:
        structural_level: Passed in structural level of the format (x0, x1, x2 ...)

      Returns: None

      """
      self.next_struct_level = structural_level



