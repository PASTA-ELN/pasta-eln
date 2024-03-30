""" Widget: setup tab inside the configuration dialog window """
import logging, os, ctypes
from enum import Enum
from pathlib import Path
from typing import Callable, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMessageBox, QFileDialog, QProgressBar   # pylint: disable=no-name-in-module
from ..guiStyle import TextButton, widgetAndLayout
from ..installationTools import couchdb, configuration, dataHierarchy, exampleData, createShortcut
from ..fixedStringsJson import setupTextWindows, couchDBWindows, exampleDataWindows, restartPastaWindows
from ..miscTools import restart
from ..guiCommunicate import Communicate

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
    self.mainL = QVBoxLayout()
    self.setMinimumWidth(400)
    self.setMinimumHeight(500)
    self.setLayout(self.mainL)
    self.callbackFinished = callbackFinished
    self.comm = comm

    #widget 1 = screen 1
    self.screen1W, screen1L = widgetAndLayout('V', self.mainL)
    self.text1 = QTextEdit()
    self.mainText = setupTextWindows
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
      flagContinue = True
      flagInstalledSoftware = False
      logging.info('Windows setup analyse start')

      #Couchdb
      if flagContinue:
        res = couchdb('test')
        if res =='':
          self.mainText = self.mainText.replace('- CouchDB','- CouchDB is installed' )
          self.text1.setMarkdown(self.mainText)
        else:
          button = QMessageBox.question(self, "CouchDB installation", couchDBWindows)
          if button == QMessageBox.Yes:
            try:
              isAdmin = os.getuid() == 0
            except AttributeError:
              isAdmin = ctypes.windll.shell32.IsUserAnAdmin() == 1 # type: ignore[attr-defined]
            if not isAdmin:
              QMessageBox.information(self,'Administrator rights required', \
                          'You require administrator rights for your user. I exit installation now.')
              self.mainText = self.mainText.replace('- CouchDB','- CouchDB: no admin rights' )
              self.text1.setMarkdown(self.mainText)
              flagContinue = False
            else:
              res = couchdb('install')
              flagInstalledSoftware = True
              if len(res.split('|'))==3:
                password=res.split('|')[1]
              else:
                logging.error('Could not retrieve password :%s',str(res))
          else:
            self.mainText = self.mainText.replace('- CouchDB','- CouchDB: user chose to NOT install' )
            self.text1.setMarkdown(self.mainText)
            flagContinue = False

      #Configuration
      if flagContinue:
        res = configuration('test')
        if res =='':
          self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration of preferences is acceptable' )
          self.text1.setMarkdown(self.mainText)
        else:
          button = QMessageBox.question(self, "PASTA-ELN configuration", "Do you want to create/repain the configuration.")
          if button == QMessageBox.Yes:
            dirName = QFileDialog.getExistingDirectory(self,'Create and select directory for scientific data',str(Path.home()/'Documents'))
            configuration('repair','admin', password, Path(dirName))
            flagInstalledSoftware = True
          else:
            self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration: user chose to NOT install' )
            self.text1.setMarkdown(self.mainText)
            flagContinue = False

      #DataHierarchy
      if flagContinue:
        res = dataHierarchy('test')
        if '**ERROR' not in res:
          self.mainText = self.mainText.replace('- DataHierarchy of the datastructure','- DataHierarchy of the datastructure is acceptable\n'+res )
          self.text1.setMarkdown(self.mainText)
        else:
          # button = QMessageBox.question(self, "PASTA-ELN dataHierarchy", "Do you want to create the default dataHierarchy?")
          # if button == QMessageBox.Yes:
          dataHierarchy('install')
          # else:
          #   self.mainText = self.mainText.replace('- DataHierarchy of the datastructure','- DataHierarchy: user chose to NOT install' )
          #   self.text1.setMarkdown(self.mainText)
          #   flagContinue = False

      #Shortcut
      if flagContinue:
        button = QMessageBox.question(self, "Create shortcut", "Do you want to create the shortcut for PASTA-ELN on desktop?")
        if button == QMessageBox.Yes:
          createShortcut()
          self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to add a shortcut' )
        else:
          self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to NOT add a shortcut' )
        self.text1.setMarkdown(self.mainText)

      #If installed, restart
      if flagInstalledSoftware:
        QMessageBox.information(self,'PASTA-ELN restart required', restartPastaWindows)
        restart()

      #Example data
      if flagContinue:
        button = QMessageBox.question(self, "Example data", exampleDataWindows)
        if button == QMessageBox.Yes:
          self.progress1.show()
          if (self.comm.backend.basePath/'pastasExampleProject').exists():
            button1 = QMessageBox.question(self, "Example data", 'Data exists. Should I reset?')
            if button1 == QMessageBox.Yes:
              exampleData(True, self.callbackProgress)
            else:
              self.mainText = self.mainText.replace('- Example data', '- Example data exists and should not be deleted.')
          else:
            exampleData(False, self.callbackProgress)
            self.mainText = self.mainText.replace('- Example data', '- Example data was added')
        else:
          self.mainText = self.mainText.replace('- Example data', '- Example data was NOT added, per user choice')
          flagContinue = False
        self.text1.setMarkdown(self.mainText)

      #at end
      self.button1.hide()
      self.button2.show()
      logging.info('Windows setup analyse end')
    elif command[0] is Command.FINISHED: # What do do when setup is finished: success or unsuccessfully
      restart()
      # self.callbackFinished()
    return




class Command(Enum):
  """ Commands used in this file """
  ANALYSE   = 1
  FINISHED  = 2
