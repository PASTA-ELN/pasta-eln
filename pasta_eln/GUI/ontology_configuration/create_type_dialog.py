# Form implementation generated from reading ui file 'create_type_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_CreateTypeDialog(object):
  def setupUi(self, CreateTypeDialog):
    CreateTypeDialog.setObjectName("CreateTypeDialog")
    CreateTypeDialog.resize(459, 301)
    self.buttonBox = QtWidgets.QDialogButtonBox(parent=CreateTypeDialog)
    self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
    self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
    self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
    self.buttonBox.setObjectName("buttonBox")
    self.verticalLayoutWidget = QtWidgets.QWidget(parent=CreateTypeDialog)
    self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 461, 221))
    self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
    self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
    self.mainVerticalLayout.setContentsMargins(20, 0, 20, 0)
    self.mainVerticalLayout.setObjectName("mainVerticalLayout")
    self.tileHorizontalLayout = QtWidgets.QHBoxLayout()
    self.tileHorizontalLayout.setObjectName("tileHorizontalLayout")
    self.titleLabel = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
    self.titleLabel.setMinimumSize(QtCore.QSize(120, 0))
    self.titleLabel.setObjectName("titleLabel")
    self.tileHorizontalLayout.addWidget(self.titleLabel)
    spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    self.tileHorizontalLayout.addItem(spacerItem)
    self.titleLineEdit = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget)
    self.titleLineEdit.setObjectName("titleLineEdit")
    self.tileHorizontalLayout.addWidget(self.titleLineEdit)
    self.mainVerticalLayout.addLayout(self.tileHorizontalLayout)
    self.horizontalLayout = QtWidgets.QHBoxLayout()
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.typeLabel = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
    self.typeLabel.setMinimumSize(QtCore.QSize(120, 0))
    self.typeLabel.setObjectName("typeLabel")
    self.horizontalLayout.addWidget(self.typeLabel)
    spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    self.horizontalLayout.addItem(spacerItem1)
    self.labelLineEdit = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget)
    self.labelLineEdit.setObjectName("labelLineEdit")
    self.horizontalLayout.addWidget(self.labelLineEdit)
    self.mainVerticalLayout.addLayout(self.horizontalLayout)
    self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
    self.horizontalLayout_2.setObjectName("horizontalLayout_2")
    self.structuralLevelCheckBox = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget)
    self.structuralLevelCheckBox.setObjectName("structuralLevelCheckBox")
    self.horizontalLayout_2.addWidget(self.structuralLevelCheckBox)
    self.mainVerticalLayout.addLayout(self.horizontalLayout_2)

    self.retranslateUi(CreateTypeDialog)
    self.buttonBox.accepted.connect(CreateTypeDialog.accept) # type: ignore
    self.buttonBox.rejected.connect(CreateTypeDialog.reject) # type: ignore
    QtCore.QMetaObject.connectSlotsByName(CreateTypeDialog)

  def retranslateUi(self, CreateTypeDialog):
    _translate = QtCore.QCoreApplication.translate
    CreateTypeDialog.setWindowTitle(_translate("CreateTypeDialog", "Create New Type"))
    self.titleLabel.setText(_translate("CreateTypeDialog", "Enter Type title"))
    self.titleLineEdit.setToolTip(_translate("CreateTypeDialog", "Exclude titles which start with \'x\' (reserved for structure level titles) or whitespace"))
    self.titleLineEdit.setPlaceholderText(_translate("CreateTypeDialog", "Enter title for the new type"))
    self.typeLabel.setText(_translate("CreateTypeDialog", "Enter Type Label"))
    self.labelLineEdit.setToolTip(_translate("CreateTypeDialog", "Enter label for the new type, which can also be modified later in the main editor window"))
    self.labelLineEdit.setPlaceholderText(_translate("CreateTypeDialog", "Enter label for the new type"))
    self.structuralLevelCheckBox.setToolTip(_translate("CreateTypeDialog", "If this is a structural type, then title will be automatically populated as (x0, x1...xn). Next number will be chosen for xn from the existing list of structural items."))
    self.structuralLevelCheckBox.setText(_translate("CreateTypeDialog", "Is this a structural Type?"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CreateTypeDialog = QtWidgets.QDialog()
    ui = Ui_CreateTypeDialog()
    ui.setupUi(CreateTypeDialog)
    CreateTypeDialog.show()
    sys.exit(app.exec())
