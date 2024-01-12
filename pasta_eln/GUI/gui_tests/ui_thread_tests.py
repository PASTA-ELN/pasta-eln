#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: ui_thread_tests.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
import time
from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QDialog

from pasta_eln.GUI.gui_tests.ui_thread_tests_base import Ui_UIThreadTestsDialog
from pasta_eln.GUI.gui_tests.upload_worker import UploadWorker


class UIThreadTests(Ui_UIThreadTestsDialog):

  def __new__(cls, *_: Any, **__: Any) -> Any:
    return super(UIThreadTests, cls).__new__(cls)

  def __init__(self):
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.instance = QDialog()
    super().setupUi(self.instance)
    self.clickPushButton.clicked.connect(self.update_clicks)
    self.clicks = 0
    self.worker_threads = []
    self.workers = []
    self.create_update_thread(self.progressPushButton1, self.progressBar1, self.label1)
    self.create_update_thread(self.progressPushButton2, self.progressBar2, self.label2)
    self.create_update_thread(self.progressPushButton3, self.progressBar3, self.label3)
    self.create_update_thread(self.progressPushButton4, self.progressBar4, self.label4)
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(lambda: self.finalize_threads())
    self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(lambda: self.finalize_threads())
    self.cancelPushButton.clicked.connect(lambda: [i.cancel() for i in self.workers])

  def create_update_thread(self,
                           progressBarPushButton: QtWidgets.QPushButton,
                           progressBar: QtWidgets.QProgressBar,
                           label: QtWidgets.QLabel):
    thread = QThread()
    thread.start()
    worker = UploadWorker()
    worker.moveToThread(thread)
    worker.progressChanged.connect(progressBar.setValue)
    worker.statusChanged.connect(label.setText)
    # self.worker.finished.connect(self.thread.quit)
    # self.worker.finished.connect(self.worker.deleteLater)
    progressBarPushButton.clicked.connect(worker.work)
    self.worker_threads.append(thread)
    self.workers.append(worker)


  def update_clicks(self):
    self.clicks += 1
    self.clickLabel.setText(f"Clicks: {self.clicks}")

  def finalize_threads(self):
    [i.cancel() for i in self.workers]
    time.sleep(0.1)
    [i.quit() for i in self.worker_threads]


if __name__ == "__main__":
  import sys

  app = QtWidgets.QApplication(sys.argv)

  ui = UIThreadTests()
  ui.instance.show()
  sys.exit(app.exec())
        
    
