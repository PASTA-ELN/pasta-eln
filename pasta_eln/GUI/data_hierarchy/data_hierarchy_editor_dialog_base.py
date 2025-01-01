################################################################################
## Form generated from reading UI file 'data_hierarchy_editor_dialog_base.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QSpacerItem, QTableView, QWidget)


class Ui_DataHierarchyEditorDialogBase:
    def setupUi(self, DataHierarchyEditorDialogBase):
        if not DataHierarchyEditorDialogBase.objectName():
            DataHierarchyEditorDialogBase.setObjectName('DataHierarchyEditorDialogBase')
        DataHierarchyEditorDialogBase.resize(1254, 750)
        self.gridLayout = QGridLayout(DataHierarchyEditorDialogBase)
        self.gridLayout.setObjectName('gridLayout')
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.mainWidget = QWidget(DataHierarchyEditorDialogBase)
        self.mainWidget.setObjectName('mainWidget')
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainWidget.sizePolicy().hasHeightForWidth())
        self.mainWidget.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QGridLayout(self.mainWidget)
        self.gridLayout_2.setObjectName('gridLayout_2')
        self.mainGridLayout = QGridLayout()
        self.mainGridLayout.setObjectName('mainGridLayout')
        self.mainGridLayout.setContentsMargins(30, -1, 30, -1)
        self.typeMetadataTableView = QTableView(self.mainWidget)
        self.typeMetadataTableView.setObjectName('typeMetadataTableView')
        sizePolicy.setHeightForWidth(self.typeMetadataTableView.sizePolicy().hasHeightForWidth())
        self.typeMetadataTableView.setSizePolicy(sizePolicy)
        self.typeMetadataTableView.setSortingEnabled(False)
        self.typeMetadataTableView.horizontalHeader().setCascadingSectionResizes(True)
        self.typeMetadataTableView.horizontalHeader().setProperty('showSortIndicator', False)
        self.typeMetadataTableView.horizontalHeader().setStretchLastSection(False)
        self.typeMetadataTableView.verticalHeader().setCascadingSectionResizes(True)
        self.typeMetadataTableView.verticalHeader().setProperty('showSortIndicator', False)
        self.typeMetadataTableView.verticalHeader().setStretchLastSection(False)

        self.mainGridLayout.addWidget(self.typeMetadataTableView, 6, 0, 1, 1)

        self.attachmentsHeaderHorizontalLayout = QHBoxLayout()
        self.attachmentsHeaderHorizontalLayout.setObjectName('attachmentsHeaderHorizontalLayout')
        self.attachmentsHeaderHorizontalLayout.setContentsMargins(0, 5, 0, 5)
        self.attachmentsShowHidePushButton = QPushButton(self.mainWidget)
        self.attachmentsShowHidePushButton.setObjectName('attachmentsShowHidePushButton')
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.attachmentsShowHidePushButton.sizePolicy().hasHeightForWidth())
        self.attachmentsShowHidePushButton.setSizePolicy(sizePolicy1)
        self.attachmentsShowHidePushButton.setMinimumSize(QSize(200, 0))

        self.attachmentsHeaderHorizontalLayout.addWidget(self.attachmentsShowHidePushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.attachmentsHeaderHorizontalLayout.addItem(self.horizontalSpacer_2)


        self.mainGridLayout.addLayout(self.attachmentsHeaderHorizontalLayout, 10, 0, 1, 1)

        self.metadataGroupHorizontalLayout = QHBoxLayout()
        self.metadataGroupHorizontalLayout.setObjectName('metadataGroupHorizontalLayout')
        self.metadataGroupHorizontalLayout.setContentsMargins(0, 5, 0, 5)
        self.metadataGroupLabel = QLabel(self.mainWidget)
        self.metadataGroupLabel.setObjectName('metadataGroupLabel')
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.metadataGroupLabel.sizePolicy().hasHeightForWidth())
        self.metadataGroupLabel.setSizePolicy(sizePolicy2)
        self.metadataGroupLabel.setMinimumSize(QSize(130, 0))

        self.metadataGroupHorizontalLayout.addWidget(self.metadataGroupLabel)

        self.metadataGroupComboBox = QComboBox(self.mainWidget)
        self.metadataGroupComboBox.setObjectName('metadataGroupComboBox')
        self.metadataGroupComboBox.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.metadataGroupComboBox.sizePolicy().hasHeightForWidth())
        self.metadataGroupComboBox.setSizePolicy(sizePolicy3)
        self.metadataGroupComboBox.setMinimumSize(QSize(200, 0))
        self.metadataGroupComboBox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.metadataGroupHorizontalLayout.addWidget(self.metadataGroupComboBox)

        self.addMetadataGroupLineEdit = QLineEdit(self.mainWidget)
        self.addMetadataGroupLineEdit.setObjectName('addMetadataGroupLineEdit')
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.addMetadataGroupLineEdit.sizePolicy().hasHeightForWidth())
        self.addMetadataGroupLineEdit.setSizePolicy(sizePolicy4)
        self.addMetadataGroupLineEdit.setMinimumSize(QSize(0, 0))
        self.addMetadataGroupLineEdit.setClearButtonEnabled(True)

        self.metadataGroupHorizontalLayout.addWidget(self.addMetadataGroupLineEdit)

        self.addMetadataGroupPushButton = QPushButton(self.mainWidget)
        self.addMetadataGroupPushButton.setObjectName('addMetadataGroupPushButton')
        sizePolicy3.setHeightForWidth(self.addMetadataGroupPushButton.sizePolicy().hasHeightForWidth())
        self.addMetadataGroupPushButton.setSizePolicy(sizePolicy3)
        self.addMetadataGroupPushButton.setMinimumSize(QSize(200, 0))

        self.metadataGroupHorizontalLayout.addWidget(self.addMetadataGroupPushButton)

        self.deleteMetadataGroupPushButton = QPushButton(self.mainWidget)
        self.deleteMetadataGroupPushButton.setObjectName('deleteMetadataGroupPushButton')
        sizePolicy3.setHeightForWidth(self.deleteMetadataGroupPushButton.sizePolicy().hasHeightForWidth())
        self.deleteMetadataGroupPushButton.setSizePolicy(sizePolicy3)
        self.deleteMetadataGroupPushButton.setMinimumSize(QSize(200, 0))

        self.metadataGroupHorizontalLayout.addWidget(self.deleteMetadataGroupPushButton)


        self.mainGridLayout.addLayout(self.metadataGroupHorizontalLayout, 3, 0, 1, 1)

        self.datatypeHorizontalLayout = QHBoxLayout()
        self.datatypeHorizontalLayout.setObjectName('datatypeHorizontalLayout')
        self.datatypeHorizontalLayout.setContentsMargins(0, 5, 0, 5)
        self.typeLabel = QLabel(self.mainWidget)
        self.typeLabel.setObjectName('typeLabel')
        sizePolicy2.setHeightForWidth(self.typeLabel.sizePolicy().hasHeightForWidth())
        self.typeLabel.setSizePolicy(sizePolicy2)
        self.typeLabel.setMinimumSize(QSize(130, 0))

        self.datatypeHorizontalLayout.addWidget(self.typeLabel)

        self.typeComboBox = QComboBox(self.mainWidget)
        self.typeComboBox.setObjectName('typeComboBox')
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.typeComboBox.sizePolicy().hasHeightForWidth())
        self.typeComboBox.setSizePolicy(sizePolicy5)
        self.typeComboBox.setMinimumSize(QSize(400, 0))
        self.typeComboBox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.datatypeHorizontalLayout.addWidget(self.typeComboBox)

        self.addTypePushButton = QPushButton(self.mainWidget)
        self.addTypePushButton.setObjectName('addTypePushButton')
        sizePolicy3.setHeightForWidth(self.addTypePushButton.sizePolicy().hasHeightForWidth())
        self.addTypePushButton.setSizePolicy(sizePolicy3)
        self.addTypePushButton.setMinimumSize(QSize(200, 0))

        self.datatypeHorizontalLayout.addWidget(self.addTypePushButton)

        self.editTypePushButton = QPushButton(self.mainWidget)
        self.editTypePushButton.setObjectName('editTypePushButton')
        sizePolicy3.setHeightForWidth(self.editTypePushButton.sizePolicy().hasHeightForWidth())
        self.editTypePushButton.setSizePolicy(sizePolicy3)
        self.editTypePushButton.setMinimumSize(QSize(200, 0))

        self.datatypeHorizontalLayout.addWidget(self.editTypePushButton)

        self.deleteTypePushButton = QPushButton(self.mainWidget)
        self.deleteTypePushButton.setObjectName('deleteTypePushButton')
        sizePolicy3.setHeightForWidth(self.deleteTypePushButton.sizePolicy().hasHeightForWidth())
        self.deleteTypePushButton.setSizePolicy(sizePolicy3)
        self.deleteTypePushButton.setMinimumSize(QSize(200, 0))

        self.datatypeHorizontalLayout.addWidget(self.deleteTypePushButton)


        self.mainGridLayout.addLayout(self.datatypeHorizontalLayout, 1, 0, 1, 1)

        self.metadataTableButtonHorizontalLayout = QHBoxLayout()
        self.metadataTableButtonHorizontalLayout.setObjectName('metadataTableButtonHorizontalLayout')
        self.metadataTableButtonHorizontalLayout.setContentsMargins(0, 5, 0, 5)
        self.addMetadataRowPushButton = QPushButton(self.mainWidget)
        self.addMetadataRowPushButton.setObjectName('addMetadataRowPushButton')
        sizePolicy1.setHeightForWidth(self.addMetadataRowPushButton.sizePolicy().hasHeightForWidth())
        self.addMetadataRowPushButton.setSizePolicy(sizePolicy1)
        self.addMetadataRowPushButton.setMinimumSize(QSize(200, 0))

        self.metadataTableButtonHorizontalLayout.addWidget(self.addMetadataRowPushButton)

        self.metadataButtonLayoutHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.metadataTableButtonHorizontalLayout.addItem(self.metadataButtonLayoutHorizontalSpacer)


        self.mainGridLayout.addLayout(self.metadataTableButtonHorizontalLayout, 8, 0, 1, 1)

        self.attachmentTableButtonsHorizontalLayout = QHBoxLayout()
        self.attachmentTableButtonsHorizontalLayout.setObjectName('attachmentTableButtonsHorizontalLayout')
        self.attachmentTableButtonsHorizontalLayout.setContentsMargins(0, 5, 0, 5)
        self.addAttachmentPushButton = QPushButton(self.mainWidget)
        self.addAttachmentPushButton.setObjectName('addAttachmentPushButton')
        self.addAttachmentPushButton.setMinimumSize(QSize(200, 0))

        self.attachmentTableButtonsHorizontalLayout.addWidget(self.addAttachmentPushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.attachmentTableButtonsHorizontalLayout.addItem(self.horizontalSpacer)


        self.mainGridLayout.addLayout(self.attachmentTableButtonsHorizontalLayout, 13, 0, 1, 1)

        self.metadataTableHeaderHorizontalLayout = QHBoxLayout()
        self.metadataTableHeaderHorizontalLayout.setObjectName('metadataTableHeaderHorizontalLayout')
        self.metadataTableHeaderHorizontalLayout.setContentsMargins(-1, 5, -1, 5)
        self.metadataTableHeaderLabel = QLabel(self.mainWidget)
        self.metadataTableHeaderLabel.setObjectName('metadataTableHeaderLabel')
        font = QFont()
        font.setBold(True)
        self.metadataTableHeaderLabel.setFont(font)

        self.metadataTableHeaderHorizontalLayout.addWidget(self.metadataTableHeaderLabel)


        self.mainGridLayout.addLayout(self.metadataTableHeaderHorizontalLayout, 4, 0, 1, 1)

        self.typeAttachmentsTableView = QTableView(self.mainWidget)
        self.typeAttachmentsTableView.setObjectName('typeAttachmentsTableView')
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.typeAttachmentsTableView.sizePolicy().hasHeightForWidth())
        self.typeAttachmentsTableView.setSizePolicy(sizePolicy6)
        self.typeAttachmentsTableView.horizontalHeader().setStretchLastSection(False)

        self.mainGridLayout.addWidget(self.typeAttachmentsTableView, 12, 0, 1, 1)

        self.headerHorizontalLayout = QHBoxLayout()
        self.headerHorizontalLayout.setObjectName('headerHorizontalLayout')
        self.headerHorizontalLayout.setContentsMargins(0, 20, 0, 20)
        self.headerLabel = QLabel(self.mainWidget)
        self.headerLabel.setObjectName('headerLabel')
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        self.headerLabel.setFont(font1)
        self.headerLabel.setMargin(0)

        self.headerHorizontalLayout.addWidget(self.headerLabel)

        self.headerHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.headerHorizontalLayout.addItem(self.headerHorizontalSpacer)

        self.saveDataHierarchyPushButton = QPushButton(self.mainWidget)
        self.saveDataHierarchyPushButton.setObjectName('saveDataHierarchyPushButton')

        self.headerHorizontalLayout.addWidget(self.saveDataHierarchyPushButton)

        self.helpPushButton = QPushButton(self.mainWidget)
        self.helpPushButton.setObjectName('helpPushButton')

        self.headerHorizontalLayout.addWidget(self.helpPushButton)

        self.cancelPushButton = QPushButton(self.mainWidget)
        self.cancelPushButton.setObjectName('cancelPushButton')

        self.headerHorizontalLayout.addWidget(self.cancelPushButton)


        self.mainGridLayout.addLayout(self.headerHorizontalLayout, 0, 0, 1, 1)


        self.gridLayout_2.addLayout(self.mainGridLayout, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.mainWidget, 0, 1, 1, 1)


        self.retranslateUi(DataHierarchyEditorDialogBase)

        QMetaObject.connectSlotsByName(DataHierarchyEditorDialogBase)
    # setupUi

    def retranslateUi(self, DataHierarchyEditorDialogBase):
        DataHierarchyEditorDialogBase.setWindowTitle(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Data Hierarchy Editor', None))
#if QT_CONFIG(tooltip)
        DataHierarchyEditorDialogBase.setToolTip('')
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.typeMetadataTableView.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', "Table for all metadata associated with the Data Type. Add \"comment\" or \"content\" for editable text fields, \"image\" for image support, or enter another Data Type to enable links.", None))
#endif // QT_CONFIG(tooltip)
        self.attachmentsShowHidePushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Show/Hide Attachments', None))
        self.metadataGroupLabel.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Metadata Group', None))
#if QT_CONFIG(tooltip)
        self.metadataGroupComboBox.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Select the group of metadata to be listed below in the table', None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.addMetadataGroupLineEdit.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Enter the new group to be added to the data type', None))
