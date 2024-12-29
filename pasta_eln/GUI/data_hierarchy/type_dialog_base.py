# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'type_dialog_base.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_TypeDialogBase(object):
    def setupUi(self, TypeDialogBase):
        if not TypeDialogBase.objectName():
            TypeDialogBase.setObjectName(u'TypeDialogBase')
        TypeDialogBase.resize(733, 351)
        self.gridLayout = QGridLayout(TypeDialogBase)
        self.gridLayout.setObjectName(u'gridLayout')
        self.mainVerticalLayout = QVBoxLayout()
        self.mainVerticalLayout.setObjectName(u'mainVerticalLayout')
        self.mainVerticalLayout.setContentsMargins(20, -1, 20, -1)
        self.tileHorizontalLayout = QHBoxLayout()
        self.tileHorizontalLayout.setObjectName(u'tileHorizontalLayout')
        self.typeLabel = QLabel(TypeDialogBase)
        self.typeLabel.setObjectName(u'typeLabel')
        self.typeLabel.setMinimumSize(QSize(120, 0))

        self.tileHorizontalLayout.addWidget(self.typeLabel)

        self.titleHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.tileHorizontalLayout.addItem(self.titleHorizontalSpacer)

        self.typeLineEdit = QLineEdit(TypeDialogBase)
        self.typeLineEdit.setObjectName(u'typeLineEdit')
        self.typeLineEdit.setClearButtonEnabled(True)

        self.tileHorizontalLayout.addWidget(self.typeLineEdit)


        self.mainVerticalLayout.addLayout(self.tileHorizontalLayout)

        self.verticalSpacer1 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainVerticalLayout.addItem(self.verticalSpacer1)

        self.displayedTitleHorizontalLayout = QHBoxLayout()
        self.displayedTitleHorizontalLayout.setObjectName(u'displayedTitleHorizontalLayout')
        self.typeDisplayedTitleLabel = QLabel(TypeDialogBase)
        self.typeDisplayedTitleLabel.setObjectName(u'typeDisplayedTitleLabel')
        self.typeDisplayedTitleLabel.setMinimumSize(QSize(120, 0))

        self.displayedTitleHorizontalLayout.addWidget(self.typeDisplayedTitleLabel)

        self.displayedTitleHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.displayedTitleHorizontalLayout.addItem(self.displayedTitleHorizontalSpacer)

        self.typeDisplayedTitleLineEdit = QLineEdit(TypeDialogBase)
        self.typeDisplayedTitleLineEdit.setObjectName(u'typeDisplayedTitleLineEdit')
        self.typeDisplayedTitleLineEdit.setClearButtonEnabled(True)

        self.displayedTitleHorizontalLayout.addWidget(self.typeDisplayedTitleLineEdit)


        self.mainVerticalLayout.addLayout(self.displayedTitleHorizontalLayout)

        self.verticalSpacer2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainVerticalLayout.addItem(self.verticalSpacer2)

        self.iriHorizontalLayout = QHBoxLayout()
        self.iriHorizontalLayout.setObjectName(u'iriHorizontalLayout')
        self.iriLabel = QLabel(TypeDialogBase)
        self.iriLabel.setObjectName(u'iriLabel')
        self.iriLabel.setMinimumSize(QSize(120, 0))

        self.iriHorizontalLayout.addWidget(self.iriLabel)

        self.iriHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.iriHorizontalLayout.addItem(self.iriHorizontalSpacer)

        self.iriLineEdit = QLineEdit(TypeDialogBase)
        self.iriLineEdit.setObjectName(u'iriLineEdit')

        self.iriHorizontalLayout.addWidget(self.iriLineEdit)


        self.mainVerticalLayout.addLayout(self.iriHorizontalLayout)

        self.verticalSpacer3 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainVerticalLayout.addItem(self.verticalSpacer3)

        self.shortcutHorizontalLayout = QHBoxLayout()
        self.shortcutHorizontalLayout.setObjectName(u'shortcutHorizontalLayout')
        self.shortcutLabel = QLabel(TypeDialogBase)
        self.shortcutLabel.setObjectName(u'shortcutLabel')
        self.shortcutLabel.setMinimumSize(QSize(120, 0))

        self.shortcutHorizontalLayout.addWidget(self.shortcutLabel)

        self.shortcutHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.shortcutHorizontalLayout.addItem(self.shortcutHorizontalSpacer)

        self.shortcutLineEdit = QLineEdit(TypeDialogBase)
        self.shortcutLineEdit.setObjectName(u'shortcutLineEdit')

        self.shortcutHorizontalLayout.addWidget(self.shortcutLineEdit)


        self.mainVerticalLayout.addLayout(self.shortcutHorizontalLayout)

        self.verticalSpacer4 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainVerticalLayout.addItem(self.verticalSpacer4)

        self.iconHorizontalLayout = QHBoxLayout()
        self.iconHorizontalLayout.setObjectName(u'iconHorizontalLayout')
        self.iconLabel = QLabel(TypeDialogBase)
        self.iconLabel.setObjectName(u'iconLabel')
        self.iconLabel.setMinimumSize(QSize(120, 0))

        self.iconHorizontalLayout.addWidget(self.iconLabel)

        self.iconHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.iconHorizontalLayout.addItem(self.iconHorizontalSpacer)

        self.iconFontCollectionComboBox = QComboBox(TypeDialogBase)
        self.iconFontCollectionComboBox.setObjectName(u'iconFontCollectionComboBox')
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.iconFontCollectionComboBox.sizePolicy().hasHeightForWidth())
        self.iconFontCollectionComboBox.setSizePolicy(sizePolicy)
        self.iconFontCollectionComboBox.setMinimumSize(QSize(100, 0))

        self.iconHorizontalLayout.addWidget(self.iconFontCollectionComboBox)

        self.iconComboBox = QComboBox(TypeDialogBase)
        self.iconComboBox.setObjectName(u'iconComboBox')
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.iconComboBox.sizePolicy().hasHeightForWidth())
        self.iconComboBox.setSizePolicy(sizePolicy1)
        self.iconComboBox.setEditable(True)
        self.iconComboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.iconHorizontalLayout.addWidget(self.iconComboBox)


        self.mainVerticalLayout.addLayout(self.iconHorizontalLayout)

        self.verticalSpacer5 = QSpacerItem(20, 90, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mainVerticalLayout.addItem(self.verticalSpacer5)

        self.mainVerticalLayout.setStretch(0, 1)
        self.mainVerticalLayout.setStretch(1, 1)
        self.mainVerticalLayout.setStretch(2, 1)
        self.mainVerticalLayout.setStretch(3, 1)
        self.mainVerticalLayout.setStretch(4, 1)
        self.mainVerticalLayout.setStretch(5, 1)
        self.mainVerticalLayout.setStretch(6, 1)
        self.mainVerticalLayout.setStretch(7, 1)
        self.mainVerticalLayout.setStretch(8, 1)

        self.gridLayout.addLayout(self.mainVerticalLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(TypeDialogBase)
        self.buttonBox.setObjectName(u'buttonBox')
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi(TypeDialogBase)
        self.buttonBox.accepted.connect(TypeDialogBase.accept)
        self.buttonBox.rejected.connect(TypeDialogBase.reject)

        QMetaObject.connectSlotsByName(TypeDialogBase)
    # setupUi

    def retranslateUi(self, TypeDialogBase):
        TypeDialogBase.setWindowTitle(QCoreApplication.translate('TypeDialogBase', u'data type', None))
        self.typeLabel.setText(QCoreApplication.translate('TypeDialogBase', u'Data type', None))
#if QT_CONFIG(tooltip)
        self.typeLineEdit.setToolTip(QCoreApplication.translate('TypeDialogBase', u'Enter the new type title, exclude title which contains whitespace.', None))
#endif // QT_CONFIG(tooltip)
        self.typeLineEdit.setPlaceholderText(QCoreApplication.translate('TypeDialogBase', u'Enter the data type', None))
        self.typeDisplayedTitleLabel.setText(QCoreApplication.translate('TypeDialogBase', u'Title', None))
#if QT_CONFIG(tooltip)
        self.typeDisplayedTitleLineEdit.setToolTip(QCoreApplication.translate('TypeDialogBase', u'Enter the displayed title property of the type', None))
#endif // QT_CONFIG(tooltip)
        self.typeDisplayedTitleLineEdit.setPlaceholderText(QCoreApplication.translate('TypeDialogBase', u'Enter the displayed title', None))
        self.iriLabel.setText(QCoreApplication.translate('TypeDialogBase', u'IRI', None))
#if QT_CONFIG(tooltip)
        self.iriLineEdit.setToolTip(QCoreApplication.translate('TypeDialogBase', u'Enter the Internationalized Resource Identifier for the type', None))
#endif // QT_CONFIG(tooltip)
        self.iriLineEdit.setPlaceholderText(QCoreApplication.translate('TypeDialogBase', u'Enter the IRI', None))
        self.shortcutLabel.setText(QCoreApplication.translate('TypeDialogBase', u'Shortcut', None))
#if QT_CONFIG(tooltip)
        self.shortcutLineEdit.setToolTip(QCoreApplication.translate('TypeDialogBase', u'Enter the shortcut key combination for the type', None))
#endif // QT_CONFIG(tooltip)
        self.shortcutLineEdit.setPlaceholderText(QCoreApplication.translate('TypeDialogBase', u'Enter the shortcut key combination', None))
        self.iconLabel.setText(QCoreApplication.translate('TypeDialogBase', u'Icon', None))
#if QT_CONFIG(tooltip)
        self.iconFontCollectionComboBox.setToolTip(QCoreApplication.translate('TypeDialogBase', u'Select the icon font collection for this type', None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.iconComboBox.setToolTip(QCoreApplication.translate('TypeDialogBase', u'Select the icon used for this type', None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi
