""" Widget: setup tab inside the configuration dialog window """
import webbrowser, logging
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QMessageBox, QInputDialog, QFileDialog, QProgressBar    # pylint: disable=no-name-in-module
import qtawesome as qta

from .installationTools import gitAnnex, couchdb, configuration, ontology, exampleData, createShortcut, installLinuxRoot
from .fixedStrings import setupTextLinux, rootInstallLinux, exampleDataLinux

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

    #widget 1 = screen 1
    self.screen1W = QWidget()
    self.mainL.addWidget(self.screen1W)
    screen1L = QVBoxLayout(self.screen1W)
    self.text1 = QTextEdit()
    self.mainText = setupTextLinux
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
    logging.info('Linux setup analyse start')

    #Git annex
    res = gitAnnex('test')
    existsGitAnnex = None
    if res =='':
      self.mainText = self.mainText.replace('- Git-Annex','- Git-Annex is installed' )
      self.text1.setMarkdown(self.mainText)
      existsGitAnnex = True
    else:
      existsGitAnnex = False

    #Couchdb
    existsCouchDB = None
    if flagContinue:
      res = couchdb('test')
      if res =='':
        self.mainText = self.mainText.replace('- CouchDB','- CouchDB is installed' )
        self.text1.setMarkdown(self.mainText)
        existsCouchDB = True
      else:
        existsCouchDB = False

    #Install git-annex und couchdb
    if (not existsGitAnnex) or (not existsCouchDB):
      textGitAnnex = '' if existsGitAnnex else 'git-annex'
      textCouchDB  = '' if existsCouchDB else 'couch-DB'
      separator    = '' if existsGitAnnex or existsCouchDB else ', '
      text = rootInstallLinux.replace('XX--XX', textGitAnnex+separator+textCouchDB)
      button = QMessageBox.question(self, "Root installations", text)
      if button == QMessageBox.Yes:
        dirName = QFileDialog.getExistingDirectory(self,'Create and select directory for scientific data',str(Path.home()))
        installLinuxRoot(existsGitAnnex, existsCouchDB, dirName)
      else:
        self.mainText = self.mainText.replace('- Git-Annex','- Git-Annex: user chose to NOT install' )
        self.mainText = self.mainText.replace('- CouchDB','- CouchDB: user chose to NOT install' )
        self.text1.setMarkdown(self.mainText)

    #Configuration
    if flagContinue:
      res = configuration('test')
      if res =='':
        self.mainText = self.mainText.replace('- Configuration of preferences','- Configuration of preferences is acceptable' )
        self.text1.setMarkdown(self.mainText)
      else:
        button = QMessageBox.question(self, "PASTA-ELN configuration", "Do you want to create/repain the configuration.")
        if button == QMessageBox.Yes:
          configuration('repair')
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

    ## Ubuntu autocreates the shortcut: if true in May2023: remove
    # #Shortcut
    # if flagContinue:
    #   button = QMessageBox.question(self, "Create shortcut", "Do you want to create the shortcut for PASTA-ELN on desktop?")
    #   if button == QMessageBox.Yes:
    #     createShortcut()
    #     self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to add a shortcut' )
    #   else:
    #     self.mainText = self.mainText.replace('- Shortcut creation', '- User selected to NOT add a shortcut' )
    #   self.text1.setMarkdown(self.mainText)

    #Example data
    if flagContinue:
      button = QMessageBox.question(self, "Example data", exampleDataLinux)
      if button == QMessageBox.Yes:
        self.progress1.show()
        exampleData(False, self.callbackProgress)
        self.mainText = self.mainText.replace('- Example data', '- Example data was added')
      else:
        self.mainText = self.mainText.replace('- Example data', '- Example data was NOT added, per user choice')
      self.text1.setMarkdown(self.mainText)

    #at end
    self.button1.setText('Finished')
    self.button1.clicked.disconnect(self.analyse)
    self.button1.clicked.connect(self.finished)
    logging.info('Linux setup analyse end')
    return


  def finished(self):
    """
    What do do when setup is finished: success or unsuccessfully
    """
    self.callbackFinished()
