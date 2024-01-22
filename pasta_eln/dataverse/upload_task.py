#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_task_thread.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import random
import time

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QLabel

from pasta_eln.GUI.dataverse_ui.dataverse_upload_widget_base import Ui_UploadWidgetFrame
from pasta_eln.dataverse.generic_task_object import GenericTaskObject

import qtawesome as qta



class UploadGenericTask(GenericTaskObject):
    progressChanged = Signal(int)
    statusChanged = Signal(str)
    def __init__(self, widget: Ui_UploadWidgetFrame):
        super().__init__()
        self.progressChanged.connect(widget.uploadProgressBar.setValue)
        self.statusChanged.connect(lambda status:  self.update_status(status, widget.statusIconLabel, widget.statusLabel))
        widget.uploadCancelPushButton.clicked.connect(lambda: self.cancel.emit())

    def start_task(self):
        super().start_task()
        self.progressChanged.emit(0)
        self.statusChanged.emit("Queued")
        self.statusChanged.emit("Uploading")
        for progressbar_value in range(101):
            self.progressChanged.emit(progressbar_value)
            if self.cancelled:
                break
            time.sleep(random.uniform(0.01, 0.06))
        self.finished.emit()
        self.statusChanged.emit("Cancelled" if self.cancelled else "Finished")

    def cancel_task(self):
        super().cancel_task()
        self.statusChanged.emit("Cancelled")

    def update_status(self,
                      status,
                      statusIconLabel: QLabel,
                      statusLabel: QLabel):
        statusLabel.setText(status)
        match status:
            case "Queued":
                statusIconLabel.setPixmap(qta.icon('ph.queue-bold').pixmap(statusIconLabel.size()))
            case "Uploading":
                statusIconLabel.setPixmap(qta.icon('mdi6.progress-upload').pixmap(statusIconLabel.size()))
            case "Cancelled":
                statusIconLabel.setPixmap(qta.icon('mdi.cancel').pixmap(statusIconLabel.size()))
            case "Finished":
                statusIconLabel.setPixmap(qta.icon('fa.check-circle-o').pixmap(statusIconLabel.size()))
            case "Error":
                statusIconLabel.setPixmap(qta.icon('msc.error-small').pixmap(statusIconLabel.size()))
            case "Warning":
                statusIconLabel.setPixmap(qta.icon('fa.warning').pixmap(statusIconLabel.size()))


