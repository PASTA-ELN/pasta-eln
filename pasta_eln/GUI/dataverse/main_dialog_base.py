# Form implementation generated from reading ui file 'main_dialog_base.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_MainDialogBase(object):
  def setupUi(self, MainDialogBase):
    MainDialogBase.setObjectName("MainDialogBase")
    MainDialogBase.resize(1261, 782)
    self.gridLayout = QtWidgets.QGridLayout(MainDialogBase)
    self.gridLayout.setObjectName("gridLayout")
    self.buttonBox = QtWidgets.QDialogButtonBox(parent=MainDialogBase)
    self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
    self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
    self.buttonBox.setObjectName("buttonBox")
    self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
    self.mainHorizontalLayout = QtWidgets.QHBoxLayout()
    self.mainHorizontalLayout.setObjectName("mainHorizontalLayout")
    self.mainVerticalLayout = QtWidgets.QVBoxLayout()
    self.mainVerticalLayout.setObjectName("mainVerticalLayout")
    self.scrollAreaHorizontalLayout = QtWidgets.QHBoxLayout()
    self.scrollAreaHorizontalLayout.setObjectName("scrollAreaHorizontalLayout")
    self.projectsScrollArea = QtWidgets.QScrollArea(parent=MainDialogBase)
    self.projectsScrollArea.setWidgetResizable(True)
    self.projectsScrollArea.setObjectName("projectsScrollArea")
    self.projectScrollAreaWidgetContents = QtWidgets.QWidget()
    self.projectScrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1235, 336))
    self.projectScrollAreaWidgetContents.setObjectName("projectScrollAreaWidgetContents")
    self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.projectScrollAreaWidgetContents)
    self.verticalLayout_3.setObjectName("verticalLayout_3")
    self.projectsScrollAreaVerticalLayout = QtWidgets.QVBoxLayout()
    self.projectsScrollAreaVerticalLayout.setObjectName("projectsScrollAreaVerticalLayout")
    self.verticalLayout_3.addLayout(self.projectsScrollAreaVerticalLayout)
    self.projectsScrollArea.setWidget(self.projectScrollAreaWidgetContents)
    self.scrollAreaHorizontalLayout.addWidget(self.projectsScrollArea)
    self.mainVerticalLayout.addLayout(self.scrollAreaHorizontalLayout)
    self.uploadButtonHorizontalLayout = QtWidgets.QHBoxLayout()
    self.uploadButtonHorizontalLayout.setObjectName("uploadButtonHorizontalLayout")
    spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    self.uploadButtonHorizontalLayout.addItem(spacerItem)
    self.selectAllPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.selectAllPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.selectAllPushButton.setObjectName("selectAllPushButton")
    self.uploadButtonHorizontalLayout.addWidget(self.selectAllPushButton)
    self.deselectAllPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.deselectAllPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.deselectAllPushButton.setObjectName("deselectAllPushButton")
    self.uploadButtonHorizontalLayout.addWidget(self.deselectAllPushButton)
    self.configureUploadPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.configureUploadPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.configureUploadPushButton.setObjectName("configureUploadPushButton")
    self.uploadButtonHorizontalLayout.addWidget(self.configureUploadPushButton)
    self.editFullMetadataPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.editFullMetadataPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.editFullMetadataPushButton.setObjectName("editFullMetadataPushButton")
    self.uploadButtonHorizontalLayout.addWidget(self.editFullMetadataPushButton)
    self.uploadPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.uploadPushButton.setMinimumSize(QtCore.QSize(100, 0))
    self.uploadPushButton.setObjectName("uploadPushButton")
    self.uploadButtonHorizontalLayout.addWidget(self.uploadPushButton)
    self.mainVerticalLayout.addLayout(self.uploadButtonHorizontalLayout)
    self.scrollAreaVerticalLayout = QtWidgets.QVBoxLayout()
    self.scrollAreaVerticalLayout.setObjectName("scrollAreaVerticalLayout")
    self.uploadQueueScrollArea = QtWidgets.QScrollArea(parent=MainDialogBase)
    self.uploadQueueScrollArea.setWidgetResizable(True)
    self.uploadQueueScrollArea.setObjectName("uploadQueueScrollArea")
    self.scrollAreaWidgetContents = QtWidgets.QWidget()
    self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1235, 302))
    self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
    self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
    self.verticalLayout.setObjectName("verticalLayout")
    self.uploadQueueVerticalLayout = QtWidgets.QVBoxLayout()
    self.uploadQueueVerticalLayout.setObjectName("uploadQueueVerticalLayout")
    self.verticalLayout.addLayout(self.uploadQueueVerticalLayout)
    self.uploadQueueScrollArea.setWidget(self.scrollAreaWidgetContents)
    self.scrollAreaVerticalLayout.addWidget(self.uploadQueueScrollArea)
    self.scrollAreaButtonsHorizontalLayout = QtWidgets.QHBoxLayout()
    self.scrollAreaButtonsHorizontalLayout.setObjectName("scrollAreaButtonsHorizontalLayout")
    spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    self.scrollAreaButtonsHorizontalLayout.addItem(spacerItem1)
    self.clearFinishedPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.clearFinishedPushButton.setMinimumSize(QtCore.QSize(150, 0))
    self.clearFinishedPushButton.setObjectName("clearFinishedPushButton")
    self.scrollAreaButtonsHorizontalLayout.addWidget(self.clearFinishedPushButton)
    self.cancelAllPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.cancelAllPushButton.setMinimumSize(QtCore.QSize(150, 0))
    self.cancelAllPushButton.setObjectName("cancelAllPushButton")
    self.scrollAreaButtonsHorizontalLayout.addWidget(self.cancelAllPushButton)
    self.showCompletedPushButton = QtWidgets.QPushButton(parent=MainDialogBase)
    self.showCompletedPushButton.setMinimumSize(QtCore.QSize(150, 0))
    self.showCompletedPushButton.setObjectName("showCompletedPushButton")
    self.scrollAreaButtonsHorizontalLayout.addWidget(self.showCompletedPushButton)
    self.scrollAreaVerticalLayout.addLayout(self.scrollAreaButtonsHorizontalLayout)
    self.mainVerticalLayout.addLayout(self.scrollAreaVerticalLayout)
    self.mainHorizontalLayout.addLayout(self.mainVerticalLayout)
    self.gridLayout.addLayout(self.mainHorizontalLayout, 0, 0, 1, 1)
    spacerItem2 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
    self.gridLayout.addItem(spacerItem2, 1, 0, 1, 1)

    self.retranslateUi(MainDialogBase)
    self.buttonBox.accepted.connect(MainDialogBase.accept) # type: ignore
    self.buttonBox.rejected.connect(MainDialogBase.reject) # type: ignore
    QtCore.QMetaObject.connectSlotsByName(MainDialogBase)

  def retranslateUi(self, MainDialogBase):
    _translate = QtCore.QCoreApplication.translate
    MainDialogBase.setWindowTitle(_translate("MainDialogBase", "Dataverse upload"))
    self.selectAllPushButton.setToolTip(_translate("MainDialogBase", "Select all the projects listed above."))
    self.selectAllPushButton.setText(_translate("MainDialogBase", "Select all"))
    self.deselectAllPushButton.setToolTip(_translate("MainDialogBase", "Deselect all the projects listed above."))
    self.deselectAllPushButton.setText(_translate("MainDialogBase", "Deselect all"))
    self.configureUploadPushButton.setToolTip(_translate("MainDialogBase", "Configure the contents of projects which need to be uploaded to dataverse."))
    self.configureUploadPushButton.setText(_translate("MainDialogBase", "Configure"))
    self.editFullMetadataPushButton.setToolTip(_translate("MainDialogBase", "Click to edit full/minimal list of metadata to be used for dataverse upload."))
    self.editFullMetadataPushButton.setText(_translate("MainDialogBase", "Edit metadata"))
    self.uploadPushButton.setToolTip(_translate("MainDialogBase", "Start uploading the above selected projects to dataverse."))
    self.uploadPushButton.setText(_translate("MainDialogBase", "Start upload"))
    self.uploadQueueScrollArea.setToolTip(_translate("MainDialogBase", "<html><head/><body><p><span style=\" font-style:italic;\">Displays the enqueued lists of PASTA projects to be uploaded to dataverse.</span><span style=\" font-style:italic;\">Users can view individual logs for each project upload, cancel each or all of them and also clear all the finished items anytime.</span></p></body></html>"))
    self.clearFinishedPushButton.setToolTip(_translate("MainDialogBase", "Clear all finished uploads."))
    self.clearFinishedPushButton.setText(_translate("MainDialogBase", "Clear finished"))
    self.cancelAllPushButton.setToolTip(_translate("MainDialogBase", "Cancel all the ongoing uploads."))
    self.cancelAllPushButton.setText(_translate("MainDialogBase", "Cancel all"))
    self.showCompletedPushButton.setToolTip(_translate("MainDialogBase", "Show uploaded projects history."))
    self.showCompletedPushButton.setText(_translate("MainDialogBase", "Show completed"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainDialogBase = QtWidgets.QDialog()
    ui = Ui_MainDialogBase()
    ui.setupUi(MainDialogBase)
    MainDialogBase.show()
    sys.exit(app.exec())
