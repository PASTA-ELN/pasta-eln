# Form implementation generated from reading ui file 'create_type_dialog_base.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_CreateTypeDialogBase(object):
  def setupUi(self, CreateTypeDialogBase):
    CreateTypeDialogBase.setObjectName("CreateTypeDialogBase")
    CreateTypeDialogBase.resize(584, 375)
    self.gridLayout = QtWidgets.QGridLayout(CreateTypeDialogBase)
    self.gridLayout.setObjectName("gridLayout")
    self.mainVerticalLayout = QtWidgets.QVBoxLayout()
    self.mainVerticalLayout.setContentsMargins(20, -1, 20, -1)
    self.mainVerticalLayout.setObjectName("mainVerticalLayout")
    self.tileHorizontalLayout = QtWidgets.QHBoxLayout()
    self.tileHorizontalLayout.setObjectName("tileHorizontalLayout")
    self.titleLabel = QtWidgets.QLabel(parent=CreateTypeDialogBase)
    self.titleLabel.setMinimumSize(QtCore.QSize(120, 0))
    self.titleLabel.setObjectName("titleLabel")
    self.tileHorizontalLayout.addWidget(self.titleLabel)
    spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    self.tileHorizontalLayout.addItem(spacerItem)
    self.titleLineEdit = QtWidgets.QLineEdit(parent=CreateTypeDialogBase)
    self.titleLineEdit.setClearButtonEnabled(True)
    self.titleLineEdit.setObjectName("titleLineEdit")
    self.tileHorizontalLayout.addWidget(self.titleLineEdit)
    self.mainVerticalLayout.addLayout(self.tileHorizontalLayout)
    self.displayedTitleHorizontalLayout = QtWidgets.QHBoxLayout()
    self.displayedTitleHorizontalLayout.setObjectName("displayedTitleHorizontalLayout")
    self.typeLabel = QtWidgets.QLabel(parent=CreateTypeDialogBase)
    self.typeLabel.setMinimumSize(QtCore.QSize(120, 0))
    self.typeLabel.setObjectName("typeLabel")
    self.displayedTitleHorizontalLayout.addWidget(self.typeLabel)
    spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    self.displayedTitleHorizontalLayout.addItem(spacerItem1)
    self.displayedTitleLineEdit = QtWidgets.QLineEdit(parent=CreateTypeDialogBase)
    self.displayedTitleLineEdit.setClearButtonEnabled(True)
    self.displayedTitleLineEdit.setObjectName("displayedTitleLineEdit")
    self.displayedTitleHorizontalLayout.addWidget(self.displayedTitleLineEdit)
    self.mainVerticalLayout.addLayout(self.displayedTitleHorizontalLayout)
    spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
    self.mainVerticalLayout.addItem(spacerItem2)
    self.checkBoxHorizontalLayout = QtWidgets.QHBoxLayout()
    self.checkBoxHorizontalLayout.setObjectName("checkBoxHorizontalLayout")
    self.structuralLevelCheckBox = QtWidgets.QCheckBox(parent=CreateTypeDialogBase)
    self.structuralLevelCheckBox.setObjectName("structuralLevelCheckBox")
    self.checkBoxHorizontalLayout.addWidget(self.structuralLevelCheckBox)
    self.mainVerticalLayout.addLayout(self.checkBoxHorizontalLayout)
    self.mainVerticalLayout.setStretch(0, 1)
    self.mainVerticalLayout.setStretch(1, 1)
    self.mainVerticalLayout.setStretch(2, 1)
    self.mainVerticalLayout.setStretch(3, 1)
    self.gridLayout.addLayout(self.mainVerticalLayout, 0, 0, 1, 1)
    self.buttonBox = QtWidgets.QDialogButtonBox(parent=CreateTypeDialogBase)
    self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
    self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
    self.buttonBox.setObjectName("buttonBox")
    self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

    self.retranslateUi(CreateTypeDialogBase)
    self.buttonBox.accepted.connect(CreateTypeDialogBase.accept) # type: ignore
    self.buttonBox.rejected.connect(CreateTypeDialogBase.reject) # type: ignore
    QtCore.QMetaObject.connectSlotsByName(CreateTypeDialogBase)

  def retranslateUi(self, CreateTypeDialogBase):
    _translate = QtCore.QCoreApplication.translate
    CreateTypeDialogBase.setWindowTitle(_translate("CreateTypeDialogBase", "Create New Type"))
    self.titleLabel.setText(_translate("CreateTypeDialogBase", "Title in the hierarchy"))
    self.titleLineEdit.setToolTip(_translate("CreateTypeDialogBase", "Exclude titles which start with \'x\' (reserved for structure level titles) or whitespace"))
    self.titleLineEdit.setPlaceholderText(_translate("CreateTypeDialogBase", "Enter the Data Type title for the hierarchy"))
    self.typeLabel.setText(_translate("CreateTypeDialogBase", "Displayed title"))
    self.displayedTitleLineEdit.setToolTip(_translate("CreateTypeDialogBase", "Enter displayed title for the new type, which can also be modified later in the main editor window"))
    self.displayedTitleLineEdit.setPlaceholderText(_translate("CreateTypeDialogBase", "Enter the displayed title of the Data Type"))
    self.structuralLevelCheckBox.setToolTip(_translate("CreateTypeDialogBase", "If this is a structural type, then title will be automatically populated as (x0, x1...xn). Next number will be chosen for xn from the existing list of structural items."))
    self.structuralLevelCheckBox.setText(_translate("CreateTypeDialogBase", "Is this a structural Type?"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CreateTypeDialogBase = QtWidgets.QDialog()
    ui = Ui_CreateTypeDialogBase()
    ui.setupUi(CreateTypeDialogBase)
    CreateTypeDialogBase.show()
    sys.exit(app.exec())