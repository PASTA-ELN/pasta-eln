#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_task.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import random
import time

from PySide6.QtCore import QObject, Signal

from pasta_eln.GUI.dataverse_ui.dataverse_upload_widget_base import Ui_UploadWidgetFrame


class UploadTask(QObject):
    progressChanged = Signal(int)
    statusChanged = Signal(str)
    finished = Signal()
    start = Signal()
    def __init__(self, widget: Ui_UploadWidgetFrame):
        super().__init__()
        self.cancelled = False
        self.progressChanged.connect(widget.uploadProgressBar.setValue)
        self.statusChanged.connect(widget.statusPushButton.setText)
        self.start.connect(self.do_upload)
        widget.uploadCancelPushButton.clicked.connect(lambda: self.cancel_upload())

    def cancel_upload(self):
        self.cancelled = True
    def do_upload(self):
        self.cancelled = False
        self.progressChanged.emit(0)
        self.statusChanged.emit("Queued...")
        self.statusChanged.emit("Uploading...")
        for progressbar_value in range(101):
            self.progressChanged.emit(progressbar_value)
            if self.cancelled:
                break
            time.sleep(random.uniform(0.1, 0.6))
        self.finished.emit()
        self.statusChanged.emit("Cancelled..." if self.cancelled else "Finished...")

