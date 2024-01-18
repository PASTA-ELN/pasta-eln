#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: task_thread_general.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
from PySide6.QtCore import QObject, QThread


class TaskThread:

    def __init__(self, task: QObject):
        self.task = task
        self.thread = QThread()
        self.task.moveToThread(self.thread)
        self.thread.start()

    def quit(self):
        self.task.cancel_process()
        self.thread.quit()