#endif // QT_CONFIG(tooltip)
        self.addMetadataGroupLineEdit.setPlaceholderText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Enter the new group to be added', None))
#if QT_CONFIG(tooltip)
        self.addMetadataGroupPushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Add a new group of metadata to the data type, table below will be reset to empty list!', None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.addMetadataGroupPushButton.setStatusTip('')
#endif // QT_CONFIG(statustip)
        self.addMetadataGroupPushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', '+ Add', None))
#if QT_CONFIG(tooltip)
        self.deleteMetadataGroupPushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Delete the selected group in the group combobox', None))
#endif // QT_CONFIG(tooltip)
        self.deleteMetadataGroupPushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', '- Delete', None))
        self.typeLabel.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Data Type', None))
#if QT_CONFIG(tooltip)
        self.typeComboBox.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Select the type from the loaded data hierarchy types', None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.addTypePushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Add a new type (structural or normal type) to the data hierarchy data set.', None))
#endif // QT_CONFIG(tooltip)
        self.addTypePushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', '+ Add', None))
        self.editTypePushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', '* Edit', None))
#if QT_CONFIG(tooltip)
        self.deleteTypePushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Delete the type with the full metadata and attachments completely', None))
#endif // QT_CONFIG(tooltip)
        self.deleteTypePushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', '- Delete', None))
