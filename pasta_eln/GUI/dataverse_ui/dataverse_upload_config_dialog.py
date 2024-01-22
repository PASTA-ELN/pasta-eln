#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: dataverse_upload_config_dialog.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog

from pasta_eln.GUI.dataverse_ui.dataverse_upload_config_dialog_base import Ui_UploadConfigDialog


class DataverseUploadConfigDialog(Ui_UploadConfigDialog):

    def __new__(cls, *_: Any, **__: Any) -> Any:
        return super(DataverseUploadConfigDialog, cls).__new__(cls)

    def __init__(self) -> None:
        """
        Initializes the creation type dialog
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.instance = QDialog()
        super().setupUi(self.instance)
        self.numParallelComboBox.addItems(map(str, range(3, 26)))
        self.numParallelComboBox.setCurrentIndex(2)
        self.instance.setWindowModality(QtCore.Qt.ApplicationModal)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = DataverseUploadConfigDialog()
    ui.instance.show()
    sys.exit(app.exec())