#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: upload_manager.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6.QtCore import QObject, QThread, Signal

from pasta_eln.dataverse.upload_task import UploadTask


class UploadManager(QObject):
    start = Signal()
    def __init__(self):
        super().__init__()
        self.upload_queue: list[dict[str, UploadTask | QThread]] = []
        self.start.connect(self.process_queue)

    def add_to_queue(self, upload_task: dict[str, UploadTask | QThread]):
        self.upload_queue.append(upload_task)

    def remove_from_queue(self, upload_task: dict[str, UploadTask | QThread]):
        self.upload_queue.remove(upload_task)

    def process_queue(self):
        for upload_task in self.upload_queue:
            upload_task["task"].start.emit()

