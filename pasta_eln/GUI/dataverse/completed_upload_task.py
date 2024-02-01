# Form implementation generated from reading ui file 'completed_upload_task.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_CompletedUploadTaskFrame(object):
  def setupUi(self, CompletedUploadTaskFrame):
    CompletedUploadTaskFrame.setObjectName("CompletedUploadTaskFrame")
    CompletedUploadTaskFrame.resize(1288, 64)
    CompletedUploadTaskFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
    CompletedUploadTaskFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
    self.horizontalLayout_2 = QtWidgets.QHBoxLayout(CompletedUploadTaskFrame)
    self.horizontalLayout_2.setObjectName("horizontalLayout_2")
    self.horizontalLayout = QtWidgets.QHBoxLayout()
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.projectNameLabel = QtWidgets.QLabel(parent=CompletedUploadTaskFrame)
    self.projectNameLabel.setObjectName("projectNameLabel")
    self.horizontalLayout.addWidget(self.projectNameLabel)
    self.dataverseUrlLabel = QtWidgets.QLabel(parent=CompletedUploadTaskFrame)
    self.dataverseUrlLabel.setObjectName("dataverseUrlLabel")
    self.horizontalLayout.addWidget(self.dataverseUrlLabel)
    self.finishedDateTimeLabel = QtWidgets.QLabel(parent=CompletedUploadTaskFrame)
    self.finishedDateTimeLabel.setObjectName("finishedDateTimeLabel")
    self.horizontalLayout.addWidget(self.finishedDateTimeLabel)
    self.statusLabel = QtWidgets.QLabel(parent=CompletedUploadTaskFrame)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.statusLabel.sizePolicy().hasHeightForWidth())
    self.statusLabel.setSizePolicy(sizePolicy)
    self.statusLabel.setMinimumSize(QtCore.QSize(100, 0))
    self.statusLabel.setObjectName("statusLabel")
    self.horizontalLayout.addWidget(self.statusLabel)
    self.horizontalLayout_2.addLayout(self.horizontalLayout)

    self.retranslateUi(CompletedUploadTaskFrame)
    QtCore.QMetaObject.connectSlotsByName(CompletedUploadTaskFrame)

  def retranslateUi(self, CompletedUploadTaskFrame):
    _translate = QtCore.QCoreApplication.translate
    CompletedUploadTaskFrame.setWindowTitle(_translate("CompletedUploadTaskFrame", "Frame"))
    self.projectNameLabel.setToolTip(_translate("CompletedUploadTaskFrame", "PASTA project name which was uploaded to dataverse."))
    self.projectNameLabel.setText(_translate("CompletedUploadTaskFrame", "Example Project 1"))
    self.dataverseUrlLabel.setToolTip(_translate("CompletedUploadTaskFrame", "The dataverse URL where the PASTA project was uploaded."))
    self.dataverseUrlLabel.setText(_translate("CompletedUploadTaskFrame", "<html><head/><body><p>Dataverse URL: <a href=\"https://data-beta.fz-juelich.de/dataset.xhtml?persistentId=doi:10.0346/JUELICH-DATA-BETA/BORORQ\"><span style=\" text-decoration: underline; color:#0000ff;\">Test Data Set 12</span></a></p></body></html>"))
    self.finishedDateTimeLabel.setToolTip(_translate("CompletedUploadTaskFrame", "Dataverse upload time."))
    self.finishedDateTimeLabel.setText(_translate("CompletedUploadTaskFrame", "01-16-2024 10:52:15"))
    self.statusLabel.setToolTip(_translate("CompletedUploadTaskFrame", "Displays the status of the upload."))
    self.statusLabel.setText(_translate("CompletedUploadTaskFrame", "Queued"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CompletedUploadTaskFrame = QtWidgets.QFrame()
    ui = Ui_CompletedUploadTaskFrame()
    ui.setupUi(CompletedUploadTaskFrame)
    CompletedUploadTaskFrame.show()
    sys.exit(app.exec())