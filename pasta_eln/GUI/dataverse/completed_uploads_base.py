# Form implementation generated from reading ui file 'completed_uploads_base.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_CompletedUploadsForm:
  def setupUi(self, CompletedUploadsForm):
    CompletedUploadsForm.setObjectName('CompletedUploadsForm')
    CompletedUploadsForm.resize(1300, 475)
    self.gridLayout = QtWidgets.QGridLayout(CompletedUploadsForm)
    self.gridLayout.setObjectName('gridLayout')
    spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
    self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
    self.mainVerticalLayout = QtWidgets.QVBoxLayout()
    self.mainVerticalLayout.setObjectName('mainVerticalLayout')
    self.filterHorizontalLayout = QtWidgets.QHBoxLayout()
    self.filterHorizontalLayout.setObjectName('filterHorizontalLayout')
    self.filterTermLineEdit = QtWidgets.QLineEdit(parent=CompletedUploadsForm)
    self.filterTermLineEdit.setClearButtonEnabled(True)
    self.filterTermLineEdit.setObjectName('filterTermLineEdit')
    self.filterHorizontalLayout.addWidget(self.filterTermLineEdit)
    self.mainVerticalLayout.addLayout(self.filterHorizontalLayout)
    self.completedUploadsScrollArea = QtWidgets.QScrollArea(parent=CompletedUploadsForm)
    self.completedUploadsScrollArea.setWidgetResizable(True)
    self.completedUploadsScrollArea.setObjectName('completedUploadsScrollArea')
    self.scrollAreaWidgetContents = QtWidgets.QWidget()
    self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1278, 404))
    self.scrollAreaWidgetContents.setObjectName('scrollAreaWidgetContents')
    self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
    self.verticalLayout_3.setObjectName('verticalLayout_3')
    self.completedUploadsVerticalLayout = QtWidgets.QVBoxLayout()
    self.completedUploadsVerticalLayout.setObjectName('completedUploadsVerticalLayout')
    self.verticalLayout_3.addLayout(self.completedUploadsVerticalLayout)
    self.completedUploadsScrollArea.setWidget(self.scrollAreaWidgetContents)
    self.mainVerticalLayout.addWidget(self.completedUploadsScrollArea)
    self.gridLayout.addLayout(self.mainVerticalLayout, 0, 0, 1, 1)

    self.retranslateUi(CompletedUploadsForm)
    QtCore.QMetaObject.connectSlotsByName(CompletedUploadsForm)

  def retranslateUi(self, CompletedUploadsForm):
    _translate = QtCore.QCoreApplication.translate
    CompletedUploadsForm.setWindowTitle(_translate('CompletedUploadsForm', 'Dataverse upload history'))
    self.filterTermLineEdit.setToolTip(_translate('CompletedUploadsForm', 'Enter project name / dataverse URL / finished time to filter the below listed tasks.'))
    self.filterTermLineEdit.setPlaceholderText(_translate('CompletedUploadsForm', 'Enter the information to filter the tasks.'))
    self.completedUploadsScrollArea.setToolTip(_translate('CompletedUploadsForm', "<html><head/><body><p><span style=\" font-style:italic;\">Displays the history of finished dataverse uploads done in the past.</span></p></body></html>"))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CompletedUploadsForm = QtWidgets.QWidget()
    ui = Ui_CompletedUploadsForm()
    ui.setupUi(CompletedUploadsForm)
    CompletedUploadsForm.show()
    sys.exit(app.exec())
