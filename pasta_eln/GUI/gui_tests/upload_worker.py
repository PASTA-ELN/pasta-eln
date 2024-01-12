#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_worker.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import time

from PySide6.QtCore import QObject, Signal


class UploadWorker(QObject):
    progressChanged = Signal(int)
    statusChanged = Signal(str)
    finished = Signal()
    def __init__(self):
        super().__init__()
    def work(self):
        self.progressChanged.emit(0)
        self.statusChanged.emit("Queued...")
        self.statusChanged.emit("Uploading...")
        for progressbar_value in range(101):
            self.progressChanged.emit(progressbar_value)
            time.sleep(0.07)
        self.finished.emit()
        self.statusChanged.emit("Finished...")
        
    
