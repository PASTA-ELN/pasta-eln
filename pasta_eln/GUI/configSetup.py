""" Widget: setup tab inside the configuration dialog window """
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Callable
from PySide6.QtWidgets import (QFileDialog, QMessageBox, QProgressBar, QTextEdit,  # pylint: disable=no-name-in-module
                               QVBoxLayout, QWidget)
from ..fixedStringsJson import exampleDataString, setupText
from ..guiCommunicate import Communicate
from ..guiStyle import TextButton, widgetAndLayout
from ..installationTools import configuration, createShortcut, exampleData
from ..miscTools import restart

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

    self.text = QTextEdit()
    self.mainText = setupText
    self.text.setMarkdown(self.mainText)
    self.mainL.addWidget(self.text)
    self.progressBar = QProgressBar(self)
    self.progressBar.setMaximum(24)
    self.progressBar.hide()
    self.mainL.addWidget(self.progressBar)

    _, footerL = widgetAndLayout('H', self.mainL, 's', top='m', left='xl', right='xl')
    style = 'color: orange; font-weight: 550; font-size: 20px'
    self.button1 = TextButton('Click to install / repair', self, [Command.ANALYSE], footerL, style=style)
    self.button2 = TextButton('Click to finish',           self, [Command.FINISHED], footerL, style=style, hide=True)


  def callbackProgress(self, number:int) -> None:
    """
    Increase progressbar by moving to number

    Args:
      number (int): integer to move to
    """
    self.progressBar.setValue(number)
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
        self.text.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, 'PASTA-ELN configuration', 'Do you want to create/repair the configuration.',
                                      QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if button == QMessageBox.StandardButton.Yes:
          dirName = QFileDialog.getExistingDirectory(self,'Create and select directory for scientific data',str(Path.home()))
          if dirName is None:
            self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration: user chose to INVALID folder' )
            self.text.setMarkdown(self.mainText)
          else:
            configuration('repair', dirName)
        else:
          self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration: user chose to NOT install' )
          self.text.setMarkdown(self.mainText)
      #Shortcut
      button = QMessageBox.question(self, 'Create shortcut', 'Do you want to create the shortcut for PASTA-ELN on desktop?',
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.Yes:
        createShortcut()
        self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to add a shortcut' )
      else:
        self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to NOT add a shortcut' )
      self.text.setMarkdown(self.mainText)
      #Example data
      button = QMessageBox.question(self, 'Example data', exampleDataString,
                                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
      if button == QMessageBox.StandardButton.Yes:
        self.progressBar.show()
        exampleData(True, self.callbackProgress)
        self.mainText = self.mainText.replace('- Example data', '- Example data was added')
      else:
        self.mainText = self.mainText.replace('- Example data', '- Example data was NOT added, per user choice')
      self.text.setMarkdown(self.mainText)
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
