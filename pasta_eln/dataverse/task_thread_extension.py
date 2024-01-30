#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2024
#
#  Author: Jithu Murugan
#  Filename: task_thread_extension.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from PySide6.QtCore import QObject, QThread

from pasta_eln.dataverse.generic_task_object import GenericTaskObject


class TaskThreadExtension(QObject):

  def __init__(self, task: GenericTaskObject):
    super().__init__()
    self.task = task
    self.thread = QThread()
    self.task.moveToThread(self.thread)
    self.thread.start()

  def quit(self):
    self.task.cancel.emit()
    self.task.cleanup()
    self.thread.quit()
