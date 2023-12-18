# Form implementation generated from reading ui file 'terminology_lookup_dialog_base.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_TerminologyLookupDialogBase(object):
  def setupUi(self, TerminologyLookupDialogBase):
    TerminologyLookupDialogBase.setObjectName("TerminologyLookupDialogBase")
    TerminologyLookupDialogBase.resize(900, 767)
    self.gridLayout = QtWidgets.QGridLayout(TerminologyLookupDialogBase)
    self.gridLayout.setObjectName("gridLayout")
    self.buttonBox = QtWidgets.QDialogButtonBox(parent=TerminologyLookupDialogBase)
    self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
    self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
    self.buttonBox.setObjectName("buttonBox")
    self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
    self.mainVerticalLayout = QtWidgets.QVBoxLayout()
    self.mainVerticalLayout.setObjectName("mainVerticalLayout")
    self.searchBarHorizontalLayout = QtWidgets.QHBoxLayout()
    self.searchBarHorizontalLayout.setObjectName("searchBarHorizontalLayout")
    self.terminologyLineEdit = QtWidgets.QLineEdit(parent=TerminologyLookupDialogBase)
    self.terminologyLineEdit.setClearButtonEnabled(True)
    self.terminologyLineEdit.setObjectName("terminologyLineEdit")
    self.searchBarHorizontalLayout.addWidget(self.terminologyLineEdit)
    self.terminologySearchPushButton = QtWidgets.QPushButton(parent=TerminologyLookupDialogBase)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.terminologySearchPushButton.sizePolicy().hasHeightForWidth())
    self.terminologySearchPushButton.setSizePolicy(sizePolicy)
    self.terminologySearchPushButton.setMinimumSize(QtCore.QSize(150, 0))
    self.terminologySearchPushButton.setObjectName("terminologySearchPushButton")
    self.searchBarHorizontalLayout.addWidget(self.terminologySearchPushButton)
    self.mainVerticalLayout.addLayout(self.searchBarHorizontalLayout)
    self.searchProgressBar = QtWidgets.QProgressBar(parent=TerminologyLookupDialogBase)
    self.searchProgressBar.setProperty("value", 0)
    self.searchProgressBar.setObjectName("searchProgressBar")
    self.mainVerticalLayout.addWidget(self.searchProgressBar)
    self.scrollAreaHorizontalLayout = QtWidgets.QHBoxLayout()
    self.scrollAreaHorizontalLayout.setObjectName("scrollAreaHorizontalLayout")
    self.scrollArea = QtWidgets.QScrollArea(parent=TerminologyLookupDialogBase)
    self.scrollArea.setWidgetResizable(True)
    self.scrollArea.setObjectName("scrollArea")
    self.scrollAreaWidgetContents = QtWidgets.QWidget()
    self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 876, 415))
    self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
    self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
    self.gridLayout_2.setObjectName("gridLayout_2")
    self.scrollAreaContentsVerticalLayout = QtWidgets.QVBoxLayout()
    self.scrollAreaContentsVerticalLayout.setObjectName("scrollAreaContentsVerticalLayout")
    self.gridLayout_2.addLayout(self.scrollAreaContentsVerticalLayout, 0, 0, 1, 1)
    self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    self.scrollAreaHorizontalLayout.addWidget(self.scrollArea)
    self.mainVerticalLayout.addLayout(self.scrollAreaHorizontalLayout)
    self.errorConsoleVerticalLayout = QtWidgets.QVBoxLayout()
    self.errorConsoleVerticalLayout.setObjectName("errorConsoleVerticalLayout")
    self.errorButtonsHorizontalLayout = QtWidgets.QHBoxLayout()
    self.errorButtonsHorizontalLayout.setObjectName("errorButtonsHorizontalLayout")
    self.errorConsolePushButton = QtWidgets.QPushButton(parent=TerminologyLookupDialogBase)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.errorConsolePushButton.sizePolicy().hasHeightForWidth())
    self.errorConsolePushButton.setSizePolicy(sizePolicy)
    self.errorConsolePushButton.setMinimumSize(QtCore.QSize(150, 0))
    self.errorConsolePushButton.setObjectName("errorConsolePushButton")
    self.errorButtonsHorizontalLayout.addWidget(self.errorConsolePushButton)
    spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    self.errorButtonsHorizontalLayout.addItem(spacerItem)
    self.errorConsoleVerticalLayout.addLayout(self.errorButtonsHorizontalLayout)
    self.errorConsoleTextEdit = QtWidgets.QTextEdit(parent=TerminologyLookupDialogBase)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.errorConsoleTextEdit.sizePolicy().hasHeightForWidth())
    self.errorConsoleTextEdit.setSizePolicy(sizePolicy)
    self.errorConsoleTextEdit.setMinimumSize(QtCore.QSize(0, 0))
    self.errorConsoleTextEdit.setObjectName("errorConsoleTextEdit")
    self.errorConsoleVerticalLayout.addWidget(self.errorConsoleTextEdit)
    self.mainVerticalLayout.addLayout(self.errorConsoleVerticalLayout)
    self.gridLayout.addLayout(self.mainVerticalLayout, 0, 0, 1, 1)

    self.retranslateUi(TerminologyLookupDialogBase)
    self.buttonBox.accepted.connect(TerminologyLookupDialogBase.accept) # type: ignore
    self.buttonBox.rejected.connect(TerminologyLookupDialogBase.reject) # type: ignore
    QtCore.QMetaObject.connectSlotsByName(TerminologyLookupDialogBase)

  def retranslateUi(self, TerminologyLookupDialogBase):
    _translate = QtCore.QCoreApplication.translate
    TerminologyLookupDialogBase.setWindowTitle(_translate("TerminologyLookupDialogBase", "Terminology Lookup"))
    self.terminologyLineEdit.setPlaceholderText(_translate("TerminologyLookupDialogBase", "\"Search for Definitions in Wikis/Ontologies\""))
    self.terminologySearchPushButton.setText(_translate("TerminologyLookupDialogBase", "Search"))
    self.errorConsolePushButton.setText(_translate("TerminologyLookupDialogBase", "Show/Hide Errors"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TerminologyLookupDialogBase = QtWidgets.QDialog()
    ui = Ui_TerminologyLookupDialogBase()
    ui.setupUi(TerminologyLookupDialogBase)
    TerminologyLookupDialogBase.show()
    sys.exit(app.exec())