#if QT_CONFIG(tooltip)
        self.addMetadataRowPushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Add a new metadata row to the above table with empty values', None))
#endif // QT_CONFIG(tooltip)
        self.addMetadataRowPushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', '+ Add Metadata', None))
#if QT_CONFIG(tooltip)
        self.addAttachmentPushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Add a new attachment row to the above table with empty values', None))
#endif // QT_CONFIG(tooltip)
        self.addAttachmentPushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', '+ Add Attachment', None))
        self.metadataTableHeaderLabel.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Metadata', None))
#if QT_CONFIG(tooltip)
        self.typeAttachmentsTableView.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Table which displays the attachments for the above selected data type', None))
#endif // QT_CONFIG(tooltip)
        self.headerLabel.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Edit the data hierarchy for the PASTA-ELN projects', None))
#if QT_CONFIG(tooltip)
        self.saveDataHierarchyPushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Save loaded data hierarchy in local database', None))
#endif // QT_CONFIG(tooltip)
        self.saveDataHierarchyPushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Save', None))
#if QT_CONFIG(tooltip)
        self.helpPushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Navigate to the help page', None))
#endif // QT_CONFIG(tooltip)
        self.helpPushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Help', None))
#if QT_CONFIG(tooltip)
        self.cancelPushButton.setToolTip(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Close the editor', None))
#endif // QT_CONFIG(tooltip)
        self.cancelPushButton.setText(QCoreApplication.translate('DataHierarchyEditorDialogBase', 'Cancel', None))
    # retranslateUi
