# Form implementation generated from reading ui file 'ontology_configuration.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide6 import QtCore, QtGui, QtWidgets


class Ui_OntologyConfigurationBaseForm(object):
  def setupUi(self, OntologyConfigurationBaseForm):
    OntologyConfigurationBaseForm.setObjectName("OntologyConfigurationBaseForm")
    OntologyConfigurationBaseForm.resize(1271, 845)
    OntologyConfigurationBaseForm.setToolTip("")
    self.gridLayout = QtWidgets.QGridLayout(OntologyConfigurationBaseForm)
    self.gridLayout.setContentsMargins(10, 10, 10, 10)
    self.gridLayout.setObjectName("gridLayout")
    self.mainWidget = QtWidgets.QWidget(parent=OntologyConfigurationBaseForm)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.mainWidget.sizePolicy().hasHeightForWidth())
    self.mainWidget.setSizePolicy(sizePolicy)
    self.mainWidget.setObjectName("mainWidget")
    self.gridLayout_2 = QtWidgets.QGridLayout(self.mainWidget)
    self.gridLayout_2.setObjectName("gridLayout_2")
    self.mainGridLayout = QtWidgets.QGridLayout()
    self.mainGridLayout.setContentsMargins(30, -1, 30, -1)
    self.mainGridLayout.setObjectName("mainGridLayout")
    self.typeMetadataTableView = QtWidgets.QTableView(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.typeMetadataTableView.sizePolicy().hasHeightForWidth())
    self.typeMetadataTableView.setSizePolicy(sizePolicy)
    self.typeMetadataTableView.setSortingEnabled(False)
    self.typeMetadataTableView.setObjectName("typeMetadataTableView")
    self.typeMetadataTableView.horizontalHeader().setCascadingSectionResizes(True)
    self.typeMetadataTableView.horizontalHeader().setSortIndicatorShown(False)
    self.typeMetadataTableView.horizontalHeader().setStretchLastSection(False)
    self.typeMetadataTableView.verticalHeader().setCascadingSectionResizes(True)
    self.typeMetadataTableView.verticalHeader().setSortIndicatorShown(False)
    self.typeMetadataTableView.verticalHeader().setStretchLastSection(False)
    self.mainGridLayout.addWidget(self.typeMetadataTableView, 6, 0, 1, 1)
    self.attachmentsHeaderHorizontalLayout = QtWidgets.QHBoxLayout()
    self.attachmentsHeaderHorizontalLayout.setContentsMargins(0, 5, 0, 5)
    self.attachmentsHeaderHorizontalLayout.setObjectName("attachmentsHeaderHorizontalLayout")
    self.attachmentsShowHidePushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.attachmentsShowHidePushButton.sizePolicy().hasHeightForWidth())
    self.attachmentsShowHidePushButton.setSizePolicy(sizePolicy)
    self.attachmentsShowHidePushButton.setMinimumSize(QtCore.QSize(200, 0))
    self.attachmentsShowHidePushButton.setObjectName("attachmentsShowHidePushButton")
    self.attachmentsHeaderHorizontalLayout.addWidget(self.attachmentsShowHidePushButton)
    spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    self.attachmentsHeaderHorizontalLayout.addItem(spacerItem)
    self.mainGridLayout.addLayout(self.attachmentsHeaderHorizontalLayout, 10, 0, 1, 1)
    self.metadataGroupHorizontalLayout = QtWidgets.QHBoxLayout()
    self.metadataGroupHorizontalLayout.setContentsMargins(0, 5, 0, 5)
    self.metadataGroupHorizontalLayout.setObjectName("metadataGroupHorizontalLayout")
    self.metadataGroupLabel = QtWidgets.QLabel(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.metadataGroupLabel.sizePolicy().hasHeightForWidth())
    self.metadataGroupLabel.setSizePolicy(sizePolicy)
    self.metadataGroupLabel.setMinimumSize(QtCore.QSize(130, 0))
    self.metadataGroupLabel.setObjectName("metadataGroupLabel")
    self.metadataGroupHorizontalLayout.addWidget(self.metadataGroupLabel)
    self.metadataGroupComboBox = QtWidgets.QComboBox(parent=self.mainWidget)
    self.metadataGroupComboBox.setEnabled(True)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.metadataGroupComboBox.sizePolicy().hasHeightForWidth())
    self.metadataGroupComboBox.setSizePolicy(sizePolicy)
    self.metadataGroupComboBox.setMinimumSize(QtCore.QSize(200, 0))
    self.metadataGroupComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
    self.metadataGroupComboBox.setObjectName("metadataGroupComboBox")
    self.metadataGroupHorizontalLayout.addWidget(self.metadataGroupComboBox)
    self.addMetadataGroupLineEdit = QtWidgets.QLineEdit(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addMetadataGroupLineEdit.sizePolicy().hasHeightForWidth())
    self.addMetadataGroupLineEdit.setSizePolicy(sizePolicy)
    self.addMetadataGroupLineEdit.setMinimumSize(QtCore.QSize(0, 0))
    self.addMetadataGroupLineEdit.setClearButtonEnabled(True)
    self.addMetadataGroupLineEdit.setObjectName("addMetadataGroupLineEdit")
    self.metadataGroupHorizontalLayout.addWidget(self.addMetadataGroupLineEdit)
    self.addMetadataGroupPushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addMetadataGroupPushButton.sizePolicy().hasHeightForWidth())
    self.addMetadataGroupPushButton.setSizePolicy(sizePolicy)
    self.addMetadataGroupPushButton.setMinimumSize(QtCore.QSize(200, 0))
    self.addMetadataGroupPushButton.setStatusTip("")
    self.addMetadataGroupPushButton.setObjectName("addMetadataGroupPushButton")
    self.metadataGroupHorizontalLayout.addWidget(self.addMetadataGroupPushButton)
    self.deleteMetadataGroupPushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.deleteMetadataGroupPushButton.sizePolicy().hasHeightForWidth())
    self.deleteMetadataGroupPushButton.setSizePolicy(sizePolicy)
    self.deleteMetadataGroupPushButton.setMinimumSize(QtCore.QSize(200, 0))
    self.deleteMetadataGroupPushButton.setObjectName("deleteMetadataGroupPushButton")
    self.metadataGroupHorizontalLayout.addWidget(self.deleteMetadataGroupPushButton)
    self.mainGridLayout.addLayout(self.metadataGroupHorizontalLayout, 3, 0, 1, 1)
    self.datatypeHorizontalLayout = QtWidgets.QHBoxLayout()
    self.datatypeHorizontalLayout.setContentsMargins(0, 5, 0, 5)
    self.datatypeHorizontalLayout.setObjectName("datatypeHorizontalLayout")
    self.typeLabel = QtWidgets.QLabel(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.typeLabel.sizePolicy().hasHeightForWidth())
    self.typeLabel.setSizePolicy(sizePolicy)
    self.typeLabel.setMinimumSize(QtCore.QSize(130, 0))
    self.typeLabel.setObjectName("typeLabel")
    self.datatypeHorizontalLayout.addWidget(self.typeLabel)
    self.typeComboBox = QtWidgets.QComboBox(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.typeComboBox.sizePolicy().hasHeightForWidth())
    self.typeComboBox.setSizePolicy(sizePolicy)
    self.typeComboBox.setMinimumSize(QtCore.QSize(200, 0))
    self.typeComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
    self.typeComboBox.setObjectName("typeComboBox")
    self.datatypeHorizontalLayout.addWidget(self.typeComboBox)
    self.typeDisplayedTitleLineEdit = QtWidgets.QLineEdit(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.typeDisplayedTitleLineEdit.sizePolicy().hasHeightForWidth())
    self.typeDisplayedTitleLineEdit.setSizePolicy(sizePolicy)
    self.typeDisplayedTitleLineEdit.setMinimumSize(QtCore.QSize(0, 0))
    self.typeDisplayedTitleLineEdit.setText("")
    self.typeDisplayedTitleLineEdit.setClearButtonEnabled(True)
    self.typeDisplayedTitleLineEdit.setObjectName("typeDisplayedTitleLineEdit")
    self.datatypeHorizontalLayout.addWidget(self.typeDisplayedTitleLineEdit)
    self.typeIriLineEdit = QtWidgets.QLineEdit(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.typeIriLineEdit.sizePolicy().hasHeightForWidth())
    self.typeIriLineEdit.setSizePolicy(sizePolicy)
    self.typeIriLineEdit.setClearButtonEnabled(True)
    self.typeIriLineEdit.setObjectName("typeIriLineEdit")
    self.datatypeHorizontalLayout.addWidget(self.typeIriLineEdit)
    self.addTypePushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addTypePushButton.sizePolicy().hasHeightForWidth())
    self.addTypePushButton.setSizePolicy(sizePolicy)
    self.addTypePushButton.setMinimumSize(QtCore.QSize(200, 0))
    self.addTypePushButton.setObjectName("addTypePushButton")
    self.datatypeHorizontalLayout.addWidget(self.addTypePushButton)
    self.deleteTypePushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.deleteTypePushButton.sizePolicy().hasHeightForWidth())
    self.deleteTypePushButton.setSizePolicy(sizePolicy)
    self.deleteTypePushButton.setMinimumSize(QtCore.QSize(200, 0))
    self.deleteTypePushButton.setObjectName("deleteTypePushButton")
    self.datatypeHorizontalLayout.addWidget(self.deleteTypePushButton)
    self.mainGridLayout.addLayout(self.datatypeHorizontalLayout, 1, 0, 1, 1)
    self.metadataTableButtonHorizontalLayout = QtWidgets.QHBoxLayout()
    self.metadataTableButtonHorizontalLayout.setContentsMargins(0, 5, 0, 5)
    self.metadataTableButtonHorizontalLayout.setObjectName("metadataTableButtonHorizontalLayout")
    self.addMetadataRowPushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.addMetadataRowPushButton.sizePolicy().hasHeightForWidth())
    self.addMetadataRowPushButton.setSizePolicy(sizePolicy)
    self.addMetadataRowPushButton.setMinimumSize(QtCore.QSize(200, 0))
    self.addMetadataRowPushButton.setObjectName("addMetadataRowPushButton")
    self.metadataTableButtonHorizontalLayout.addWidget(self.addMetadataRowPushButton)
    spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    self.metadataTableButtonHorizontalLayout.addItem(spacerItem1)
    self.mainGridLayout.addLayout(self.metadataTableButtonHorizontalLayout, 8, 0, 1, 1)
    self.attachmentTableButtonsHorizontalLayout = QtWidgets.QHBoxLayout()
    self.attachmentTableButtonsHorizontalLayout.setContentsMargins(0, 5, 0, 5)
    self.attachmentTableButtonsHorizontalLayout.setObjectName("attachmentTableButtonsHorizontalLayout")
    self.addAttachmentPushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    self.addAttachmentPushButton.setMinimumSize(QtCore.QSize(200, 0))
    self.addAttachmentPushButton.setObjectName("addAttachmentPushButton")
    self.attachmentTableButtonsHorizontalLayout.addWidget(self.addAttachmentPushButton)
    spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    self.attachmentTableButtonsHorizontalLayout.addItem(spacerItem2)
    self.mainGridLayout.addLayout(self.attachmentTableButtonsHorizontalLayout, 13, 0, 1, 1)
    self.metadataTableHeaderHorizontalLayout = QtWidgets.QHBoxLayout()
    self.metadataTableHeaderHorizontalLayout.setContentsMargins(-1, 5, -1, 5)
    self.metadataTableHeaderHorizontalLayout.setObjectName("metadataTableHeaderHorizontalLayout")
    self.metadataTableHeaderLabel = QtWidgets.QLabel(parent=self.mainWidget)
    font = QtGui.QFont()
    font.setBold(True)
    self.metadataTableHeaderLabel.setFont(font)
    self.metadataTableHeaderLabel.setObjectName("metadataTableHeaderLabel")
    self.metadataTableHeaderHorizontalLayout.addWidget(self.metadataTableHeaderLabel)
    self.mainGridLayout.addLayout(self.metadataTableHeaderHorizontalLayout, 4, 0, 1, 1)
    self.typeAttachmentsTableView = QtWidgets.QTableView(parent=self.mainWidget)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.typeAttachmentsTableView.sizePolicy().hasHeightForWidth())
    self.typeAttachmentsTableView.setSizePolicy(sizePolicy)
    self.typeAttachmentsTableView.setObjectName("typeAttachmentsTableView")
    self.typeAttachmentsTableView.horizontalHeader().setStretchLastSection(False)
    self.mainGridLayout.addWidget(self.typeAttachmentsTableView, 12, 0, 1, 1)
    self.headerHorizontalLayout = QtWidgets.QHBoxLayout()
    self.headerHorizontalLayout.setContentsMargins(0, 20, 0, 20)
    self.headerHorizontalLayout.setObjectName("headerHorizontalLayout")
    self.headerLabel = QtWidgets.QLabel(parent=self.mainWidget)
    font = QtGui.QFont()
    font.setPointSize(14)
    font.setBold(True)
    self.headerLabel.setFont(font)
    self.headerLabel.setObjectName("headerLabel")
    self.headerHorizontalLayout.addWidget(self.headerLabel)
    spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
    self.headerHorizontalLayout.addItem(spacerItem3)
    self.saveOntologyPushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    self.saveOntologyPushButton.setObjectName("saveOntologyPushButton")
    self.headerHorizontalLayout.addWidget(self.saveOntologyPushButton)
    self.helpPushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    self.helpPushButton.setObjectName("helpPushButton")
    self.headerHorizontalLayout.addWidget(self.helpPushButton)
    self.cancelPushButton = QtWidgets.QPushButton(parent=self.mainWidget)
    self.cancelPushButton.setObjectName("cancelPushButton")
    self.headerHorizontalLayout.addWidget(self.cancelPushButton)
    self.mainGridLayout.addLayout(self.headerHorizontalLayout, 0, 0, 1, 1)
    self.gridLayout_2.addLayout(self.mainGridLayout, 0, 0, 1, 1)
    self.gridLayout.addWidget(self.mainWidget, 0, 1, 1, 1)

    self.retranslateUi(OntologyConfigurationBaseForm)
    QtCore.QMetaObject.connectSlotsByName(OntologyConfigurationBaseForm)

  def retranslateUi(self, OntologyConfigurationBaseForm):
    _translate = QtCore.QCoreApplication.translate
    OntologyConfigurationBaseForm.setWindowTitle(_translate("OntologyConfigurationBaseForm", "Data Hierarchy Editor"))
    self.typeMetadataTableView.setToolTip(_translate("OntologyConfigurationBaseForm", "Table which lists and allows editing of all the metadata associated with the above selected type"))
    self.attachmentsShowHidePushButton.setText(_translate("OntologyConfigurationBaseForm", "Show/Hide Attachments"))
    self.metadataGroupLabel.setText(_translate("OntologyConfigurationBaseForm", "Metadata Group"))
    self.metadataGroupComboBox.setToolTip(_translate("OntologyConfigurationBaseForm", "Select the group of metadata to be listed below in the table"))
    self.addMetadataGroupLineEdit.setToolTip(_translate("OntologyConfigurationBaseForm", "Enter the new group to be added to the data type"))
    self.addMetadataGroupLineEdit.setPlaceholderText(_translate("OntologyConfigurationBaseForm", "Enter the new group to be added"))
    self.addMetadataGroupPushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Add a new group of metadata to the data type, table below will be reset to empty list!"))
    self.addMetadataGroupPushButton.setText(_translate("OntologyConfigurationBaseForm", "+ Add"))
    self.deleteMetadataGroupPushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Delete the selected group in the group combobox"))
    self.deleteMetadataGroupPushButton.setText(_translate("OntologyConfigurationBaseForm", "- Delete"))
    self.typeLabel.setText(_translate("OntologyConfigurationBaseForm", "Data Type"))
    self.typeComboBox.setToolTip(_translate("OntologyConfigurationBaseForm", "Select the type from the loaded ontology"))
    self.typeDisplayedTitleLineEdit.setToolTip(_translate("OntologyConfigurationBaseForm", "Modify the displayed title property of the type"))
    self.typeDisplayedTitleLineEdit.setPlaceholderText(_translate("OntologyConfigurationBaseForm", "Modify the type displayed title here"))
    self.typeIriLineEdit.setToolTip(_translate("OntologyConfigurationBaseForm", "Enter the link/iri to be associated with this data-type"))
    self.typeIriLineEdit.setPlaceholderText(_translate("OntologyConfigurationBaseForm", "Enter the IRI for the type"))
    self.addTypePushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Add a new type (structural or normal type) to the ontology data set."))
    self.addTypePushButton.setText(_translate("OntologyConfigurationBaseForm", "+ Add"))
    self.deleteTypePushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Delete the type with the full metadata and attachments completely"))
    self.deleteTypePushButton.setText(_translate("OntologyConfigurationBaseForm", "- Delete"))
    self.addMetadataRowPushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Add a new metadata row to the above table with empty values"))
    self.addMetadataRowPushButton.setText(_translate("OntologyConfigurationBaseForm", "+ Add Metadata group"))
    self.addAttachmentPushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Add a new attachment row to the above table with empty values"))
    self.addAttachmentPushButton.setText(_translate("OntologyConfigurationBaseForm", "+ Add Attachment"))
    self.metadataTableHeaderLabel.setText(_translate("OntologyConfigurationBaseForm", "Metadata Form Editor"))
    self.typeAttachmentsTableView.setToolTip(_translate("OntologyConfigurationBaseForm", "Table which displays the attachments for the above selected data type"))
    self.headerLabel.setText(_translate("OntologyConfigurationBaseForm", "Edit the data hierarchy for the PASTA-ELN projects"))
    self.saveOntologyPushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Save loaded ontology in local database"))
    self.saveOntologyPushButton.setText(_translate("OntologyConfigurationBaseForm", "Save"))
    self.helpPushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Navigate to the help page"))
    self.helpPushButton.setText(_translate("OntologyConfigurationBaseForm", "Help"))
    self.cancelPushButton.setToolTip(_translate("OntologyConfigurationBaseForm", "Close the editor"))
    self.cancelPushButton.setText(_translate("OntologyConfigurationBaseForm", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    OntologyConfigurationBaseForm = QtWidgets.QWidget()
    ui = Ui_OntologyConfigurationBaseForm()
    ui.setupUi(OntologyConfigurationBaseForm)
    OntologyConfigurationBaseForm.show()
    sys.exit(app.exec())
