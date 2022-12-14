""" Widget: setup tab inside the configuration dialog window """
import webbrowser, logging
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QMessageBox, QInputDialog, QFileDialog, QProgressBar   # pylint: disable=no-name-in-module
import qtawesome as qta

from .installationTools import git, gitAnnex, couchdb, couchdbUserPassword, configuration, ontology, exampleData, createShortcut
from .fixedStrings import setupTextWindows, gitWindows, gitAnnexWindows, couchDBWindows, exampleDataWindows, restartPastaWindows

class ConfigurationSetup(QWidget):
  """
  Main class
  """
  def __init__(self, backend, callbackFinished):
    super().__init__()
    self.mainL = QVBoxLayout()
    self.setMinimumWidth(400)
    self.setMinimumHeight(500)
    self.setLayout(self.mainL)
    self.callbackFinished = callbackFinished
    self.backend = backend

    #widget 1 = screen 1
    self.screen1W = QWidget()
    self.mainL.addWidget(self.screen1W)
    screen1L = QVBoxLayout(self.screen1W)
    self.text1 = QTextEdit()
    self.mainText = setupTextWindows
    self.text1.setMarkdown(self.mainText)
    screen1L.addWidget(self.text1)
    self.progress1 = QProgressBar(self.screen1W)
    self.progress1.setMaximum(24)
    self.progress1.hide()
    screen1L.addWidget(self.progress1)

    footerW = QWidget()
    screen1L.addWidget(footerW)
    footerL = QHBoxLayout(footerW)
    self.button1 = QPushButton('Start analyse and repair')
    self.button1.clicked.connect(self.analyse)
    footerL.addWidget(self.button1)


  def callbackProgress(self, number):
    """
    Increse progressbar by moving to number

    Args:
      number (int): integer to move to
    """
    self.progress1.setValue(number)
    return


  def analyse(self):
    """
    Main method that does all the analysis: open dialogs, ...
    """
    flagContinue = True
    flagInstalledSoftware = False
    logging.info('Windows setup analyse start')

    #Git
    res = git('test')
    if res =='':
      self.mainText = self.mainText.replace('- Git Windows','- Git Windows is installed' )
      self.text1.setMarkdown(self.mainText)
    else:
      button = QMessageBox.question(self, "Git installation", gitWindows)
      if button == QMessageBox.Yes:
        git('install')
        flagInstalledSoftware = True
      else:
        self.mainText = self.mainText.replace('- Git Windows','- Git Windows: user chose to NOT install' )
        self.text1.setMarkdown(self.mainText)
        flagContinue = False


    #Git annex
    password = ''
    if flagContinue:
      res = gitAnnex('test')
      if res =='':
        self.mainText = self.mainText.replace('- Git-Annex','- Git-Annex is installed' )
        self.text1.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, "Git-Annex installation", gitAnnexWindows)
        if button == QMessageBox.Yes:
          gitAnnex('install')
          flagInstalledSoftware = True
        else:
          self.mainText = self.mainText.replace('- Git-Annex','- Git-Annex: user chose to NOT install' )
          self.text1.setMarkdown(self.mainText)
          flagContinue = False

    #Couchdb
    if flagContinue:
      res = couchdb('test')
      if res =='':
        self.mainText = self.mainText.replace('- CouchDB','- CouchDB is installed' )
        self.text1.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, "CouchDB installation", couchDBWindows)
        if button == QMessageBox.Yes:
          res = couchdb('install')
          flagInstalledSoftware = True
          if len(res.split('|'))==3:
            password=res.split('|')[1]
          else:
            logging.error('Could not retrieve password :'+str(res))
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
          configuration('repair','admin', password,dirName)
          flagInstalledSoftware = True
        else:
          self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration: user chose to NOT install' )
          self.text1.setMarkdown(self.mainText)
          flagContinue = False

    #Ontology
    if flagContinue:
      res = ontology('test')
      if '**ERROR' not in res:
        self.mainText = self.mainText.replace('- Ontology of the datastructure','- Ontology of the datastructure is acceptable\n'+res )
        self.text1.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, "PASTA-ELN ontology", "Do you want to create the default ontology?")
        if button == QMessageBox.Yes:
          ontology('install')
        else:
          self.mainText = self.mainText.replace('- Ontology of the datastructure','- Ontology: user chose to NOT install' )
          self.text1.setMarkdown(self.mainText)
          flagContinue = False

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
      button = QMessageBox.information(self,'PASTA-ELN restart required', restartPastaWindows)
      #TODO execute restart here via comm to gui.py

    #Example data
    if flagContinue:
      button = QMessageBox.question(self, "Example data", exampleDataWindows)
      if button == QMessageBox.Yes:
        self.progress1.show()
        if (self.backend.basePath/'pastasExampleProject').exists():
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
      self.text1.setMarkdown(self.mainText)

    #at end
    self.button1.setText('Finished')
    self.button1.clicked.disconnect(self.analyse)
    self.button1.clicked.connect(self.finished)
    logging.info('Windows setup analyse end')
    return


  def finished(self):
    """
    What do do when setup is finished: success or unsuccessfully
    """
    self.callbackFinished()
