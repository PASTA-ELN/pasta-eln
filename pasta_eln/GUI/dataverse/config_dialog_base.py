# Form implementation generated from reading ui file 'config_dialog_base.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_ConfigDialogBase(object):
  def setupUi(self, ConfigDialogBase):
    ConfigDialogBase.setObjectName("ConfigDialogBase")
    ConfigDialogBase.resize(1070, 192)
    self.gridLayout = QtWidgets.QGridLayout(ConfigDialogBase)
    self.gridLayout.setObjectName("gridLayout")
    self.buttonBox = QtWidgets.QDialogButtonBox(parent=ConfigDialogBase)
    self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
    self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Save)
    self.buttonBox.setObjectName("buttonBox")
    self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
    self.mainVerticalLayout = QtWidgets.QVBoxLayout()
    self.mainVerticalLayout.setObjectName("mainVerticalLayout")
    self.serverHorizontalLayout = QtWidgets.QHBoxLayout()
    self.serverHorizontalLayout.setObjectName("serverHorizontalLayout")
    self.dataverseServerLabel = QtWidgets.QLabel(parent=ConfigDialogBase)
    self.dataverseServerLabel.setMinimumSize(QtCore.QSize(200, 0))
    self.dataverseServerLabel.setObjectName("dataverseServerLabel")
    self.serverHorizontalLayout.addWidget(self.dataverseServerLabel)
    self.dataverseServerLineEdit = QtWidgets.QLineEdit(parent=ConfigDialogBase)
    self.dataverseServerLineEdit.setClearButtonEnabled(True)
    self.dataverseServerLineEdit.setObjectName("dataverseServerLineEdit")
    self.serverHorizontalLayout.addWidget(self.dataverseServerLineEdit)
    spacerItem = QtWidgets.QSpacerItem(213, 20, QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
    self.serverHorizontalLayout.addItem(spacerItem)
    self.mainVerticalLayout.addLayout(self.serverHorizontalLayout)
    spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
    self.mainVerticalLayout.addItem(spacerItem1)
    self.apiTokenHorizontalLayout = QtWidgets.QHBoxLayout()
    self.apiTokenHorizontalLayout.setObjectName("apiTokenHorizontalLayout")
    self.apiTokenLabel = QtWidgets.QLabel(parent=ConfigDialogBase)
    self.apiTokenLabel.setMinimumSize(QtCore.QSize(200, 0))
    self.apiTokenLabel.setObjectName("apiTokenLabel")
    self.apiTokenHorizontalLayout.addWidget(self.apiTokenLabel)
    self.apiTokenLineEdit = QtWidgets.QLineEdit(parent=ConfigDialogBase)
    self.apiTokenLineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
    self.apiTokenLineEdit.setClearButtonEnabled(True)
    self.apiTokenLineEdit.setObjectName("apiTokenLineEdit")
    self.apiTokenHorizontalLayout.addWidget(self.apiTokenLineEdit)
    self.apiTokenVerifyPushButton = QtWidgets.QPushButton(parent=ConfigDialogBase)
    self.apiTokenVerifyPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.apiTokenVerifyPushButton.setObjectName("apiTokenVerifyPushButton")
    self.apiTokenHorizontalLayout.addWidget(self.apiTokenVerifyPushButton)
    self.apiTokenHelpPushButton = QtWidgets.QPushButton(parent=ConfigDialogBase)
    self.apiTokenHelpPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.apiTokenHelpPushButton.setObjectName("apiTokenHelpPushButton")
    self.apiTokenHorizontalLayout.addWidget(self.apiTokenHelpPushButton)
    self.mainVerticalLayout.addLayout(self.apiTokenHorizontalLayout)
    spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
    self.mainVerticalLayout.addItem(spacerItem2)
    self.dataverseListHorizontalLayout = QtWidgets.QHBoxLayout()
    self.dataverseListHorizontalLayout.setObjectName("dataverseListHorizontalLayout")
    self.dataverseListLabel = QtWidgets.QLabel(parent=ConfigDialogBase)
    self.dataverseListLabel.setMinimumSize(QtCore.QSize(200, 0))
    self.dataverseListLabel.setObjectName("dataverseListLabel")
    self.dataverseListHorizontalLayout.addWidget(self.dataverseListLabel)
    self.dataverseListComboBox = QtWidgets.QComboBox(parent=ConfigDialogBase)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.dataverseListComboBox.sizePolicy().hasHeightForWidth())
    self.dataverseListComboBox.setSizePolicy(sizePolicy)
    self.dataverseListComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    self.dataverseListComboBox.setObjectName("dataverseListComboBox")
    self.dataverseListHorizontalLayout.addWidget(self.dataverseListComboBox)
    self.dataverseLineEdit = QtWidgets.QLineEdit(parent=ConfigDialogBase)
    self.dataverseLineEdit.setObjectName("dataverseLineEdit")
    self.dataverseListHorizontalLayout.addWidget(self.dataverseLineEdit)
    self.dataverseLoadPushButton = QtWidgets.QPushButton(parent=ConfigDialogBase)
    self.dataverseLoadPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.dataverseLoadPushButton.setObjectName("dataverseLoadPushButton")
    self.dataverseListHorizontalLayout.addWidget(self.dataverseLoadPushButton)
    spacerItem3 = QtWidgets.QSpacerItem(105, 20, QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
    self.dataverseListHorizontalLayout.addItem(spacerItem3)
    self.mainVerticalLayout.addLayout(self.dataverseListHorizontalLayout)
    spacerItem4 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
    self.mainVerticalLayout.addItem(spacerItem4)
    self.gridLayout.addLayout(self.mainVerticalLayout, 0, 0, 1, 1)

    self.retranslateUi(ConfigDialogBase)
    self.buttonBox.accepted.connect(ConfigDialogBase.accept) # type: ignore
    self.buttonBox.rejected.connect(ConfigDialogBase.reject) # type: ignore
    QtCore.QMetaObject.connectSlotsByName(ConfigDialogBase)

  def retranslateUi(self, ConfigDialogBase):
    _translate = QtCore.QCoreApplication.translate
    ConfigDialogBase.setWindowTitle(_translate("ConfigDialogBase", "Dataverse configuration"))
    self.dataverseServerLabel.setText(_translate("ConfigDialogBase", "Dataverse URL"))
    self.dataverseServerLineEdit.setToolTip(_translate("ConfigDialogBase", "Enter the dataverse server URL."))
    self.dataverseServerLineEdit.setPlaceholderText(_translate("ConfigDialogBase", "Enter the dataverse server URL, e.g. https://data.fz-juelich.de/"))
    self.apiTokenLabel.setText(_translate("ConfigDialogBase", "API token"))
    self.apiTokenLineEdit.setToolTip(_translate("ConfigDialogBase", "Enter the API token."))
    self.apiTokenLineEdit.setPlaceholderText(_translate("ConfigDialogBase", "Enter the API token, e.g. c6527048-5bdc-48b0-a1d5-ed1b62c4513b"))
    self.apiTokenVerifyPushButton.setToolTip(_translate("ConfigDialogBase", "Verify if the given dataverse server and api token are reachable."))
    self.apiTokenVerifyPushButton.setText(_translate("ConfigDialogBase", "Verify"))
    self.apiTokenHelpPushButton.setToolTip(_translate("ConfigDialogBase", "Navigate to the help page for generating dataverse API token."))
    self.apiTokenHelpPushButton.setText(_translate("ConfigDialogBase", "Help"))
    self.dataverseListLabel.setText(_translate("ConfigDialogBase", "Dataverse list"))
    self.dataverseListComboBox.setToolTip(_translate("ConfigDialogBase", "Displays the dataverse list from the server."))
    self.dataverseLineEdit.setToolTip(_translate("ConfigDialogBase", "Displays the ID of the selected dataverse from the list."))
    self.dataverseLineEdit.setPlaceholderText(_translate("ConfigDialogBase", "Selected Dataverse ID"))
    self.dataverseLoadPushButton.setToolTip(_translate("ConfigDialogBase", "Loads available dataverse list from the server."))
    self.dataverseLoadPushButton.setText(_translate("ConfigDialogBase", "Load"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfigDialogBase = QtWidgets.QDialog()
    ui = Ui_ConfigDialogBase()
    ui.setupUi(ConfigDialogBase)
    ConfigDialogBase.show()
    sys.exit(app.exec())
