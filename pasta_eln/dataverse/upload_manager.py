#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_manager.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import time

from PySide6.QtCore import QObject, QThread, Signal

from pasta_eln.dataverse.upload_task import UploadTask


class UploadManager(QObject):
    start = Signal()
    cancel = Signal()
    def __init__(self):
        super().__init__()
        self.upload_queue: list[dict[str, UploadTask | QThread]] = []
        self.start.connect(self.process_queue)
        self.cancelled = False
        self.cancel.connect(self.cancel_process)

    def add_to_queue(self, upload_task: dict[str, UploadTask | QThread]):
        self.upload_queue.append(upload_task)
        upload_task["task"].finished.connect(lambda: self.remove_from_queue(upload_task))

    def remove_from_queue(self, upload_task: dict[str, UploadTask | QThread]):
        if upload_task in self.upload_queue:
            self.upload_queue.remove(upload_task)
            upload_task["thread"].quit()

    def process_queue(self):
        for upload_task in self.upload_queue:
            if self.cancelled:
                break
            if not upload_task["task"].started:
                upload_task["task"].start.emit()
    def cancel_process(self):
        self.cancelled = True

    def cleanup(self):
        for upload_task in self.upload_queue:
            upload_task["task"].cancel()
        time.sleep(0.1)
        for upload_task in self.upload_queue:
            upload_task["thread"].quit()


