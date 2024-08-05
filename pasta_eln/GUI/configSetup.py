""" Widget: setup tab inside the configuration dialog window """
import logging
from enum import Enum
from pathlib import Path
from typing import Callable, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMessageBox, QProgressBar, QFileDialog  # pylint: disable=no-name-in-module
from ..guiStyle import TextButton, widgetAndLayout
from ..installationTools import configuration, exampleData, createShortcut
from ..fixedStringsJson import setupText, exampleDataString
from ..miscTools import restart
from ..guiCommunicate import Communicate
# from ..dataverse.database_api import DatabaseAPI

class ConfigurationSetup(QWidget):
  """
  Main class
  """
  def __init__(self, comm:Communicate, callbackFinished:Callable[[],None]):
    """
    Initialization

    Args:
      comm (Communicate): communication
      callbackFinished (function): callback function to call upon end
    """
    super().__init__()
    self.comm = comm

    #GUI elements
    self.mainL = QVBoxLayout()
    self.setMinimumWidth(400)
    self.setMinimumHeight(500)
    self.setLayout(self.mainL)
    self.callbackFinished = callbackFinished

    #widget 1 = screen 1
    self.screen1W, screen1L = widgetAndLayout('V', self.mainL)
    self.text1 = QTextEdit()
    self.mainText = setupText
    self.text1.setMarkdown(self.mainText)
    screen1L.addWidget(self.text1)
    self.progress1 = QProgressBar(self.screen1W)
    self.progress1.setMaximum(24)
    self.progress1.hide()
    screen1L.addWidget(self.progress1)

    _, footerL = widgetAndLayout('H', screen1L, 's')
    self.button1 = TextButton('Start analyse and repair', self, [Command.ANALYSE], footerL)
    self.button2 = TextButton('Finished',                 self, [Command.FINISHED], footerL)
    self.button2.hide()


  def callbackProgress(self, number:int) -> None:
    """
    Increase progressbar by moving to number

    Args:
      number (int): integer to move to
    """
    self.progress1.setValue(number)
    return


  def execute(self, command:list[Any]) -> None:
    """
    Main method that does all the analysis: open dialogs, ...
    """
    if command[0] is Command.ANALYSE:
      #Configuration
      res = configuration('test', '')
      if res =='':
        self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration of preferences is acceptable' )
        self.text1.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, "PASTA-ELN configuration", "Do you want to create/repair the configuration.")
        if button == QMessageBox.StandardButton.Yes:
          dirName = QFileDialog.getExistingDirectory(self,'Create and select directory for scientific data',str(Path.home()))
          if dirName is None:
            self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration: user chose to INVALID folder' )
            self.text1.setMarkdown(self.mainText)
          else:
            configuration('repair', dirName)
        else:
          self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration: user chose to NOT install' )
          self.text1.setMarkdown(self.mainText)
      #Shortcut
      button = QMessageBox.question(self, "Create shortcut", "Do you want to create the shortcut for PASTA-ELN on desktop?")
      if button == QMessageBox.StandardButton.Yes:
        createShortcut()
        self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to add a shortcut' )
      else:
        self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to NOT add a shortcut' )
      self.text1.setMarkdown(self.mainText)
      #Example data
      button = QMessageBox.question(self, "Example data", exampleDataString)
      if button == QMessageBox.StandardButton.Yes:
        self.progress1.show()
        exampleData(True, self.callbackProgress)
        self.mainText = self.mainText.replace('- Example data', '- Example data was added')
      else:
        self.mainText = self.mainText.replace('- Example data', '- Example data was NOT added, per user choice')
      self.text1.setMarkdown(self.mainText)
      #at end
      self.button1.hide()
      self.button2.show()
      logging.info('Setup analyse end')
    elif command[0] is Command.FINISHED: # What do do when setup is finished: success or unsuccessfully
      # Jithu's code: comment out for now
      # db_api = DatabaseAPI()
      # db_api.initialize_database()
      restart()
      # self.callbackFinished()
    return


class Command(Enum):
  """ Commands used in this file """
  ANALYSE   = 1
  FINISHED  = 2
